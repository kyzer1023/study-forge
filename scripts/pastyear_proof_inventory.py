from __future__ import annotations

from dataclasses import dataclass

from scripts.pastyear_proof_common import NON_ANSWERABLE_STATUSES, normalized, text_field
from scripts.pastyear_proof_model import JsonObject, JsonValue


@dataclass(frozen=True, slots=True)
class ExpectedSubpart:
    question_id: str
    paper_id: str
    status: str
    record: JsonObject


@dataclass(frozen=True, slots=True)
class InventorySubpart:
    question_id: str
    status: str
    record: JsonObject


def ledger_entries(value: JsonValue) -> tuple[JsonObject, ...]:
    if isinstance(value, list):
        return tuple(entry for entry in value if isinstance(entry, dict))
    if isinstance(value, dict):
        for key in ("answers", "entries", "items"):
            entries = value.get(key)
            if isinstance(entries, list):
                return tuple(entry for entry in entries if isinstance(entry, dict))
    return ()


def ledger_question_ids(value: JsonValue) -> set[str]:
    ids: set[str] = set()
    for entry in ledger_entries(value):
        question_id = text_field(entry, "question_id")
        if question_id is not None:
            ids.add(question_id)
    return ids


def ledger_statuses_by_question_id(value: JsonValue) -> dict[str, str]:
    statuses: dict[str, str] = {}
    for entry in ledger_entries(value):
        question_id = text_field(entry, "question_id")
        if question_id is not None:
            statuses[question_id] = normalized(text_field(entry, "status"))
    return statuses


def paper_entries(value: JsonValue) -> tuple[JsonObject, ...]:
    if isinstance(value, dict):
        papers = value.get("papers")
        if isinstance(papers, list):
            return tuple(paper for paper in papers if isinstance(paper, dict))
    if isinstance(value, list):
        return tuple(paper for paper in value if isinstance(paper, dict))
    return ()


def paper_id(paper: JsonObject, index: int) -> str:
    return text_field(paper, "paper_id") or f"paper[{index}]"


def mark_value_is_number(value: JsonValue | None) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def expected_subparts(value: JsonValue) -> tuple[ExpectedSubpart, ...]:
    subparts: list[ExpectedSubpart] = []
    for index, paper in enumerate(paper_entries(value)):
        granularity = paper.get("extraction_granularity")
        if not isinstance(granularity, dict):
            continue
        expected = granularity.get("expected_answerable_subparts")
        if not isinstance(expected, list):
            continue
        current_paper_id = paper_id(paper, index)
        for entry in expected:
            if not isinstance(entry, dict):
                continue
            question_id = text_field(entry, "question_id")
            if question_id is not None:
                subparts.append(
                    ExpectedSubpart(
                        question_id=question_id,
                        paper_id=current_paper_id,
                        status=normalized(text_field(entry, "status")),
                        record=entry,
                    )
                )
    return tuple(subparts)


def collect_inventory_subparts(value: JsonValue, inside_subparts: bool, rows: list[InventorySubpart]) -> None:
    if isinstance(value, list):
        for child in value:
            collect_inventory_subparts(child, inside_subparts, rows)
        return
    if not isinstance(value, dict):
        return
    marks = value.get("marks")
    question_id = text_field(value, "question_id")
    parent_id = text_field(value, "parent_question_id")
    if question_id is not None and (inside_subparts or parent_id is not None) and mark_value_is_number(marks):
        rows.append(
            InventorySubpart(
                question_id=question_id,
                status=normalized(text_field(value, "status")),
                record=value,
            )
        )
    for key in ("subparts", "children"):
        collect_inventory_subparts(value.get(key), True, rows)


def inventory_subparts(value: JsonValue) -> tuple[InventorySubpart, ...]:
    rows: list[InventorySubpart] = []
    for paper in paper_entries(value):
        collect_inventory_subparts(paper.get("questions"), False, rows)
    return tuple(rows)


def status_is_exempt(status: str) -> bool:
    return status in NON_ANSWERABLE_STATUSES


def expected_subpart_is_exempt(
    subpart: ExpectedSubpart,
    inventory_by_id: dict[str, InventorySubpart],
    ledger_statuses: dict[str, str],
) -> bool:
    inventory = inventory_by_id.get(subpart.question_id)
    statuses = [subpart.status, ledger_statuses.get(subpart.question_id, "")]
    if inventory is not None:
        statuses.append(inventory.status)
    return any(status_is_exempt(status) for status in statuses)


def expected_subpart_ids_requiring_answers(question_inventory: JsonValue, answer_ledger: JsonValue) -> set[str]:
    inventory_by_id = {subpart.question_id: subpart for subpart in inventory_subparts(question_inventory)}
    ledger_statuses = ledger_statuses_by_question_id(answer_ledger)
    return {
        subpart.question_id
        for subpart in expected_subparts(question_inventory)
        if not expected_subpart_is_exempt(subpart, inventory_by_id, ledger_statuses)
    }


def answerable_subpart_ids(question_inventory: JsonValue, answer_ledger: JsonValue) -> tuple[str, ...]:
    ids = {
        subpart.question_id
        for subpart in inventory_subparts(question_inventory)
        if not status_is_exempt(subpart.status)
    }
    ids.update(expected_subpart_ids_requiring_answers(question_inventory, answer_ledger))
    return tuple(sorted(ids))
