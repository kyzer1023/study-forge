from __future__ import annotations

from scripts.pastyear_proof_classification import add_classification_issues
from scripts.pastyear_proof_common import (
    ANSWERED_STATUSES,
    JUSTIFIED_DUPLICATE_STATUSES,
    OBJECTIVE_QUESTION_TYPES,
    explanation_fingerprint,
    normalized,
    question_text_is_placeholder,
    text_field,
)
from scripts.pastyear_proof_inventory import (
    answerable_subpart_ids,
    expected_subpart_is_exempt,
    expected_subparts,
    inventory_questions,
    inventory_questions_by_question_id,
    inventory_subparts,
    ledger_entries,
    ledger_entries_by_question_id,
    ledger_question_ids,
    ledger_statuses_by_question_id,
    question_text,
)
from scripts.pastyear_proof_model import Issue, IssueCode, JsonObject, JsonValue, ObjectiveExplanation, ProofData


def objective_explanations(value: JsonValue) -> tuple[ObjectiveExplanation, ...]:
    answers: list[ObjectiveExplanation] = []
    for entry in ledger_entries(value):
        status = normalized(text_field(entry, "status"))
        question_type = normalized(text_field(entry, "question_type"))
        question_id = text_field(entry, "question_id")
        fingerprint = explanation_fingerprint(text_field(entry, "student_explanation"))
        if status in ANSWERED_STATUSES and question_type in OBJECTIVE_QUESTION_TYPES and question_id is not None and fingerprint:
            answers.append(
                ObjectiveExplanation(
                    question_id=question_id,
                    question_text=text_field(entry, "question_text") or "",
                    answer=text_field(entry, "answer") or "",
                    fingerprint=fingerprint,
                )
            )
    return tuple(answers)


def justified_duplicate_entries(report: JsonObject) -> tuple[JsonObject, ...]:
    entries: list[JsonObject] = []
    for key in ("accepted_duplicate_explanations", "generic_objective_explanation_justifications", "findings"):
        value = report.get(key)
        if isinstance(value, list):
            entries.extend(item for item in value if isinstance(item, dict))
    return tuple(entries)


def duplicate_explanation_is_justified(reports: tuple[JsonObject, ...], fingerprint: str, question_ids: set[str]) -> bool:
    for report in reports:
        for entry in justified_duplicate_entries(report):
            status = normalized(text_field(entry, "status"))
            code = normalized(text_field(entry, "issue_code") or text_field(entry, "code"))
            entry_fingerprint = explanation_fingerprint(
                text_field(entry, "normalized_student_explanation")
                or text_field(entry, "student_explanation")
                or text_field(entry, "explanation")
            )
            ids = entry.get("question_ids")
            justified_ids: set[str] = set()
            if isinstance(ids, list):
                justified_ids = {item.strip() for item in ids if isinstance(item, str) and item.strip()}
            has_issue_code = code in {"generic_objective_explanation", ""}
            if status in JUSTIFIED_DUPLICATE_STATUSES and has_issue_code and entry_fingerprint == fingerprint and question_ids <= justified_ids and text_field(entry, "justification") is not None:
                return True
    return False


def add_generic_objective_explanation_issues(data: ProofData, issues: list[Issue]) -> None:
    by_fingerprint: dict[str, list[ObjectiveExplanation]] = {}
    for answer in objective_explanations(data.answer_ledger):
        by_fingerprint.setdefault(answer.fingerprint, []).append(answer)
    for fingerprint, answers in by_fingerprint.items():
        question_ids = {answer.question_id for answer in answers}
        question_texts = {answer.question_text for answer in answers if answer.question_text}
        answer_texts = {answer.answer for answer in answers if answer.answer}
        if len(question_ids) >= 2 and (len(question_texts) >= 2 or len(answer_texts) >= 2) and not duplicate_explanation_is_justified(data.verifier_reports, fingerprint, question_ids):
            issues.append(
                Issue(
                    IssueCode.GENERIC_OBJECTIVE_EXPLANATION,
                    "answer-ledger.json",
                    f"answered objective questions {', '.join(sorted(question_ids))} reuse the same normalized student_explanation",
                )
            )


def add_expected_subpart_inventory_issues(data: ProofData, issues: list[Issue]) -> None:
    inventory_by_id = {subpart.question_id: subpart for subpart in inventory_subparts(data.question_inventory)}
    ledger_statuses = ledger_statuses_by_question_id(data.answer_ledger)
    missing_ids: set[str] = set()
    for subpart in expected_subparts(data.question_inventory):
        if subpart.question_id not in inventory_by_id and not expected_subpart_is_exempt(subpart, inventory_by_id, ledger_statuses):
            missing_ids.add(subpart.question_id)
    for question_id in sorted(missing_ids):
        issues.append(
            Issue(
                IssueCode.EXPECTED_SUBPART_MISSING_INVENTORY_ROW,
                "question-inventory.json",
                f"{question_id} is listed in expected_answerable_subparts but has no inventory child row",
            )
        )


def normalized_question_text(value: str) -> str:
    return " ".join(value.casefold().replace("-", " ").split())


