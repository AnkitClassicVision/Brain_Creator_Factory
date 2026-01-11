"""Memory - Long-term memory (sediment) store for brains."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class Provenance:
    """Provenance tracking for a fact."""
    source: str              # Where the fact came from
    kind: str                # Type: "tool", "llm", "user", "learning"
    confidence: float = 1.0  # Source confidence
    timestamp: Optional[datetime] = None
    run_id: Optional[str] = None
    node_id: Optional[str] = None
    note: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "kind": self.kind,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "run_id": self.run_id,
            "node_id": self.node_id,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Provenance:
        return cls(
            source=data.get("source", "unknown"),
            kind=data.get("kind", "unknown"),
            confidence=data.get("confidence", 1.0),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None,
            run_id=data.get("run_id"),
            node_id=data.get("node_id"),
            note=data.get("note"),
        )


@dataclass
class Triplet:
    """A semantic triplet for relationship tracking."""
    subject: str
    predicate: str
    object: str

    def to_tuple(self) -> Tuple[str, str, str]:
        return (self.subject, self.predicate, self.object)

    def to_dict(self) -> Dict[str, str]:
        return {
            "subject": self.subject,
            "predicate": self.predicate,
            "object": self.object,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> Triplet:
        return cls(
            subject=data.get("subject", ""),
            predicate=data.get("predicate", ""),
            object=data.get("object", ""),
        )


@dataclass
class Fact:
    """A fact stored in memory."""
    fact_id: str
    text: str
    confidence: float = 1.0
    kind: str = "fact"  # fact, decision, observation, lesson
    provenance: List[Provenance] = field(default_factory=list)
    triplets: List[Triplet] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fact_id": self.fact_id,
            "text": self.text,
            "confidence": self.confidence,
            "kind": self.kind,
            "provenance": [p.to_dict() for p in self.provenance],
            "triplets": [t.to_dict() for t in self.triplets],
            "tags": self.tags,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Fact:
        return cls(
            fact_id=data.get("fact_id", str(uuid.uuid4())),
            text=data.get("text", ""),
            confidence=data.get("confidence", 1.0),
            kind=data.get("kind", "fact"),
            provenance=[Provenance.from_dict(p) for p in data.get("provenance", [])],
            triplets=[Triplet.from_dict(t) for t in data.get("triplets", [])],
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )


@dataclass
class MemoryRecord:
    """A versioned record in the memory store."""
    record_id: str
    fact: Fact
    valid_from: datetime
    valid_to: Optional[datetime] = None
    run_id: Optional[str] = None
    node_id: Optional[str] = None
    supersedes: Optional[str] = None  # ID of record this supersedes

    def is_valid(self, as_of: Optional[datetime] = None) -> bool:
        """Check if record is valid at a given time."""
        check_time = as_of or datetime.utcnow()
        if check_time < self.valid_from:
            return False
        if self.valid_to and check_time > self.valid_to:
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "fact": self.fact.to_dict(),
            "valid_from": self.valid_from.isoformat(),
            "valid_to": self.valid_to.isoformat() if self.valid_to else None,
            "run_id": self.run_id,
            "node_id": self.node_id,
            "supersedes": self.supersedes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MemoryRecord:
        return cls(
            record_id=data.get("record_id", str(uuid.uuid4())),
            fact=Fact.from_dict(data.get("fact", {})),
            valid_from=datetime.fromisoformat(data.get("valid_from", datetime.utcnow().isoformat())),
            valid_to=datetime.fromisoformat(data["valid_to"]) if data.get("valid_to") else None,
            run_id=data.get("run_id"),
            node_id=data.get("node_id"),
            supersedes=data.get("supersedes"),
        )


@dataclass
class MemoryQuery:
    """A query to search memory."""
    text_search: Optional[str] = None
    subjects: List[str] = field(default_factory=list)
    predicates: List[str] = field(default_factory=list)
    objects: List[str] = field(default_factory=list)
    kinds: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    min_confidence: float = 0.0
    limit: int = 10
    as_key: str = "memory"  # Key to use when injecting into prompt


@dataclass
class MemoryQueryResult:
    """Result of a memory query."""
    records: List[MemoryRecord]
    query: MemoryQuery
    total_matches: int

    def to_summary(self) -> str:
        """Create a compact summary for injection into prompts."""
        if not self.records:
            return "No relevant memories found."

        lines = []
        for record in self.records:
            fact = record.fact
            confidence_str = f"[{fact.confidence:.0%}]" if fact.confidence < 1.0 else ""
            lines.append(f"- {fact.text} {confidence_str}")

        return "\n".join(lines)


class MemoryStore:
    """Persistent memory store for a brain."""

    def __init__(self, path: Path):
        self.path = path
        self._records: List[MemoryRecord] = []
        self._triplet_index: Dict[Tuple[str, str], List[str]] = {}  # (subject, predicate) -> [record_ids]
        self._loaded = False

    def load(self) -> None:
        """Load all records from disk."""
        if self._loaded:
            return

        if not self.path.exists():
            self.path.touch()
            self._loaded = True
            return

        with open(self.path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    record = MemoryRecord.from_dict(data)
                    self._records.append(record)
                    self._index_record(record)
                except Exception as e:
                    print(f"Error loading memory record: {e}")

        self._loaded = True

    def _index_record(self, record: MemoryRecord) -> None:
        """Index a record's triplets."""
        for triplet in record.fact.triplets:
            key = (triplet.subject, triplet.predicate)
            if key not in self._triplet_index:
                self._triplet_index[key] = []
            self._triplet_index[key].append(record.record_id)

    def write(
        self,
        facts: List[Fact],
        run_id: str,
        node_id: str,
        check_conflicts: bool = True
    ) -> Tuple[List[str], List[str]]:
        """
        Write facts to memory.
        Returns: (written_ids, conflict_messages)
        """
        self.load()

        written_ids = []
        conflicts = []

        for fact in facts:
            # Check for conflicts
            if check_conflicts and fact.triplets:
                fact_conflicts = self.check_triplet_conflicts(fact)
                if fact_conflicts:
                    conflicts.extend(fact_conflicts)
                    continue

            # Create record
            record = MemoryRecord(
                record_id=str(uuid.uuid4()),
                fact=fact,
                valid_from=datetime.utcnow(),
                run_id=run_id,
                node_id=node_id,
            )

            # Append to file
            with open(self.path, "a") as f:
                f.write(json.dumps(record.to_dict()) + "\n")

            # Update in-memory state
            self._records.append(record)
            self._index_record(record)
            written_ids.append(record.record_id)

        return written_ids, conflicts

    def check_triplet_conflicts(self, fact: Fact) -> List[str]:
        """Check if new fact conflicts with existing triplets."""
        conflicts = []

        for triplet in fact.triplets:
            key = (triplet.subject, triplet.predicate)
            if key in self._triplet_index:
                # Find existing values for this subject-predicate pair
                for record_id in self._triplet_index[key]:
                    record = self._get_record(record_id)
                    if record and record.is_valid():
                        for existing in record.fact.triplets:
                            if (existing.subject == triplet.subject and
                                existing.predicate == triplet.predicate and
                                existing.object != triplet.object):
                                conflicts.append(
                                    f"Conflict: ({triplet.subject}, {triplet.predicate}): "
                                    f"existing='{existing.object}' vs new='{triplet.object}'"
                                )

        return conflicts

    def _get_record(self, record_id: str) -> Optional[MemoryRecord]:
        """Get a record by ID."""
        for record in self._records:
            if record.record_id == record_id:
                return record
        return None

    def query(
        self,
        q: MemoryQuery,
        as_of: Optional[datetime] = None
    ) -> MemoryQueryResult:
        """Query the memory store."""
        self.load()

        matches = []

        for record in self._records:
            if not record.is_valid(as_of):
                continue

            fact = record.fact

            # Filter by confidence
            if fact.confidence < q.min_confidence:
                continue

            # Filter by kind
            if q.kinds and fact.kind not in q.kinds:
                continue

            # Filter by tags
            if q.tags and not any(tag in fact.tags for tag in q.tags):
                continue

            # Filter by triplet components
            if q.subjects:
                if not any(t.subject in q.subjects for t in fact.triplets):
                    continue

            if q.predicates:
                if not any(t.predicate in q.predicates for t in fact.triplets):
                    continue

            if q.objects:
                if not any(t.object in q.objects for t in fact.triplets):
                    continue

            # Text search (simple substring match)
            if q.text_search:
                if q.text_search.lower() not in fact.text.lower():
                    continue

            matches.append(record)

        # Sort by confidence (descending) then by recency
        matches.sort(key=lambda r: (-r.fact.confidence, -r.valid_from.timestamp()))

        total = len(matches)
        limited = matches[:q.limit]

        return MemoryQueryResult(
            records=limited,
            query=q,
            total_matches=total,
        )

    def invalidate(self, record_id: str, reason: str = "") -> bool:
        """Invalidate a record (set valid_to to now)."""
        self.load()

        for record in self._records:
            if record.record_id == record_id and record.is_valid():
                record.valid_to = datetime.utcnow()
                # Rewrite file to persist change
                self._save_all()
                return True

        return False

    def _save_all(self) -> None:
        """Rewrite all records to disk."""
        with open(self.path, "w") as f:
            for record in self._records:
                f.write(json.dumps(record.to_dict()) + "\n")

    def get_all_valid(self, as_of: Optional[datetime] = None) -> List[MemoryRecord]:
        """Get all currently valid records."""
        self.load()
        return [r for r in self._records if r.is_valid(as_of)]

    def get_lessons(self) -> List[Fact]:
        """Get all lesson-type facts."""
        self.load()
        lessons = []
        for record in self._records:
            if record.is_valid() and record.fact.kind == "lesson":
                lessons.append(record.fact)
        return lessons

    def write_lesson(
        self,
        text: str,
        run_id: str,
        node_id: str,
        confidence: float = 0.8,
        tags: List[str] = None
    ) -> str:
        """Write a lesson learned to memory."""
        fact = Fact(
            fact_id=f"lesson_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            text=text,
            confidence=confidence,
            kind="lesson",
            provenance=[Provenance(
                source="learning_engine",
                kind="learning",
                confidence=confidence,
                timestamp=datetime.utcnow(),
                run_id=run_id,
                node_id=node_id,
            )],
            tags=tags or ["lesson", "auto-generated"],
        )

        ids, _ = self.write([fact], run_id, node_id, check_conflicts=False)
        return ids[0] if ids else ""

    def stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        self.load()

        valid = [r for r in self._records if r.is_valid()]
        kinds = {}
        for r in valid:
            kind = r.fact.kind
            kinds[kind] = kinds.get(kind, 0) + 1

        return {
            "total_records": len(self._records),
            "valid_records": len(valid),
            "by_kind": kinds,
            "unique_subjects": len(set(
                t.subject
                for r in valid
                for t in r.fact.triplets
            )),
        }
