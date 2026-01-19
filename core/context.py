"""Context utilities for brain execution.

These helpers keep controller templates and eval-based routing consistent.
"""

from __future__ import annotations

from typing import Any, Mapping


class DotDict(dict):
    """A dict that supports attribute (dot) access recursively."""

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__()
        self.update(*args, **kwargs)

    def __getattr__(self, key: str) -> Any:
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key: str, value: Any) -> None:
        self[key] = value

    def __delattr__(self, key: str) -> None:
        del self[key]

    def __setitem__(self, key: str, value: Any) -> None:
        super().__setitem__(key, self._wrap(value))

    def update(self, *args: Any, **kwargs: Any) -> None:
        items = dict(*args, **kwargs)
        for k, v in items.items():
            self[k] = v

    @classmethod
    def _wrap(cls, value: Any) -> Any:
        if isinstance(value, DotDict):
            return value
        if isinstance(value, dict):
            return DotDict(value)
        if isinstance(value, list):
            return [cls._wrap(v) for v in value]
        return value


def build_eval_env(context: Mapping[str, Any]) -> dict[str, Any]:
    """Build a locals dict for eval()-based routing/checks.

    Supports both styles:
    - `state.data.foo` (matches controller.md + templates)
    - `data.get('foo')` (legacy / convenience)
    """
    dot = DotDict(dict(context))
    env: dict[str, Any] = dict(dot)
    env["state"] = dot
    return env