def question_text_tokens(value: str) -> set[str]:
    tokens: set[str] = set()
    token_chars: list[str] = []
    for char in normalized_question_text(value):
        if char.isalnum():
            token_chars.append(char)
            continue
        if token_chars:
            token = "".join(token_chars)
            if len(token) > 2:
                tokens.add(token)
            token_chars = []
    if token_chars:
        token = "".join(token_chars)
        if len(token) > 2:
            tokens.add(token)
    return tokens


def question_texts_conflict(ledger_text: str, inventory_text: str) -> bool:
    ledger_normalized = normalized_question_text(ledger_text)
    inventory_normalized = normalized_question_text(inventory_text)
    if ledger_normalized == inventory_normalized:
        return False
    if ledger_normalized in inventory_normalized or inventory_normalized in ledger_normalized:
        return False
    ledger_tokens = question_text_tokens(ledger_normalized)
    inventory_tokens = question_text_tokens(inventory_normalized)
    smaller_count = min(len(ledger_tokens), len(inventory_tokens))
    if smaller_count < 4:
        return False
    shared_count = len(ledger_tokens & inventory_tokens)
    return shared_count / smaller_count < 0.5


def add_duplicate_question_id_issues(data: ProofData, issues: list[Issue]) -> None:
    for question_id, entries in sorted(ledger_entries_by_question_id(data.answer_ledger).items()):
        if len(entries) > 1:
            issues.append(
                Issue(
                    IssueCode.DUPLICATE_LEDGER_QUESTION_ID,
                    "answer-ledger.json",
                    f"{question_id} appears {len(entries)} times in the answer ledger",
                )
            )
    for question_id, questions in sorted(inventory_questions_by_question_id(data.question_inventory).items()):
        if len(questions) > 1:
            paper_ids = ", ".join(sorted({question.paper_id for question in questions}))
            issues.append(
                Issue(
                    IssueCode.DUPLICATE_QUESTION_INVENTORY_ID,
                    "question-inventory.json",
                    f"{question_id} appears {len(questions)} times in the question inventory under {paper_ids}",
                )
            )


def add_ledger_inventory_text_drift_issues(data: ProofData, issues: list[Issue]) -> None:
    inventory_by_id = inventory_questions_by_question_id(data.question_inventory)
    for question_id, entries in sorted(ledger_entries_by_question_id(data.answer_ledger).items()):
        inventory_entries = inventory_by_id.get(question_id)
        if len(entries) != 1 or inventory_entries is None or len(inventory_entries) != 1:
            continue
        ledger_text = question_text(entries[0])
        inventory_text = inventory_entries[0].question_text
        if ledger_text is None or inventory_text is None:
            continue
        if question_texts_conflict(ledger_text, inventory_text):
            issues.append(
                Issue(
                    IssueCode.LEDGER_QUESTION_TEXT_DRIFT,
                    "answer-ledger.json",
                    f"{question_id} ledger question_text does not match question-inventory.json",
                )
            )


def add_placeholder_question_text_issues(data: ProofData, issues: list[Issue]) -> None:
    for entry in ledger_entries(data.answer_ledger):
        placeholder_text = question_text(entry)
        if not question_text_is_placeholder(placeholder_text):
            continue
        question_id = text_field(entry, "question_id") or "<unknown question>"
        issues.append(
            Issue(
                IssueCode.PLACEHOLDER_QUESTION_TEXT,
                "answer-ledger.json",
                f"{question_id} keeps a compacted worker-report placeholder instead of the source question text",
            )
        )
    for question in inventory_questions(data.question_inventory):
        if not question_text_is_placeholder(question.question_text):
            continue
        issues.append(
            Issue(
                IssueCode.PLACEHOLDER_QUESTION_TEXT,
                "question-inventory.json",
                f"{question.question_id} keeps a compacted worker-report placeholder instead of the source question text",
            )
        )


def add_answer_issues(data: ProofData, issues: list[Issue]) -> None:
    add_duplicate_question_id_issues(data, issues)
    add_placeholder_question_text_issues(data, issues)
    add_ledger_inventory_text_drift_issues(data, issues)
    add_expected_subpart_inventory_issues(data, issues)
    ledger_ids = ledger_question_ids(data.answer_ledger)
    for question_id in answerable_subpart_ids(data.question_inventory, data.answer_ledger):
        if question_id not in ledger_ids:
            issues.append(Issue(IssueCode.ANSWERABLE_SUBPART_MISSING_LEDGER_ENTRY, "answer-ledger.json", f"{question_id} is a mark-bearing answerable subpart but has no ledger entry"))
    add_generic_objective_explanation_issues(data, issues)
    add_classification_issues(data, issues)
    for entry in ledger_entries(data.answer_ledger):
        status = normalized(text_field(entry, "status"))
        if status in ANSWERED_STATUSES:
            refs = entry.get("source_refs")
            if not isinstance(refs, list) or len(refs) == 0:
                question_id = text_field(entry, "question_id") or "<unknown question>"
                issues.append(Issue(IssueCode.ANSWERED_WITHOUT_SOURCE_REFS, "answer-ledger.json", f"{question_id} is Answered from source but has no source_refs"))
