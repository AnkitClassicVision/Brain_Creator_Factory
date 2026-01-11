"""Evolution - High-level evolution engine for brain improvement."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .brain import Brain
from .graph import Graph
from .state import State
from .memory import MemoryStore
from .controller import BrainController, RunResult, RunOutcome
from .learning import LearningEngine, RunAnalysis, Proposal


class EvolutionEngine:
    """
    High-level engine for evolving brains over time.

    Orchestrates:
    - Run analysis across multiple executions
    - Learning and proposal generation
    - Change application with approval workflow
    - Memory-based learning persistence
    """

    def __init__(self, brain: Brain):
        self.brain = brain.load()
        self.graph = Graph.load(brain.graph_path)
        self.memory = MemoryStore(brain.memory_path)

        self.learning = LearningEngine(
            graph=self.graph,
            memory=self.memory,
            evolution_path=brain.evolution_path,
            auto_apply_config=self._get_auto_apply_config(),
        )

        self._analyses: List[RunAnalysis] = []
        self._pending_proposals: List[Proposal] = []

    def _get_auto_apply_config(self) -> Dict[str, bool]:
        """Get auto-apply configuration from brain manifest."""
        if not self.brain.manifest or not self.brain.manifest.learning:
            return {}
        return self.brain.manifest.learning.auto_update

    def record_run(self, result: RunResult, state: State) -> RunAnalysis:
        """Record and analyze a completed run."""
        analysis = self.learning.analyze_run(result, state)
        self._analyses.append(analysis)

        # Write summary to memory
        if result.outcome == RunOutcome.SUCCESS:
            self.memory.write_lesson(
                text=f"Successful run pattern: {' -> '.join(analysis.path_taken[:5])}",
                run_id=result.run_id,
                node_id="evolution_engine",
                confidence=0.8,
            )
        elif result.outcome == RunOutcome.FAILURE:
            failure_nodes = [f.get("node_id") for f in analysis.failures if f.get("node_id")]
            if failure_nodes:
                self.memory.write_lesson(
                    text=f"Failure pattern: Issues at nodes {failure_nodes}",
                    run_id=result.run_id,
                    node_id="evolution_engine",
                    confidence=0.7,
                )

        return analysis

    def evolve(
        self,
        min_runs: int = 3,
        min_confidence: float = 0.5,
        auto_apply: bool = True,
    ) -> Tuple[List[Proposal], int, List[str]]:
        """
        Run the evolution cycle.

        Returns: (proposals, applied_count, errors)
        """
        # Check if we have enough data
        if len(self._analyses) < min_runs:
            return [], 0, [f"Need at least {min_runs} runs, have {len(self._analyses)}"]

        # Generate proposals
        proposals = self.learning.generate_proposals(
            self._analyses,
            min_confidence=min_confidence,
        )

        self._pending_proposals.extend(proposals)

        # Apply safe changes if enabled
        applied_count = 0
        errors = []

        if auto_apply:
            applied_count, errors = self.learning.auto_apply_safe_changes(proposals)

            if applied_count > 0:
                # Save updated graph
                self.graph.save(self.brain.graph_path)

                # Record evolution
                self._record_evolution(proposals, applied_count)

        return proposals, applied_count, errors

    def _record_evolution(self, proposals: List[Proposal], applied_count: int) -> None:
        """Record evolution event."""
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "proposals": len(proposals),
            "applied": applied_count,
            "proposal_ids": [p.proposal_id for p in proposals],
        }

        log_path = self.brain.evolution_path / "evolution_log.jsonl"
        with open(log_path, "a") as f:
            f.write(json.dumps(record) + "\n")

    def get_pending_proposals(self) -> List[Proposal]:
        """Get proposals awaiting approval."""
        return self.learning.get_pending_proposals()

    def approve_proposal(self, proposal_id: str) -> Tuple[int, List[str]]:
        """Approve and apply a pending proposal."""
        for proposal in self._pending_proposals:
            if proposal.proposal_id == proposal_id:
                proposal.status = "approved"
                applied, errors = self.learning.apply_proposal(proposal)

                if applied > 0:
                    self.graph.save(self.brain.graph_path)

                return applied, errors

        return 0, [f"Proposal not found: {proposal_id}"]

    def reject_proposal(self, proposal_id: str, reason: str = "") -> bool:
        """Reject a pending proposal."""
        for proposal in self._pending_proposals:
            if proposal.proposal_id == proposal_id:
                proposal.status = "rejected"
                return True
        return False

    def get_evolution_stats(self) -> Dict[str, Any]:
        """Get statistics about brain evolution."""
        log_path = self.brain.evolution_path / "evolution_log.jsonl"
        events = []

        if log_path.exists():
            with open(log_path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            events.append(json.loads(line))
                        except:
                            pass

        # Calculate stats
        total_proposals = sum(e.get("proposals", 0) for e in events)
        total_applied = sum(e.get("applied", 0) for e in events)

        # Edge stats from graph
        edge_stats = {}
        for edge in self.graph.edges:
            if edge.success_count + edge.failure_count > 0:
                edge_stats[edge.id] = {
                    "success": edge.success_count,
                    "failure": edge.failure_count,
                    "success_rate": edge.success_count / (edge.success_count + edge.failure_count),
                }

        # Memory stats
        memory_stats = self.memory.stats()

        return {
            "evolution_events": len(events),
            "total_proposals": total_proposals,
            "total_applied": total_applied,
            "pending_proposals": len(self._pending_proposals),
            "analyses_collected": len(self._analyses),
            "edge_stats": edge_stats,
            "memory_stats": memory_stats,
            "relationships": len(self.graph.relationships),
        }

    def get_improvement_suggestions(self) -> List[Dict[str, Any]]:
        """Get high-level improvement suggestions based on analysis."""
        suggestions = []

        if not self._analyses:
            return [{"suggestion": "Run the brain a few times to collect data for improvements"}]

        # Check success rate
        success_count = sum(1 for a in self._analyses if a.outcome == RunOutcome.SUCCESS)
        success_rate = success_count / len(self._analyses)

        if success_rate < 0.5:
            suggestions.append({
                "priority": "high",
                "suggestion": f"Low success rate ({success_rate:.0%}). Review failure patterns.",
                "action": "analyze_failures",
            })

        # Check for consistent bottlenecks
        bottleneck_counts = {}
        for analysis in self._analyses:
            for node in analysis.bottleneck_nodes:
                bottleneck_counts[node] = bottleneck_counts.get(node, 0) + 1

        for node, count in bottleneck_counts.items():
            if count >= len(self._analyses) * 0.5:
                suggestions.append({
                    "priority": "medium",
                    "suggestion": f"Node '{node}' is a consistent bottleneck. Consider splitting or adding parallel paths.",
                    "action": "add_parallel_path",
                    "target": node,
                })

        # Check for high retry usage
        for analysis in self._analyses:
            for edge_id, retries in analysis.retries_by_edge.items():
                if retries >= 2:
                    suggestions.append({
                        "priority": "low",
                        "suggestion": f"Edge '{edge_id}' frequently uses retries. Consider adjusting guard or max_retries.",
                        "action": "adjust_edge",
                        "target": edge_id,
                    })

        # Check relationship insights
        strong_relationships = [
            r for r in self.graph.relationships
            if r.weight > 1.2
        ]
        if strong_relationships:
            suggestions.append({
                "priority": "info",
                "suggestion": f"Strong correlations found: {[r.id for r in strong_relationships[:3]]}",
                "action": "review_relationships",
            })

        return suggestions

    def reset_analyses(self) -> None:
        """Clear collected analyses to start fresh."""
        self._analyses = []

    def export_brain_state(self) -> Dict[str, Any]:
        """Export complete brain state for backup/transfer."""
        return {
            "manifest": self.brain.manifest.to_dict() if self.brain.manifest else {},
            "graph": self.graph.to_dict(),
            "memory_stats": self.memory.stats(),
            "evolution_stats": self.get_evolution_stats(),
            "exported_at": datetime.utcnow().isoformat(),
        }
