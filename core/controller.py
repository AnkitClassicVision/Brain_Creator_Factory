"""Controller - The deterministic execution controller for brain workflows."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .brain import Brain, BrainManifest, StopRule, ValidationRule, MinimumEnforcement
from .graph import (
    Graph, Node, Edge, NodeType, EdgeType, Stage,
    DecisionConfig, DependencyConfig, DecompositionConfig
)
from .state import State, AuditEvent
from .memory import MemoryStore, MemoryQuery, Fact, Provenance
from .context import build_eval_env


class RunOutcome(str, Enum):
    """Possible outcomes of a brain run."""
    SUCCESS = "success"
    FAILURE = "failure"
    ESCALATED = "escalated"
    MAX_STEPS = "max_steps"
    ERROR = "error"


@dataclass
class NodeResult:
    """Result of executing a single node."""
    success: bool
    output: Dict[str, Any] = field(default_factory=dict)
    state_patch: Dict[str, Any] = field(default_factory=dict)
    parallel_tasks: List[Dict[str, Any]] = field(default_factory=list)
    memory_writes: List[Fact] = field(default_factory=list)
    signals: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class RunResult:
    """Complete result of a brain run."""
    run_id: str
    outcome: RunOutcome
    final_node: str
    total_steps: int
    started_at: datetime
    ended_at: datetime
    final_state: Dict[str, Any]
    deliverables: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class LLMClient(Protocol):
    """Protocol for LLM client implementations."""

    def complete(
        self,
        prompt: str,
        output_schema: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a completion from the LLM."""
        ...


