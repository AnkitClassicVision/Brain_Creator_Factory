"""Learning - Learning engine that analyzes runs and proposes changes."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .graph import Graph, Edge, EdgeType, RelationType, Relationship
from .state import State
from .memory import MemoryStore
from .controller import RunResult, RunOutcome


class ChangeType(str, Enum):
    """Types of changes that can be proposed."""
    UPDATE_EDGE_PRIORITY = "update_edge_priority"
    UPDATE_EDGE_WEIGHT = "update_edge_weight"
    UPDATE_GUARD = "update_guard"
    UPDATE_PROMPT = "update_prompt"
    ADD_EDGE = "add_edge"
    REMOVE_EDGE = "remove_edge"
    ADD_NODE = "add_node"
    ADD_RELATIONSHIP = "add_relationship"
    UPDATE_RELATIONSHIP = "update_relationship"
    UPDATE_MAX_RETRIES = "update_max_retries"


@dataclass
class Change:
    """A proposed change to the brain."""
    change_id: str
    type: ChangeType
    target: str  # ID of the element to change
    description: str
    reason: str

    # Old and new values
    old_value: Any = None
    new_value: Any = None

    # Auto-apply settings
    auto_apply: bool = False
    requires_approval: bool = True
    risk_level: str = "low"  # low, medium, high

    # Application status
    applied: bool = False
    applied_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "change_id": self.change_id,
            "type": self.type.value,
            "target": self.target,
            "description": self.description,
            "reason": self.reason,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "auto_apply": self.auto_apply,
            "requires_approval": self.requires_approval,
            "risk_level": self.risk_level,
            "applied": self.applied,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Change:
        return cls(
            change_id=data.get("change_id", str(uuid.uuid4())),
            type=ChangeType(data.get("type", "update_edge_priority")),
            target=data.get("target", ""),
            description=data.get("description", ""),
            reason=data.get("reason", ""),
            old_value=data.get("old_value"),
            new_value=data.get("new_value"),
            auto_apply=data.get("auto_apply", False),
            requires_approval=data.get("requires_approval", True),
            risk_level=data.get("risk_level", "low"),
            applied=data.get("applied", False),
            applied_at=datetime.fromisoformat(data["applied_at"]) if data.get("applied_at") else None,
        )


@dataclass
class Proposal:
    """A collection of related changes."""
    proposal_id: str
    created_at: datetime
    based_on_runs: List[str]
    changes: List[Change]
    summary: str
    confidence: float = 0.5

    # Status
    status: str = "pending"  # pending, approved, rejected, applied

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "created_at": self.created_at.isoformat(),
            "based_on_runs": self.based_on_runs,
            "changes": [c.to_dict() for c in self.changes],
            "summary": self.summary,
            "confidence": self.confidence,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Proposal:
        return cls(
            proposal_id=data.get("proposal_id", str(uuid.uuid4())),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.utcnow().isoformat())),
            based_on_runs=data.get("based_on_runs", []),
            changes=[Change.from_dict(c) for c in data.get("changes", [])],
            summary=data.get("summary", ""),
            confidence=data.get("confidence", 0.5),
            status=data.get("status", "pending"),
        )


@dataclass
class RunAnalysis:
    """Analysis of a single run."""
    run_id: str
    outcome: RunOutcome
    total_steps: int
    duration_seconds: float

    # Path analysis
    path_taken: List[str] = field(default_factory=list)
    retries_by_edge: Dict[str, int] = field(default_factory=dict)
    visits_by_node: Dict[str, int] = field(default_factory=dict)

    # Signals
    successes: List[Dict[str, Any]] = field(default_factory=list)
    failures: List[Dict[str, Any]] = field(default_factory=list)
    observations: List[Dict[str, Any]] = field(default_factory=list)
    improvements: List[Dict[str, Any]] = field(default_factory=list)

    # Patterns
    bottleneck_nodes: List[str] = field(default_factory=list)
    underused_edges: List[str] = field(default_factory=list)
    overused_edges: List[str] = field(default_factory=list)


class LearningEngine:
    """
    Engine for analyzing runs and generating improvement proposals.

    Key capabilities:
    - Analyze run patterns and identify issues
    - Propose graph modifications
    - Update relationships based on observations
    - Apply approved changes
    """

    def __init__(
        self,
        graph: Graph,
        memory: MemoryStore,
        evolution_path: Path,
        auto_apply_config: Optional[Dict[str, bool]] = None,
    ):
        self.graph = graph
        self.memory = memory
        self.evolution_path = evolution_path
        self.proposals_path = evolution_path / "proposals.jsonl"
        self.applied_path = evolution_path / "applied.jsonl"

        # What can be auto-applied
        self.auto_apply_config = auto_apply_config or {
            "edge_priorities": True,
            "edge_weights": True,
            "relationship_weights": True,
            "max_retries": True,
            "guard_thresholds": False,
            "prompts": False,
            "add_edges": False,
            "remove_edges": False,
            "add_nodes": False,
        }

    def analyze_run(self, run_result: RunResult, state: State) -> RunAnalysis:
        """Analyze a single run and extract patterns."""
        duration = (run_result.ended_at - run_result.started_at).total_seconds()

        analysis = RunAnalysis(
            run_id=run_result.run_id,
            outcome=run_result.outcome,
            total_steps=run_result.total_steps,
            duration_seconds=duration,
            path_taken=self._extract_path(state),
            retries_by_edge=state.counters.retries,
            visits_by_node=state.counters.node_visits,
            successes=state.signals.successes,
            failures=state.signals.failures,
            observations=state.signals.observations,
            improvements=state.signals.improvements,
        )

        # Identify bottlenecks (nodes visited many times)
        avg_visits = sum(analysis.visits_by_node.values()) / max(len(analysis.visits_by_node), 1)
        for node_id, visits in analysis.visits_by_node.items():
            if visits > avg_visits * 2:
                analysis.bottleneck_nodes.append(node_id)

        # Identify edge usage patterns
        edge_usage = self._calculate_edge_usage()
        avg_usage = sum(edge_usage.values()) / max(len(edge_usage), 1)
        for edge_id, usage in edge_usage.items():
            if usage < avg_usage * 0.5:
                analysis.underused_edges.append(edge_id)
            elif usage > avg_usage * 2:
                analysis.overused_edges.append(edge_id)

        return analysis

    def _extract_path(self, state: State) -> List[str]:
        """Extract the path taken through the graph from audit events."""
        # Load audit from state if available
        path = []
        for event in state.audit:
            if event.node_id and event.node_id not in path[-1:]:
                path.append(event.node_id)
        return path

    def _calculate_edge_usage(self) -> Dict[str, int]:
        """Calculate usage statistics for edges."""
        return {
            edge.id: edge.success_count + edge.failure_count
            for edge in self.graph.edges
        }

    def generate_proposals(
        self,
        analyses: List[RunAnalysis],
        min_confidence: float = 0.5,
    ) -> List[Proposal]:
        """Generate improvement proposals based on run analyses."""
        proposals = []

        # Analyze patterns across runs
        aggregate = self._aggregate_analyses(analyses)

        # Generate proposals for different types of improvements
        proposals.extend(self._propose_priority_changes(aggregate, min_confidence))
        proposals.extend(self._propose_retry_changes(aggregate, min_confidence))
        proposals.extend(self._propose_relationship_updates(aggregate, min_confidence))
        proposals.extend(self._propose_structural_changes(aggregate, min_confidence))

        # Save proposals
        for proposal in proposals:
            self._save_proposal(proposal)

        return proposals

    def _aggregate_analyses(self, analyses: List[RunAnalysis]) -> Dict[str, Any]:
        """Aggregate patterns across multiple runs."""
        aggregate = {
            "total_runs": len(analyses),
            "success_count": sum(1 for a in analyses if a.outcome == RunOutcome.SUCCESS),
            "failure_count": sum(1 for a in analyses if a.outcome == RunOutcome.FAILURE),
            "avg_steps": sum(a.total_steps for a in analyses) / max(len(analyses), 1),
            "avg_duration": sum(a.duration_seconds for a in analyses) / max(len(analyses), 1),

            "edge_successes": {},
            "edge_failures": {},
            "node_visit_counts": {},
            "bottleneck_frequency": {},
            "retry_totals": {},
            "all_improvements": [],
            "all_failures": [],
        }

        for analysis in analyses:
            # Track edge success/failure
            for success in analysis.successes:
                edge_id = success.get("edge_id", "")
                if edge_id:
                    aggregate["edge_successes"][edge_id] = aggregate["edge_successes"].get(edge_id, 0) + 1

            for failure in analysis.failures:
                node_id = failure.get("node_id", "")
                if node_id:
                    aggregate["edge_failures"][node_id] = aggregate["edge_failures"].get(node_id, 0) + 1

            # Track node visits
            for node_id, visits in analysis.visits_by_node.items():
                if node_id not in aggregate["node_visit_counts"]:
                    aggregate["node_visit_counts"][node_id] = []
                aggregate["node_visit_counts"][node_id].append(visits)

            # Track bottlenecks
            for node_id in analysis.bottleneck_nodes:
                aggregate["bottleneck_frequency"][node_id] = aggregate["bottleneck_frequency"].get(node_id, 0) + 1

            # Track retries
            for edge_id, count in analysis.retries_by_edge.items():
                if edge_id not in aggregate["retry_totals"]:
                    aggregate["retry_totals"][edge_id] = []
                aggregate["retry_totals"][edge_id].append(count)

            # Collect improvements and failures
            aggregate["all_improvements"].extend(analysis.improvements)
            aggregate["all_failures"].extend(analysis.failures)

        return aggregate

    def _propose_priority_changes(
        self,
        aggregate: Dict[str, Any],
        min_confidence: float
    ) -> List[Proposal]:
        """Propose edge priority changes based on usage patterns."""
        proposals = []
        changes = []

        # Find edges that succeed often but have low priority
        for edge in self.graph.edges:
            success_count = aggregate["edge_successes"].get(edge.id, 0)
            total_runs = aggregate["total_runs"]

            if success_count > 0 and total_runs > 0:
                success_rate = success_count / total_runs

                # If edge succeeds often but has low priority, suggest raising it
                if success_rate > 0.7 and edge.priority > 2:
                    confidence = min(0.9, success_rate)
                    if confidence >= min_confidence:
                        changes.append(Change(
                            change_id=str(uuid.uuid4()),
                            type=ChangeType.UPDATE_EDGE_PRIORITY,
                            target=edge.id,
                            description=f"Lower priority (higher precedence) for edge {edge.id}",
                            reason=f"Edge succeeds {success_rate:.0%} of the time but has priority {edge.priority}",
                            old_value=edge.priority,
                            new_value=max(1, edge.priority - 1),
                            auto_apply=self.auto_apply_config.get("edge_priorities", True),
                            requires_approval=not self.auto_apply_config.get("edge_priorities", True),
                            risk_level="low",
                        ))

        if changes:
            proposals.append(Proposal(
                proposal_id=str(uuid.uuid4()),
                created_at=datetime.utcnow(),
                based_on_runs=[],
                changes=changes,
                summary=f"Adjust {len(changes)} edge priorities based on success patterns",
                confidence=0.7,
            ))

        return proposals

    def _propose_retry_changes(
        self,
        aggregate: Dict[str, Any],
        min_confidence: float
    ) -> List[Proposal]:
        """Propose changes to retry limits."""
        proposals = []
        changes = []

        for edge_id, retry_counts in aggregate["retry_totals"].items():
            if not retry_counts:
                continue

            avg_retries = sum(retry_counts) / len(retry_counts)
            max_retries_seen = max(retry_counts)

            # Find the edge
            edge = next((e for e in self.graph.edges if e.id == edge_id), None)
            if not edge or edge.type != EdgeType.TURBULENT:
                continue

            # If retries frequently hit max, suggest increasing
            if edge.max_retries and max_retries_seen >= edge.max_retries:
                changes.append(Change(
                    change_id=str(uuid.uuid4()),
                    type=ChangeType.UPDATE_MAX_RETRIES,
                    target=edge_id,
                    description=f"Increase max_retries for edge {edge_id}",
                    reason=f"Edge frequently hits retry limit (avg: {avg_retries:.1f}, max: {max_retries_seen})",
                    old_value=edge.max_retries,
                    new_value=edge.max_retries + 1,
                    auto_apply=self.auto_apply_config.get("max_retries", True),
                    requires_approval=not self.auto_apply_config.get("max_retries", True),
                    risk_level="low",
                ))

            # If retries are rarely used, suggest decreasing
            elif edge.max_retries and avg_retries < 0.5 and edge.max_retries > 1:
                changes.append(Change(
                    change_id=str(uuid.uuid4()),
                    type=ChangeType.UPDATE_MAX_RETRIES,
                    target=edge_id,
                    description=f"Decrease max_retries for edge {edge_id}",
                    reason=f"Retries rarely needed (avg: {avg_retries:.1f})",
                    old_value=edge.max_retries,
                    new_value=max(1, edge.max_retries - 1),
                    auto_apply=self.auto_apply_config.get("max_retries", True),
                    requires_approval=not self.auto_apply_config.get("max_retries", True),
                    risk_level="low",
                ))

        if changes:
            proposals.append(Proposal(
                proposal_id=str(uuid.uuid4()),
                created_at=datetime.utcnow(),
                based_on_runs=[],
                changes=changes,
                summary=f"Adjust {len(changes)} retry limits based on usage patterns",
                confidence=0.65,
            ))

        return proposals

    def _propose_relationship_updates(
        self,
        aggregate: Dict[str, Any],
        min_confidence: float
    ) -> List[Proposal]:
        """Propose relationship weight updates."""
        proposals = []
        changes = []

        # Analyze failure patterns to find correlations
        failure_nodes = [f.get("node_id") for f in aggregate["all_failures"] if f.get("node_id")]
        bottlenecks = list(aggregate["bottleneck_frequency"].keys())

        # If failures often happen at certain nodes, create/update relationships
        for node_id in set(failure_nodes):
            failure_count = failure_nodes.count(node_id)
            if failure_count >= 2:  # At least 2 failures

                # Check if there's a relationship indicating this
                existing = None
                for rel in self.graph.relationships:
                    if rel.to_concept == node_id and "failure" in rel.type.value:
                        existing = rel
                        break

                if existing:
                    # Update weight
                    new_weight = min(2.0, existing.weight + 0.1 * failure_count)
                    changes.append(Change(
                        change_id=str(uuid.uuid4()),
                        type=ChangeType.UPDATE_RELATIONSHIP,
                        target=existing.id,
                        description=f"Increase failure relationship weight for {node_id}",
                        reason=f"Node failed {failure_count} times",
                        old_value=existing.weight,
                        new_value=new_weight,
                        auto_apply=self.auto_apply_config.get("relationship_weights", True),
                        requires_approval=False,
                        risk_level="low",
                    ))
                else:
                    # Create new relationship
                    changes.append(Change(
                        change_id=str(uuid.uuid4()),
                        type=ChangeType.ADD_RELATIONSHIP,
                        target=f"failure_indicator_{node_id}",
                        description=f"Add failure indicator relationship for {node_id}",
                        reason=f"Node failed {failure_count} times across runs",
                        old_value=None,
                        new_value={
                            "from": "execution",
                            "to": node_id,
                            "type": "indicates",
                            "weight": 0.5 + (0.1 * failure_count),
                        },
                        auto_apply=self.auto_apply_config.get("relationship_weights", True),
                        requires_approval=False,
                        risk_level="low",
                    ))

        if changes:
            proposals.append(Proposal(
                proposal_id=str(uuid.uuid4()),
                created_at=datetime.utcnow(),
                based_on_runs=[],
                changes=changes,
                summary=f"Update {len(changes)} relationships based on observed patterns",
                confidence=0.6,
            ))

        return proposals

    def _propose_structural_changes(
        self,
        aggregate: Dict[str, Any],
        min_confidence: float
    ) -> List[Proposal]:
        """Propose structural graph changes (requires approval)."""
        proposals = []
        changes = []

        # If a node is consistently a bottleneck, suggest adding parallel path
        for node_id, frequency in aggregate["bottleneck_frequency"].items():
            if frequency >= aggregate["total_runs"] * 0.5:  # Bottleneck in 50%+ runs
                changes.append(Change(
                    change_id=str(uuid.uuid4()),
                    type=ChangeType.ADD_EDGE,
                    target=f"bypass_{node_id}",
                    description=f"Consider adding bypass for bottleneck node {node_id}",
                    reason=f"Node is bottleneck in {frequency}/{aggregate['total_runs']} runs",
                    old_value=None,
                    new_value={"suggestion": f"Add alternative path around {node_id}"},
                    auto_apply=False,
                    requires_approval=True,
                    risk_level="medium",
                ))

        if changes:
            proposals.append(Proposal(
                proposal_id=str(uuid.uuid4()),
                created_at=datetime.utcnow(),
                based_on_runs=[],
                changes=changes,
                summary=f"Structural improvements for {len(changes)} bottleneck areas",
                confidence=0.5,
                status="pending",  # Always requires review
            ))

        return proposals

    def _save_proposal(self, proposal: Proposal) -> None:
        """Save a proposal to disk."""
        with open(self.proposals_path, "a") as f:
            f.write(json.dumps(proposal.to_dict()) + "\n")

    def apply_proposal(self, proposal: Proposal) -> Tuple[int, List[str]]:
        """
        Apply an approved proposal.
        Returns: (applied_count, error_messages)
        """
        applied = 0
        errors = []

        for change in proposal.changes:
            if change.applied:
                continue

            if change.requires_approval and proposal.status != "approved":
                continue

            try:
                success = self._apply_change(change)
                if success:
                    change.applied = True
                    change.applied_at = datetime.utcnow()
                    applied += 1
            except Exception as e:
                errors.append(f"Failed to apply {change.change_id}: {str(e)}")

        # Save updated graph
        if applied > 0:
            self.graph.save(self.graph._path if hasattr(self.graph, '_path') else Path("graph.yaml"))

            # Log applied changes
            with open(self.applied_path, "a") as f:
                for change in proposal.changes:
                    if change.applied:
                        f.write(json.dumps(change.to_dict()) + "\n")

        return applied, errors

    def _apply_change(self, change: Change) -> bool:
        """Apply a single change to the graph."""

        if change.type == ChangeType.UPDATE_EDGE_PRIORITY:
            for edge in self.graph.edges:
                if edge.id == change.target:
                    edge.priority = change.new_value
                    return True

        elif change.type == ChangeType.UPDATE_MAX_RETRIES:
            for edge in self.graph.edges:
                if edge.id == change.target:
                    edge.max_retries = change.new_value
                    return True

        elif change.type == ChangeType.UPDATE_EDGE_WEIGHT:
            for edge in self.graph.edges:
                if edge.id == change.target:
                    edge.weight = change.new_value
                    return True

        elif change.type == ChangeType.UPDATE_RELATIONSHIP:
            for rel in self.graph.relationships:
                if rel.id == change.target:
                    rel.weight = change.new_value
                    rel.updated_at = datetime.utcnow()
                    return True

        elif change.type == ChangeType.ADD_RELATIONSHIP:
            new_rel_data = change.new_value
            self.graph.relationships.append(Relationship(
                id=change.target,
                from_concept=new_rel_data.get("from", ""),
                to_concept=new_rel_data.get("to", ""),
                type=RelationType(new_rel_data.get("type", "correlates")),
                weight=new_rel_data.get("weight", 1.0),
            ))
            return True

        return False

    def auto_apply_safe_changes(self, proposals: List[Proposal]) -> Tuple[int, List[str]]:
        """Apply all changes that don't require approval."""
        total_applied = 0
        all_errors = []

        for proposal in proposals:
            for change in proposal.changes:
                if change.auto_apply and not change.requires_approval and not change.applied:
                    try:
                        success = self._apply_change(change)
                        if success:
                            change.applied = True
                            change.applied_at = datetime.utcnow()
                            total_applied += 1
                    except Exception as e:
                        all_errors.append(f"Failed to auto-apply {change.change_id}: {str(e)}")

        return total_applied, all_errors

    def write_lesson(self, lesson: str, run_id: str, node_id: str = "learning") -> None:
        """Write a lesson learned to memory."""
        self.memory.write_lesson(
            text=lesson,
            run_id=run_id,
            node_id=node_id,
            confidence=0.8,
            tags=["lesson", "auto-generated", "learning-engine"],
        )

    def get_pending_proposals(self) -> List[Proposal]:
        """Get all pending proposals."""
        proposals = []
        if self.proposals_path.exists():
            with open(self.proposals_path) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        proposal = Proposal.from_dict(data)
                        if proposal.status == "pending":
                            proposals.append(proposal)
                    except Exception:
                        continue
        return proposals
