"""TOON - Token-Oriented Object Notation.

A compact data format optimized for LLM context windows, reducing token usage
by ~40% compared to verbose JSON while maintaining readability.

Format:
    key: value
    nested.key: value
    array_key: [item1, item2]

Features:
- Strings are emitted raw (with newlines escaped)
- Non-strings are JSON-serialized in compact form
- Supports dot-notation for nested keys
- Supports flattening and unflattening of nested structures
- Handles special types (datetime, enums, etc.)
"""

from __future__ import annotations

import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union


def encode(obj: Dict[str, Any], flatten: bool = True) -> str:
    """Encode a dictionary into TOON format.

    Args:
        obj: The dictionary to encode
        flatten: If True, flatten nested dicts to dot-notation keys

    Returns:
        TOON-formatted string

    Example:
        >>> encode({"user": {"name": "Alice", "age": 30}})
        'user.name: Alice\\nuser.age: 30\\n'
    """
    if flatten:
        obj = _flatten(obj)

    lines = []
    for key, value in obj.items():
        if value is None:
            continue

        encoded_value = _encode_value(value)
        lines.append(f"{key}: {encoded_value}")

    return "\n".join(lines) + "\n" if lines else ""


def decode(payload: str, unflatten: bool = True) -> Dict[str, Any]:
    """Decode a TOON-formatted string into a dictionary.

    Args:
        payload: The TOON string to decode
        unflatten: If True, unflatten dot-notation keys to nested dicts

    Returns:
        Decoded dictionary

    Example:
        >>> decode('user.name: Alice\\nuser.age: 30\\n')
        {'user': {'name': 'Alice', 'age': 30}}
    """
    result: Dict[str, Any] = {}

    for raw_line in (payload or "").splitlines():
        line = raw_line.strip()

        # Skip empty lines and comments
        if not line or line.startswith("#"):
            continue

        # Handle lines without colons as continuation text
        if ":" not in line:
            result["_text"] = (result.get("_text", "") + "\n" + line).strip()
            continue

        # Split on first colon only
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        # Decode the value
        result[key] = _decode_value(value)

    if unflatten:
        result = _unflatten(result)

    return result


def encode_compact(obj: Dict[str, Any]) -> str:
    """Encode to ultra-compact single-line format for maximum token savings.

    Example:
        >>> encode_compact({"a": 1, "b": "hello"})
        'a:1|b:hello'
    """
    parts = []
    flat = _flatten(obj)

    for key, value in flat.items():
        if value is None:
            continue
        encoded = _encode_value(value, compact=True)
        parts.append(f"{key}:{encoded}")

    return "|".join(parts)


def decode_compact(payload: str) -> Dict[str, Any]:
    """Decode ultra-compact single-line format.

    Example:
        >>> decode_compact('a:1|b:hello')
        {'a': 1, 'b': 'hello'}
    """
    result: Dict[str, Any] = {}

    if not payload:
        return result

    for part in payload.split("|"):
        if ":" not in part:
            continue
        key, value = part.split(":", 1)
        result[key.strip()] = _decode_value(value.strip())

    return _unflatten(result)


def _encode_value(value: Any, compact: bool = False) -> str:
    """Encode a single value to TOON format."""
    if value is None:
        return "null"

    if isinstance(value, bool):
        return "true" if value else "false"

    if isinstance(value, (int, float)):
        return str(value)

    if isinstance(value, str):
        # Escape newlines and pipes (for compact format)
        escaped = value.replace("\\", "\\\\").replace("\n", "\\n")
        if compact:
            escaped = escaped.replace("|", "\\|").replace(":", "\\:")
        return escaped

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, Enum):
        return str(value.value)

    if isinstance(value, (list, dict)):
        # Use compact JSON for complex types
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))

    # Fallback to string representation
    return str(value)