class SkillExecutor(Protocol):
    """Protocol for skill execution."""

    def execute(
        self,
        skill_name: str,
        instruction: str,
        context: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Execute a skill and return results."""
        ...


class BrainController:
    """
    The deterministic controller that orchestrates brain execution.

    Key principles:
    - State lives OUTSIDE the LLM (in State object)
    - LLM is a probabilistic subroutine, not an agent
    - Routing is deterministic via guard expressions
    - All actions are auditable
    """

    def __init__(
        self,
        brain: Brain,
        llm_client: LLMClient,
        skill_executor: Optional[SkillExecutor] = None,
        run_dir: Optional[Path] = None,
    ):
        self.brain = brain.load()
        self.manifest = brain.manifest
        self.graph = Graph.load(brain.graph_path)
        self.memory = MemoryStore(brain.memory_path)
        self.llm_client = llm_client
        self.skill_executor = skill_executor

        # Run directory for this execution
        self.run_dir = run_dir or brain.runs_path / datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.run_dir.mkdir(parents=True, exist_ok=True)

        # Paths for this run
        self.audit_path = self.run_dir / "audit.jsonl"
        self.state_path = self.run_dir / "final_state.json"

    def run(
        self,
        user_request: str,
        run_id: Optional[str] = None,
        initial_data: Optional[Dict[str, Any]] = None,
    ) -> RunResult:
        """Execute the brain with the given user request."""

        run_id = run_id or str(uuid.uuid4())

        # Initialize state
        state = State(
            brain_id=self.manifest.id,
            run_id=run_id,
            user_request=user_request,
        )
        state.brain = self.manifest.to_dict()
        state.current_node = self.graph.start_node
        state.stage = Stage.INTAKE

        if initial_data:
            state.data.update(initial_data)

        # Validate graph before running
        errors = self.graph.validate()
        if errors:
            return RunResult(
                run_id=run_id,
                outcome=RunOutcome.ERROR,
                final_node=state.current_node or "",
                total_steps=0,
                started_at=state.started_at,
                ended_at=datetime.utcnow(),
                final_state=state.to_dict(),
                error=f"Graph validation failed: {errors}",
            )

        # Main execution loop
        max_steps = self.manifest.execution.max_steps

        while state.counters.total_steps < max_steps:
            current_node_id = state.current_node

            # Check if we've reached a terminal node
            if current_node_id in self.graph.terminal_nodes:
                # Check for completion signal
                if state.get("done", False):
                    outcome = self._determine_terminal_outcome(current_node_id)
                    break
                # Terminal node but not done - execute it once more
                if state.counters.node_visits.get(current_node_id, 0) > 0:
                    outcome = self._determine_terminal_outcome(current_node_id)
                    break

            # Get current node
            node = self.graph.nodes.get(current_node_id)
            if not node:
                state.add_audit(
                    node_id=current_node_id,
                    action="error",
                    summary=f"Node not found: {current_node_id}",
                )
                outcome = RunOutcome.ERROR
                break

            # Visit node
            state.counters.visit_node(current_node_id)
            state.stage = node.stage

            # Execute node
            try:
                result = self._execute_node(node, state)
            except Exception as e:
                state.add_audit(
                    node_id=current_node_id,
                    action="error",
                    summary=f"Node execution error: {str(e)}",
                )
                state.signals.record_failure(current_node_id, str(e))
                outcome = RunOutcome.ERROR
                break

            # Apply state updates
            if result.state_patch:
                state.apply_patch(result.state_patch)

            # Handle parallel tasks
            if result.parallel_tasks:
                self._handle_parallel_tasks(result.parallel_tasks, state)

            # Handle memory writes
            if result.memory_writes:
                self._handle_memory_writes(result.memory_writes, state, node)

            # Record audit
            state.add_audit(
                node_id=current_node_id,
                action=f"executed_{node.type.value}",
                summary=result.signals.get("summary", f"{node.type.value} completed"),
                signals=result.signals,
            )

            # Choose next edge
            next_node_id = self._choose_next_edge(node, state)

            if next_node_id is None:
                state.add_audit(
                    node_id=current_node_id,
                    action="no_valid_edge",
                    summary="No valid outgoing edge found",
                )
                state.signals.record_failure(current_node_id, "No valid outgoing edge")
                outcome = RunOutcome.FAILURE
                break

            state.current_node = next_node_id

            # Flush audit periodically
            if state.counters.total_steps % 10 == 0:
                state.save_audit(self.audit_path)

        else:
            # Max steps exceeded
            outcome = RunOutcome.MAX_STEPS
            state.signals.record_failure(
                state.current_node or "unknown",
                "Max steps exceeded"
            )

        # Finalize
        state.ended_at = datetime.utcnow()
        state.save_audit(self.audit_path)
        state.save(self.state_path)

        # Save updated graph (for edge statistics)
        self.graph.save(self.brain.graph_path)

        return RunResult(
            run_id=run_id,
            outcome=outcome,
            final_node=state.current_node or "",
            total_steps=state.counters.total_steps,
            started_at=state.started_at,
            ended_at=state.ended_at,
            final_state=state.to_dict(),
            deliverables=state.get("deliverables", {}),
        )

    def _execute_node(self, node: Node, state: State) -> NodeResult:
        """Execute a single node based on its type."""

        if node.type == NodeType.PRIME:
            return self._execute_prime(node, state)
        elif node.type == NodeType.FLOW:
            return self._execute_flow(node, state)
        elif node.type == NodeType.TRIBUTARY:
            return self._execute_tributary(node, state)
        elif node.type == NodeType.DELTA:
            return self._execute_delta(node, state)
        elif node.type == NodeType.SEDIMENT:
            return self._execute_sediment(node, state)
        elif node.type == NodeType.GATE:
            return self._execute_gate(node, state)
        elif node.type == NodeType.DECISION:
            return self._execute_decision(node, state)
        elif node.type == NodeType.TERMINAL:
            return self._execute_terminal(node, state)
        else:
            return NodeResult(success=False, error=f"Unknown node type: {node.type}")

    def _execute_prime(self, node: Node, state: State) -> NodeResult:
        """Execute a PRIME node (initialization)."""
        # Dredge memory if configured
        dredged = self._dredge_memory(node, state)

        # Build prompt
        prompt = self._render_prompt(node, state, dredged)

        # Call LLM
        output_schema = self._build_output_schema(node)
        llm_output = self.llm_client.complete(prompt, output_schema)

        # Extract state patch
        state_patch = self._extract_state_patch(node, llm_output)

        return NodeResult(
            success=True,
            output=llm_output,
            state_patch=state_patch,
            signals={"summary": "Initialized riverbed schema", "confidence": llm_output.get("confidence", 1.0)},
        )

    def _execute_flow(self, node: Node, state: State) -> NodeResult:
        """Execute a FLOW node (main reasoning)."""
        # Dredge memory
        dredged = self._dredge_memory(node, state)

        # Build prompt
        prompt = self._render_prompt(node, state, dredged)

        # Call LLM
        output_schema = self._build_output_schema(node)
        llm_output = self.llm_client.complete(prompt, output_schema)

        # Extract state patch
        state_patch = self._extract_state_patch(node, llm_output)

        # Extract parallel tasks
        parallel_tasks = llm_output.get("parallel_tasks", [])

        # Extract memory writes
        memory_writes = []
        if node.memory.write and "facts" in llm_output:
            for fact_data in llm_output["facts"]:
                memory_writes.append(Fact.from_dict(fact_data))

        return NodeResult(
            success=True,
            output=llm_output,
            state_patch=state_patch,
            parallel_tasks=parallel_tasks,
            memory_writes=memory_writes,
            signals={
                "summary": "FLOW step completed",
                "confidence": llm_output.get("confidence", 0.8),
            },
        )

    def _execute_tributary(self, node: Node, state: State) -> NodeResult:
        """Execute a TRIBUTARY node (tool/skill execution)."""
        if not self.skill_executor:
            return NodeResult(
                success=False,
                error="No skill executor configured",
            )

        if not node.skill_name:
            return NodeResult(
                success=False,
                error="Tributary node missing skill_name",
            )

        # Execute skill
        try:
            result = self.skill_executor.execute(
                skill_name=node.skill_name,
                instruction=node.prompt,
                context=state.to_context(),
                **node.skill_config,
            )

            state.counters.skills_invoked += 1

            # Extract facts if present
            memory_writes = []
            if "facts" in result:
                for fact_data in result["facts"]:
                    memory_writes.append(Fact.from_dict(fact_data))

            return NodeResult(
                success=True,
                output=result,
                state_patch=result.get("state_patch", {}),
                memory_writes=memory_writes,
                signals={"summary": f"Skill {node.skill_name} executed"},
            )

        except Exception as e:
            return NodeResult(
                success=False,
                error=str(e),
                signals={"summary": f"Skill {node.skill_name} failed: {e}"},
            )

    def _execute_delta(self, node: Node, state: State) -> NodeResult:
        """Execute a DELTA node (merge parallel results)."""
        # Get completed parallel task results
        completed = state.parallel.completed_tasks
        failed = state.parallel.failed_tasks

        # Merge results
        merged_results = []
        for task in completed:
            if task.result:
                merged_results.append({
                    "task_id": task.task_id,
                    "skill": task.skill,
                    "result": task.result,
                })

        state_patch = {
            "merged_results": merged_results,
            "parallel_complete": True,
            "parallel_success_count": len(completed),
            "parallel_failure_count": len(failed),
        }

        return NodeResult(
            success=True,
            output={"merged": merged_results},
            state_patch=state_patch,
            signals={"summary": f"Merged {len(completed)} parallel results"},
        )

    def _execute_sediment(self, node: Node, state: State) -> NodeResult:
        """Execute a SEDIMENT node (memory write)."""
        # Get facts to write
        facts_path = node.memory.source or "pending_facts"
        facts_data = state.get(facts_path, [])

        facts = []
        for fd in facts_data:
            if isinstance(fd, Fact):
                facts.append(fd)
            elif isinstance(fd, dict):
                facts.append(Fact.from_dict(fd))

        if not facts:
            return NodeResult(
                success=True,
                state_patch={"sediment_written": 0},
                signals={"summary": "No facts to write"},
            )

        # Write to memory
        written, conflicts = self.memory.write(
            facts=facts,
            run_id=state.run_id,
            node_id=node.id,
            check_conflicts=node.memory.require_triplets,
        )

        state.counters.memory_writes += len(written)

        state_patch = {
            "sediment_written": len(written),
            "sediment_conflicts": conflicts,
        }

        # Handle conflicts based on configuration
        if conflicts and node.memory.conflict_action == "flag":
            state_patch["memory_conflicts"] = conflicts
            state.signals.record_observation(
                "Memory conflict detected",
                {"conflicts": conflicts}
            )

        return NodeResult(
            success=True,
            state_patch=state_patch,
            signals={"summary": f"SEDIMENT wrote {len(written)} facts"},
        )

    def _execute_gate(self, node: Node, state: State) -> NodeResult:
        """Execute a GATE node (quality check)."""
        if not node.gate:
            return NodeResult(success=False, error="Gate node missing gate_config")

        allowed_builtins = {
            "len": len,
            "any": any,
            "all": all,
            "min": min,
            "max": max,
            "sum": sum,
            "abs": abs,
            "round": round,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "True": True,
            "False": False,
            "None": None,
        }

        # Evaluate each criterion
        passed = True
        results = []

        for criterion in node.gate.criteria:
            name = criterion.get("name", "unnamed")
            check = criterion.get("check", "True")

            # Evaluate the check expression
            try:
                env = build_eval_env(state.to_context())
                result = eval(check, {"__builtins__": allowed_builtins}, env)
                results.append({"name": name, "passed": bool(result)})
                if not result:
                    passed = False
            except Exception as e:
                results.append({"name": name, "passed": False, "error": str(e)})
                passed = False

        state_patch = {
            "verification_passed": passed,
            "gate_results": results,
            "gates": {
                node.id: {
                    "passed": passed,
                    "results": results,
                }
            },
        }

        # Record learning signal
        if not passed:
            state.signals.record_failure(
                node.id,
                "Gate check failed",
                {"results": results}
            )

        return NodeResult(
            success=True,
            state_patch=state_patch,
            signals={
                "summary": f"Gate {'passed' if passed else 'failed'}",
                "passed": passed,
            },
        )

    def _execute_decision(self, node: Node, state: State) -> NodeResult:
        """Execute a DECISION node (pure routing logic).

        DECISION nodes are Router Nodes that NEVER generate text.
        They evaluate data against rules to choose the next path deterministically.
        This removes "vibe-based" LLM routing decisions.
        """
        if not node.decision:
            return NodeResult(success=False, error="Decision node missing decision_config")

        config = node.decision
        env = build_eval_env(state.to_context())

        # Check precondition if specified
        if config.precondition:
            try:
                allowed_builtins = {
                    "len": len, "any": any, "all": all,
                    "min": min, "max": max, "str": str, "int": int, "float": float,
                    "True": True, "False": False, "None": None,
                }
                precondition_met = eval(
                    config.precondition,
                    {"__builtins__": allowed_builtins},
                    env
                )
                if not precondition_met:
                    return NodeResult(
                        success=True,
                        state_patch={"decision_precondition_failed": True},
                        signals={"summary": "Decision precondition not met", "matched_rule": None},
                    )
            except Exception as e:
                return NodeResult(
                    success=False,
                    error=f"Decision precondition evaluation error: {e}",
                )

        # Get the variable value to evaluate
        variable_value = self._get_nested_value(env, config.variable)

        # Evaluate rules in order
        matched_target = None
        matched_rule = None

        for rule in config.rules:
            condition = rule.get("condition", "")
            target = rule.get("target", "")

            if condition == "default":
                # Default rule always matches (used as fallback)
                matched_target = target
                matched_rule = rule
                break

            # Evaluate the condition against the variable value
            try:
                # Build expression: "variable_value <condition>"
                # e.g., if condition is "> 0.8" and value is 0.9, evaluate "0.9 > 0.8"
                if condition.startswith(("==", "!=", ">", "<", ">=", "<=", "in ", "not in ")):
                    expr = f"value {condition}"
                elif condition.startswith("is "):
                    expr = f"value {condition}"
                else:
                    # Treat as full expression with 'value' placeholder
                    expr = condition.replace("$value", "value")

                allowed_builtins = {
                    "len": len, "any": any, "all": all,
                    "min": min, "max": max, "str": str, "int": int, "float": float,
                    "True": True, "False": False, "None": None,
                    "in": lambda x, y: x in y,
                }

                result = eval(expr, {"__builtins__": allowed_builtins}, {"value": variable_value})

                if result:
                    matched_target = target
                    matched_rule = rule
                    break

            except Exception as e:
                # Log but continue to next rule
                state.signals.record_observation(
                    f"Decision rule evaluation error: {e}",
                    {"rule": rule, "variable": config.variable, "value": variable_value}
                )

        state_patch = {
            "decision_variable": config.variable,
            "decision_value": variable_value,
            "decision_matched_rule": matched_rule,
            "decision_target": matched_target,
        }

        return NodeResult(
            success=True,
            state_patch=state_patch,
            signals={
                "summary": f"Decision: {config.variable}={variable_value} -> {matched_target or 'no match'}",
                "matched_target": matched_target,
                "matched_rule": matched_rule,
            },
        )

    def _get_nested_value(self, context: Dict[str, Any], path: str) -> Any:
        """Get a nested value from context using dot notation."""
        parts = path.split(".")
        value = context

        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None

        return value

    def _execute_terminal(self, node: Node, state: State) -> NodeResult:
        """Execute a TERMINAL node."""
        # Execute any on_reach actions
        for action in node.on_reach:
            action_type = action.get("action")
            if action_type == "trigger_learning":
                state.signals.record_observation(
                    f"Terminal reached: {node.id}",
                    {"outcome": action.get("outcome", "unknown")}
                )

        state_patch = {"done": True}

        return NodeResult(
            success=True,
            state_patch=state_patch,
            signals={"summary": f"Reached terminal node: {node.id}"},
        )

    def _choose_next_edge(self, node: Node, state: State) -> Optional[str]:
        """Choose the next node based on edge guards.

        Handles special edge types:
        - LAMINAR: Standard smooth transition
        - TURBULENT: Retry loops with bounded retries
        - DREDGING: Memory retrieval edges
        - PERMEABLE: Cross-agent state read
        - DEPENDS_ON: Blocking dependency edges
        - DECOMPOSES_INTO: Hierarchical decomposition edges
        """
        context = state.to_context()

        # Special handling for DECISION nodes: use the decision result to route
        if node.type == NodeType.DECISION and node.decision:
            decision_target = state.get("decision_target")
            if decision_target:
                # Find edge to the decision target
                for edge in self.graph.get_outgoing_edges(node.id):
                    if edge.to_node == decision_target:
                        self.graph.update_edge_stats(edge.id, success=True)
                        state.signals.record_success(node.id, edge.id)
                        return decision_target
                # If no direct edge, fall through to normal routing

        # Get outgoing edges sorted by priority
        edges = self.graph.get_outgoing_edges(node.id)

        for edge in edges:
            # Check DEPENDS_ON edges: verify all dependencies are satisfied
            if edge.type == EdgeType.DEPENDS_ON and edge.dependency:
                if not self._check_dependencies(edge.dependency, state):
                    continue  # Skip this edge, dependencies not met

            # Check DECOMPOSES_INTO edges: verify parent is ready for decomposition
            if edge.type == EdgeType.DECOMPOSES_INTO and edge.decomposition:
                if not self._check_decomposition_ready(edge.decomposition, state):
                    continue  # Skip this edge, not ready for decomposition

            # Check guard
            if edge.guard.evaluate(context):
                # For turbulent edges, check retry budget
                if edge.type == EdgeType.TURBULENT:
                    retries = state.counters.get_retries(edge.id)
                    if edge.max_retries and retries >= edge.max_retries:
                        continue
                    state.counters.add_retry(edge.id)

                # Execute on_traverse actions
                for action in edge.on_traverse:
                    self._execute_edge_action(action, state)

                # Update edge statistics
                self.graph.update_edge_stats(edge.id, success=True)

                # Record learning signal
                state.signals.record_success(node.id, edge.id)

                return edge.to_node

        return None

    def _check_dependencies(self, dependency: DependencyConfig, state: State) -> bool:
        """Check if all dependencies for a DEPENDS_ON edge are satisfied.

        DEPENDS_ON edges physically block the target node from starting
        until the source nodes are complete.
        """
        # Check required nodes have been visited
        completed_nodes = set(state.counters.node_visits.keys())

        if dependency.require_all:
            # All required nodes must be completed
            if not all(n in completed_nodes for n in dependency.required_nodes):
                return False
        else:
            # At least one required node must be completed
            if not any(n in completed_nodes for n in dependency.required_nodes):
                return False

        # Check required state values
        for path, expected in dependency.required_state.items():
            actual = state.get(path)
            if actual != expected:
                return False

        return True

    def _check_decomposition_ready(self, decomposition: DecompositionConfig, state: State) -> bool:
        """Check if a DECOMPOSES_INTO edge is ready to traverse.

        DECOMPOSES_INTO edges break a big Goal into smaller Tasks.
        This enforces "Chunking" (breaking work into 3-4 item groups).
        """
        # Check if parent task exists in state
        parent_status = state.get(f"task_status.{decomposition.parent_id}", "pending")

        # Only decompose if parent is in "ready" or "decomposing" state
        if parent_status not in ["ready", "decomposing", "pending"]:
            return False

        # Check if we haven't exceeded max children
        existing_children = state.get(f"task_children.{decomposition.parent_id}", [])
        if len(existing_children) >= decomposition.max_children:
            return False

        return True

    def _execute_edge_action(self, action, state: State) -> None:
        """Execute an action when traversing an edge."""
        action_type = action.action

        if action_type == "analyze_failure":
            state.signals.record_improvement(
                "Consider adjusting approach after verification failure",
                {"current_approach": state.get("approach", "")}
            )
        elif action_type == "adjust_approach":
            # Flag that approach needs adjustment
            state.set("needs_approach_adjustment", True)
        elif action_type == "ask_user":
            # Flag questions for user
            questions = action.parameters.get("questions", [])
            state.set("pending_questions", questions)

    def _dredge_memory(self, node: Node, state: State) -> Dict[str, str]:
        """Dredge memory based on node configuration."""
        dredged = {}

        for query_config in node.memory.dredge:
            query = MemoryQuery(
                text_search=self._render_template(query_config.get("query", ""), state),
                subjects=query_config.get("subjects", []),
                predicates=query_config.get("predicates", []),
                limit=query_config.get("limit", 5),
                as_key=query_config.get("as_key", "memory"),
            )

            result = self.memory.query(query)
            dredged[query.as_key] = result.to_summary()

        return dredged

    def _render_prompt(self, node: Node, state: State, dredged: Dict[str, str]) -> str:
        """Render the node prompt with state and memory."""
        return self._render_template(node.prompt, state, dredged)

    def _render_template(
        self,
        template: str,
        state: State,
        dredged: Optional[Dict[str, str]] = None
    ) -> str:
        """Render a template string with state values."""
        import re

        base_context = state.to_context()
        if dredged:
            base_context["dredged_memory"] = dredged

        base_context["available_skills"] = self.manifest.skills

        context = dict(base_context)
        context["state"] = base_context

        def replace_var(match):
            path = match.group(1)
            parts = path.split(".")
            value = context
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return match.group(0)  # Keep original if not found
            return str(value) if value is not None else ""

        return re.sub(r"\{\{([^}]+)\}\}", replace_var, template)

    def _build_output_schema(self, node: Node) -> Optional[Dict[str, Any]]:
        """Build JSON schema for node output."""
        if not node.output_schema:
            return None

        return {
            "type": node.output_schema.type,
            "required": node.output_schema.required,
            "properties": node.output_schema.properties,
        }

    def _extract_state_patch(self, node: Node, llm_output: Dict[str, Any]) -> Dict[str, Any]:
        """Extract state updates from LLM output based on node configuration."""
        patch = {}

        for write in node.state_writes:
            # Get value from output
            from_path = write.from_
            if from_path.startswith("output."):
                from_path = from_path[7:]

            value = llm_output
            for part in from_path.split("."):
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    value = None
                    break

            if value is not None:
                # Set in patch
                parts = write.path.split(".")
                target = patch
                for part in parts[:-1]:
                    if part not in target:
                        target[part] = {}
                    target = target[part]
                target[parts[-1]] = value

        # Also include any direct state_patch from output
        if "state_patch" in llm_output:
            patch.update(llm_output["state_patch"])

        return patch

    def _handle_parallel_tasks(
        self,
        tasks: List[Dict[str, Any]],
        state: State
    ) -> None:
        """Handle spawning and tracking parallel tasks."""
        for task_config in tasks:
            task_id = task_config.get("task_id", str(uuid.uuid4()))
            skill = task_config.get("skill", "")
            instruction = task_config.get("instruction", "")

            # Spawn task
            task = state.parallel.spawn_task(task_id, skill, instruction)
            state.counters.parallel_tasks_spawned += 1

            # If skill executor available, execute immediately
            if self.skill_executor and skill:
                try:
                    state.parallel.start_task(task_id)
                    result = self.skill_executor.execute(
                        skill_name=skill,
                        instruction=instruction,
                        context=state.to_context(),
                    )
                    state.parallel.complete_task(task_id, result)
                    state.counters.parallel_tasks_completed += 1
                except Exception as e:
                    state.parallel.fail_task(task_id, str(e))

    def _handle_memory_writes(
        self,
        facts: List[Fact],
        state: State,
        node: Node
    ) -> None:
        """Handle writing facts to memory."""
        if not facts:
            return

        written, conflicts = self.memory.write(
            facts=facts,
            run_id=state.run_id,
            node_id=node.id,
            check_conflicts=True,
        )

        state.counters.memory_writes += len(written)

        if conflicts:
            state.signals.record_observation(
                "Memory conflicts during write",
                {"conflicts": conflicts}
            )

    # ═══════════════════════════════════════════════════════════════════
    # CONSTRAINT ENFORCEMENT - Stop Rules, Validation, Minimums
    # These methods enforce LLM behavior guardrails to prevent deviation
    # ═══════════════════════════════════════════════════════════════════

    def check_stop_rules(self, state: State) -> Optional[StopRule]:
        """
        Check if any stop rule should be triggered.

        Stop rules are critical guardrails that prevent LLM deviation.
        When triggered, execution MUST halt and ask the user.

        Returns:
            The triggered StopRule if any condition is met, None otherwise
        """
        if not self.manifest.stop_rules:
            return None

        context = state.to_context()

        for stop_rule in self.manifest.stop_rules:
            if stop_rule.matches(context):
                # Record the stop condition
                state.signals.record_observation(
                    f"Stop rule triggered: {stop_rule.condition}",
                    {
                        "action": stop_rule.action,
                        "reason": stop_rule.reason,
                    }
                )
                return stop_rule

        return None

    def validate_output(
        self,
        output: Dict[str, Any],
        state: State
    ) -> List[Tuple[ValidationRule, str]]:
        """
        Validate LLM output against all validation rules.

        Returns:
            List of (failed_rule, error_message) tuples for any failures
        """
        failures = []

        if not self.manifest.validation_rules:
            return failures

        for rule in self.manifest.validation_rules:
            is_valid, error = rule.validate(output, state.to_context())
            if not is_valid:
                failures.append((rule, error))
                state.signals.record_failure(
                    state.current_node or "unknown",
                    f"Validation failed: {rule.name}",
                    {"error": error, "severity": rule.severity}
                )

        return failures

    def apply_minimum_enforcements(
        self,
        state: State
    ) -> List[Dict[str, Any]]:
        """
        Apply minimum value enforcements to state.

        When a calculated value falls below the minimum:
        - If auto_correct=True: set to minimum and log
        - If auto_correct=False: add to stop conditions

        Returns:
            List of corrections applied (field, original, corrected)
        """
        corrections = []

        if not self.manifest.minimum_enforcements:
            return corrections

        for enforcement in self.manifest.minimum_enforcements:
            # Get current value from state
            current_value = state.get(enforcement.field)

            if current_value is None:
                continue

            try:
                numeric_value = float(current_value)
            except (ValueError, TypeError):
                continue

            if numeric_value < enforcement.minimum:
                if enforcement.auto_correct:
                    # Apply correction
                    state.set(enforcement.field, enforcement.minimum)

                    correction = {
                        "field": enforcement.field,
                        "original": numeric_value,
                        "corrected": enforcement.minimum,
                        "message": enforcement.error_message,
                    }
                    corrections.append(correction)

                    if enforcement.log_correction:
                        state.signals.record_observation(
                            f"Minimum enforcement applied: {enforcement.field}",
                            correction
                        )
                else:
                    # Record as stop condition
                    state.signals.record_failure(
                        state.current_node or "unknown",
                        f"Value below minimum: {enforcement.field}",
                        {
                            "value": numeric_value,
                            "minimum": enforcement.minimum,
                            "error": enforcement.error_message,
                        }
                    )

        return corrections

    def enforce_constraints(self, state: State, node: Node) -> Optional[str]:
        """
        Run all constraint enforcement checks after node execution.

        This is the main enforcement point that should be called after
        each node execution to ensure LLM outputs meet requirements.

        Returns:
            Error message if enforcement failed and should stop, None if ok
        """
        # Check stop rules
        triggered = self.check_stop_rules(state)
        if triggered:
            return f"STOP: {triggered.condition} - {triggered.action}"

        # Apply minimum enforcements
        corrections = self.apply_minimum_enforcements(state)
        if corrections:
            state.add_audit(
                node_id=node.id,
                action="minimum_enforcement",
                summary=f"Applied {len(corrections)} minimum corrections",
                details={"corrections": corrections}
            )

        return None

    def get_must_do_checklist(self) -> List[str]:
        """Get the list of must_do constraints for this brain."""
        return [c.description for c in self.manifest.constraints if c.type == "must_do"]

    def get_must_not_checklist(self) -> List[str]:
        """Get the list of must_not constraints for this brain."""
        return [c.description for c in self.manifest.constraints if c.type == "must_not"]

    def _determine_terminal_outcome(self, node_id: str) -> RunOutcome:
        """Determine the run outcome based on terminal node."""
        if node_id == "success":
            return RunOutcome.SUCCESS
        elif node_id == "failure":
            return RunOutcome.FAILURE
        elif node_id == "escalate":
            return RunOutcome.ESCALATED
        else:
            # Check node for outcome hint
            node = self.graph.nodes.get(node_id)
            if node:
                for action in node.on_reach:
                    if action.get("outcome") == "success":
                        return RunOutcome.SUCCESS
                    elif action.get("outcome") == "failure":
                        return RunOutcome.FAILURE
            return RunOutcome.SUCCESS  # Default to success for unknown terminals
