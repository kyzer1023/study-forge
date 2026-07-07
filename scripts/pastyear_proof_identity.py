from __future__ import annotations

import re
from typing import Final

from scripts.pastyear_proof_common import text_field
from scripts.pastyear_proof_inventory import (
    inventory_questions,
    ledger_entries,
    paper_entries,
    paper_id,
    question_text,
)
from scripts.pastyear_proof_model import Issue, IssueCode, ProofData

MALAY_HEADING: Final = "kertas soalan dalam versi bahasa malaysia"
MALAY_START_RE: Final = re.compile(
    r"^\s*(?:\(?[a-zivx]+\)?[.)]?\s+)?" +
    r"(?:diberi|diberikan|jelaskan|surih|jawab|algoritma|nombor|sebuah|pepohon|" +
    r"dua\s+matriks|tulis|lakukan|beri|banding|takrifkan|sisipkan|hapuskan|kirakan|apakah)\b",
    re.IGNORECASE,
)
QUESTION_TOKEN_RE: Final = re.compile(
    r"^(?:q|b)?(?P<number>\d{1,2})(?:[a-z])?(?:\(|$)",
    re.IGNORECASE,
)
QUESTION_NUMBER_RE: Final = re.compile(
    r"(?:^|-)(?:q|b)(?P<number>\d{1,2})(?=$|[-_(])",
    re.IGNORECASE,
)
LIST_STEP_RE: Final = re.compile(
    r"^\s*\d+\.\s*" +
    r"(?:dfs|bfs|for\b|if\b|else\b|return\b|while\b|initialize\b|num\(|procedure\b|end\b)",
    re.IGNORECASE,
)


def question_number_from_id(question_id: str) -> int | None:
    match = QUESTION_NUMBER_RE.search(question_id)
    if match is not None:
        return int(match.group("number"))
    if "-" in question_id or "_" in question_id:
        return None
    for token in question_id.replace("_", "-").split("-"):
        token_match = QUESTION_TOKEN_RE.match(token)
        if token_match is not None:
            return int(token_match.group("number"))
    return None


def top_question_key(paper: str, question_id: str) -> str | None:
    number = question_number_from_id(question_id)
    if number is None:
        return None
    return f"{paper}:q{number}"


def is_malay_mirror_text(value: str | None) -> bool:
    if value is None:
        return False
    lowered = value.casefold()
    return MALAY_HEADING in lowered or MALAY_START_RE.search(value) is not None


def add_bilingual_mirror_issues(data: ProofData, issues: list[Issue]) -> None:
    seen_inventory_keys: set[str] = set()
    flagged_inventory_keys: set[str] = set()
    for question in inventory_questions(data.question_inventory):
        key = top_question_key(question.paper_id, question.question_id)
        if key is None:
            continue
        if is_malay_mirror_text(question.question_text) and key in seen_inventory_keys:
            if key not in flagged_inventory_keys:
                issues.append(
                    Issue(
                        IssueCode.BILINGUAL_MIRROR_QUESTION_DUPLICATE,
                        "question-inventory.json",
                        f"{question.question_id} looks like a Malay mirror duplicate for {key}",
                    )
                )
                flagged_inventory_keys.add(key)
            continue
        seen_inventory_keys.add(key)

    seen_ledger_keys: set[str] = set()
    flagged_ledger_keys: set[str] = set()
    for entry in ledger_entries(data.answer_ledger):
        question_id = text_field(entry, "question_id")
        current_paper = text_field(entry, "paper_id") or "<unknown paper>"
        if question_id is None:
            continue
        key = top_question_key(current_paper, question_id)
        if key is None:
            continue
        if is_malay_mirror_text(question_text(entry)) and key in seen_ledger_keys:
            if key not in flagged_ledger_keys:
                issues.append(
                    Issue(
                        IssueCode.BILINGUAL_MIRROR_QUESTION_DUPLICATE,
                        "answer-ledger.json",
                        f"{question_id} looks like a Malay mirror duplicate for {key}",
                    )
                )
                flagged_ledger_keys.add(key)
            continue
        seen_ledger_keys.add(key)


def add_inventory_order_issues(data: ProofData, issues: list[Issue]) -> None:
    for index, paper in enumerate(paper_entries(data.question_inventory)):
        current_paper = paper_id(paper, index)
        questions = paper.get("questions")
        if not isinstance(questions, list):
            continue
        last_number: int | None = None
        last_question_id = ""
        for question in questions:
            if not isinstance(question, dict):
                continue
            question_id = text_field(question, "question_id")
            if question_id is None:
                continue
            current_text = question_text(question)
            if current_text is not None and LIST_STEP_RE.search(current_text):
                detail = (
                    f"{current_paper} {question_id} looks like a numbered algorithm/list step, " +
                    "not a top-level question"
                )
                issues.append(
                    Issue(
                        IssueCode.QUESTION_INVENTORY_ORDER_DRIFT,
                        "question-inventory.json",
                        detail,
                    )
                )
            number = question_number_from_id(question_id)
            if number is None:
                continue
            if last_number is not None and number < last_number:
                detail = (
                    f"{current_paper} has {question_id} after {last_question_id}; " +
                    "printed question order decreases"
                )
                issues.append(
                    Issue(
                        IssueCode.QUESTION_INVENTORY_ORDER_DRIFT,
                        "question-inventory.json",
                        detail,
                    )
                )
                continue
            last_number = number
            last_question_id = question_id


def add_identity_issues(data: ProofData, issues: list[Issue]) -> None:
    add_bilingual_mirror_issues(data, issues)
    add_inventory_order_issues(data, issues)