def _decode_value(value: str) -> Any:
    """Decode a single TOON value."""
    if not value:
        return ""

    # Handle special literals
    if value == "null":
        return None
    if value == "true":
        return True
    if value == "false":
        return False

    # Try to parse as JSON (for arrays, objects, numbers)
    if value.startswith("{") or value.startswith("["):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass

    # Try to parse as number
    if value.replace(".", "", 1).replace("-", "", 1).isdigit():
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            pass

    # Unescape string
    return value.replace("\\n", "\n").replace("\\|", "|").replace("\\:", ":").replace("\\\\", "\\")


def _flatten(obj: Dict[str, Any], parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
    """Flatten a nested dictionary to dot-notation keys.

    Example:
        >>> _flatten({"a": {"b": 1, "c": 2}})
        {'a.b': 1, 'a.c': 2}
    """
    items: List[tuple] = []

    for key, value in obj.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key

        if isinstance(value, dict) and value:
            # Recursively flatten nested dicts
            items.extend(_flatten(value, new_key, sep).items())
        else:
            items.append((new_key, value))

    return dict(items)


def _unflatten(obj: Dict[str, Any], sep: str = ".") -> Dict[str, Any]:
    """Unflatten dot-notation keys to nested dictionary.

    Example:
        >>> _unflatten({'a.b': 1, 'a.c': 2})
        {'a': {'b': 1, 'c': 2}}
    """
    result: Dict[str, Any] = {}

    for key, value in obj.items():
        parts = key.split(sep)
        target = result

        for part in parts[:-1]:
            if part not in target:
                target[part] = {}
            elif not isinstance(target[part], dict):
                # Handle collision: convert to dict with _value key
                target[part] = {"_value": target[part]}
            target = target[part]

        target[parts[-1]] = value

    return result


def state_to_toon(state_data: Dict[str, Any], max_depth: int = 3) -> str:
    """Convert state data to TOON format optimized for LLM prompts.

    This function:
    - Flattens nested structures
    - Truncates very long strings
    - Limits array lengths
    - Prioritizes important fields

    Args:
        state_data: The state dictionary to convert
        max_depth: Maximum nesting depth to preserve

    Returns:
        TOON-formatted state string
    """
    # Priority fields to include first
    priority_fields = [
        "current_node", "stage", "user_request",
        "understood_request", "approach", "ready_to_proceed",
        "done", "error"
    ]

    # Truncate and limit the data
    truncated = _truncate_for_context(state_data, max_depth)

    # Build output with priority fields first
    lines = []
    flat = _flatten(truncated)

    # Add priority fields first
    for field in priority_fields:
        for key in list(flat.keys()):
            if key == field or key.endswith(f".{field}"):
                lines.append(f"{key}: {_encode_value(flat.pop(key))}")

    # Add remaining fields
    for key, value in flat.items():
        lines.append(f"{key}: {_encode_value(value)}")

    return "\n".join(lines) + "\n" if lines else ""


def _truncate_for_context(obj: Any, max_depth: int, current_depth: int = 0) -> Any:
    """Truncate data for LLM context to save tokens."""
    if current_depth >= max_depth:
        if isinstance(obj, dict):
            return f"{{...{len(obj)} keys}}"
        if isinstance(obj, list):
            return f"[...{len(obj)} items]"
        if isinstance(obj, str) and len(obj) > 200:
            return obj[:200] + "..."
        return obj

    if isinstance(obj, dict):
        return {
            k: _truncate_for_context(v, max_depth, current_depth + 1)
            for k, v in obj.items()
        }

    if isinstance(obj, list):
        if len(obj) > 10:
            truncated = [_truncate_for_context(v, max_depth, current_depth + 1) for v in obj[:10]]
            truncated.append(f"...and {len(obj) - 10} more")
            return truncated
        return [_truncate_for_context(v, max_depth, current_depth + 1) for v in obj]

    if isinstance(obj, str) and len(obj) > 500:
        return obj[:500] + "..."

    return obj


# Aliases for backward compatibility with codex_brain_factory naming
tune_encode = encode
tune_decode = decode
