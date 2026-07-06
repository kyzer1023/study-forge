from __future__ import annotations

import json
from pathlib import Path
from typing import assert_never

from .model import Issue, JsonObject, JsonValue


def read_text(root: Path, relative_path: str, issues: list[Issue]) -> str:
    path = root / relative_path
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(Issue(relative_path, "missing required file"))
    except UnicodeDecodeError as error:
        issues.append(Issue(relative_path, f"cannot read UTF-8 text: {error}"))
    return ""


def write_file(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(content, encoding="utf-8")


def to_json_value(value: JsonValue) -> JsonValue:
    match value:
        case str() | int() | float() | bool() | None:
            return value
        case list():
            return [to_json_value(item) for item in value]
        case dict():
            return {str(key): to_json_value(item) for key, item in value.items()}
        case _ as unreachable:
            assert_never(unreachable)


def read_json_object(root: Path, relative_path: str, issues: list[Issue]) -> JsonObject | None:
    path = root / relative_path
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except UnicodeDecodeError as error:
        issues.append(Issue(relative_path, f"cannot read UTF-8 JSON: {error}"))
        return None
    except json.JSONDecodeError as error:
        issues.append(Issue(relative_path, f"cannot parse JSON: {error}"))
        return None
    data = to_json_value(loaded)
    if isinstance(data, dict):
        return data
    issues.append(Issue(relative_path, "JSON root must be an object"))
    return None


def text_json(container: JsonObject, key: str) -> str | None:
    value = container.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def bool_json(container: JsonObject, key: str) -> bool | None:
    value = container.get(key)
    if isinstance(value, bool):
        return value
    return None


def object_json(container: JsonObject, key: str) -> JsonObject | None:
    value = container.get(key)
    if isinstance(value, dict):
        return value
    return None


def object_list_json(container: JsonObject, key: str) -> tuple[JsonObject, ...]:
    value = container.get(key)
    if isinstance(value, list):
        return tuple(item for item in value if isinstance(item, dict))
    return ()


def string_list_json(container: JsonObject, key: str) -> tuple[str, ...]:
    value = container.get(key)
    if isinstance(value, list):
        return tuple(item.strip() for item in value if isinstance(item, str) and item.strip())
    return ()


def normalized_json_text(container: JsonObject, key: str) -> str:
    value = text_json(container, key)
    if value is None:
        return ""
    return "_".join(value.casefold().replace("-", " ").split())
