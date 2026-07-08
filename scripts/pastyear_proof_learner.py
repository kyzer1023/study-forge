from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
from typing import Final, override

from scripts.pastyear_proof_common import (
    ANSWERED_STATUSES,
    evidence_text,
    normalized,
    question_text_is_placeholder,
    text_field,
)
from scripts.pastyear_proof_inventory import inventory_subparts, ledger_entries
from scripts.pastyear_proof_model import Issue, IssueCode, JsonObject, JsonValue, ProofData

TOKEN_RE: Final[re.Pattern[str]] = re.compile(r"[a-z0-9]+")
MARK_VALUE_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*(?:marks?|pts?|points?)\b|[\[(](\d+(?:\.\d+)?)/\d+(?:\.\d+)?[\])]",
    re.IGNORECASE,
)
OPTION_ONLY_RE: Final[re.Pattern[str]] = re.compile(
    r"\s*(?:the\s+)?(?:correct\s+)?(?:answer\s+is\s+)?(?:(?:option|choice)\s*)?[a-f]\s*[\).:]?\s*",
    re.IGNORECASE,
)
OPTION_LINE_RE: Final[re.Pattern[str]] = re.compile(
    r"(?:^|[\n\r;])\s*(?:\(?[a-f]\)|[a-f][.)])\s+\S",
    re.IGNORECASE,
)
OPTION_WORD_RE: Final[re.Pattern[str]] = re.compile(r"\b(?:option|choice)\s+[a-f]\b", re.IGNORECASE)
NUMBERED_STEP_RE: Final[re.Pattern[str]] = re.compile(r"(?:^|\n)\s*\d+[.)]\s+\S")
HIGH_MARK_THRESHOLD: Final[float] = 4.0
MCQ_OPTION_FIELDS: Final[tuple[str, ...]] = (
    "options",
    "choices",
    "mcq_options",
    "answer_options",
    "choice_options",
)
COMMON_ANSWER_TOKENS: Final[frozenset[str]] = frozenset(
    {
        "a",
        "an",
        "and",
        "as",
        "by",
        "for",
        "from",
        "in",
        "is",
        "it",
        "of",
        "or",
        "the",
        "to",
        "when",
        "with",
    }
)
CODING_MARKERS: Final[tuple[str, ...]] = (
    "for ",
    "while ",
    "if ",
    "else",
    "return",
    "procedure",
    "algorithm",
    "pseudocode",
    ":=",
    "->",
    "{",
    "}",
)
TRACE_MARKERS: Final[tuple[str, ...]] = ("step", "state", "trace", "->", "=>", "|", "\n1", "\n2", "\n3")
REASONING_MARKERS: Final[tuple[str, ...]] = ("because", "therefore", "so ", "then", "after", "hence", "\n", ";")
TRUE_FALSE_TYPES: Final[frozenset[str]] = frozenset({"true_false", "true/false", "boolean"})
LOW_MARK_DEFINITION_TYPES: Final[frozenset[str]] = frozenset({"definition", "short_answer", "short answer"})
WORKED_PROMPT_TERMS: Final[tuple[str, ...]] = (
    "apply the",
    "construct",
    "describe and illustrate",
    "draw",
    "illustrate",
    "perform the",
    "show steps",
    "show the steps",
    "sort the following",
    "trace",
    "using a figure",
    "using a table",
)
WORKED_STEP_MARKERS: Final[tuple[str, ...]] = (
    "bucket",
    "compare",
    "diagram",
    "digit",
    "initial",
    "iteration",
    "pass",
    "phase",
    "round",
    "state",
    "step",
    "swap",
    "table",
    "trace",
    "|",
)


class LearnerTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    @override
    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data)


def normalized_tokens(text: str) -> tuple[str, ...]:
    matches: list[str] = TOKEN_RE.findall(text.casefold())
    return tuple(token for token in matches if token not in COMMON_ANSWER_TOKENS)


def answer_coverage_is_visible(learner_text: str, answer: str) -> bool:
    answer_tokens = set(normalized_tokens(answer))
    if len(answer_tokens) < 3:
        return True
    learner_tokens = set(normalized_tokens(learner_text))
    missing = answer_tokens - learner_tokens
    return len(missing) <= max(1, len(answer_tokens) // 5)


def learner_html_path(data: ProofData) -> Path | None:
    for field in ("learner_html_path", "rendered_html_path", "html_path"):
        value = text_field(data.qa_report, field)
        if value is not None:
            return data.proof_dir / value
    default_path = data.proof_dir / "index.html"
    if default_path.is_file():
        return default_path
    return None


def learner_text(path: Path) -> str | None:
    try:
        html = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    parser = LearnerTextParser()
    parser.feed(html)
    parser.close()
    return " ".join(parser.parts)


def marks_by_question_id(question_inventory: JsonValue) -> dict[str, float]:
    marks: dict[str, float] = {}
    for subpart in inventory_subparts(question_inventory):
        value = subpart.record.get("marks")
        if isinstance(value, int | float) and not isinstance(value, bool):
            marks[subpart.question_id] = float(value)
    return marks


def numeric_mark(value: JsonValue) -> float | None:
    if isinstance(value, int | float) and not isinstance(value, bool):
        return float(value)
    return None


def inferred_mark_from_entry(entry: JsonObject) -> float | None:
    text = evidence_text(
        [
            entry.get("question_text"),
            entry.get("prompt"),
            entry.get("instruction"),
            entry.get("context"),
        ]
    )
    for match in MARK_VALUE_RE.finditer(text):
        raw_mark = match.group(1) or match.group(2)
        if raw_mark is not None:
            return float(raw_mark)
    return None


def effective_mark(entry: JsonObject, inventory_mark: float | None) -> float | None:
    return numeric_mark(entry.get("marks")) or inventory_mark or inferred_mark_from_entry(entry)


def entry_has_choice_payload(entry: JsonObject) -> bool:
    for field in MCQ_OPTION_FIELDS:
        value = entry.get(field)
        if isinstance(value, list) and sum(1 for item in value if evidence_text(item).strip()) >= 2:
            return True
        if isinstance(value, dict) and sum(1 for item in value.values() if evidence_text(item).strip()) >= 2:
            return True
        if isinstance(value, str):
            if len(OPTION_LINE_RE.findall(value)) >= 2 or len(OPTION_WORD_RE.findall(value)) >= 2:
                return True
    prompt_text = evidence_text(
        [
            entry.get("question_text"),
            entry.get("prompt"),
            entry.get("instruction"),
            entry.get("context"),
        ]
    )
    return len(OPTION_LINE_RE.findall(prompt_text)) >= 2 or len(OPTION_WORD_RE.findall(prompt_text)) >= 2


def answer_is_option_reference_only(answer: str) -> bool:
    return OPTION_ONLY_RE.fullmatch(answer) is not None


def answer_requires_worked_steps(entry: JsonObject, marks: float | None) -> bool:
    if marks is not None and marks >= HIGH_MARK_THRESHOLD:
        return True
    prompt_text = evidence_text(
        [
            entry.get("question_text"),
            entry.get("prompt"),
            entry.get("instruction"),
            entry.get("context"),
        ]
    )
    return any(term in prompt_text for term in WORKED_PROMPT_TERMS)


def answer_has_worked_steps(answer: str) -> bool:
    answer_lower = answer.casefold()
    marker_count = sum(answer_lower.count(marker) for marker in WORKED_STEP_MARKERS)
    marker_count += len(NUMBERED_STEP_RE.findall(answer))
    return marker_count >= 2


def answer_has_exam_structure(entry: JsonObject, marks: float | None) -> bool:
    answer = text_field(entry, "answer") or ""
    explanation = text_field(entry, "student_explanation") or ""
    question_type = normalized(text_field(entry, "question_type"))
    answer_lower = answer.casefold()
    answer_tokens = normalized_tokens(answer)
    explanation_tokens = normalized_tokens(explanation)
    marks = effective_mark(entry, marks)
    requires_worked_steps = answer_requires_worked_steps(entry, marks)
    match question_type:
        case "coding" | "code" | "pseudocode" | "algorithm":
            return any(marker in answer_lower for marker in CODING_MARKERS)
        case "trace" | "tracing":
            if not any(marker in answer_lower for marker in TRACE_MARKERS):
                return False
            return not requires_worked_steps or answer_has_worked_steps(answer)
        case "structured" | "essay" | "long_answer" | "long answer":
            if len(answer_tokens) < 6 or not any(marker in answer_lower for marker in REASONING_MARKERS):
                return False
            return not requires_worked_steps or answer_has_worked_steps(answer)
        case "objective" | "mcq" | "multiple_choice" | "multiple choice":
            if answer_is_option_reference_only(answer) and not entry_has_choice_payload(entry):
                return False
            return bool(answer_tokens) and len(explanation_tokens) >= 4
        case "definition" | "short_answer" | "short answer":
            return bool(answer_tokens) and (marks is not None and marks <= 2 or len(answer_tokens) >= 6)
        case "true_false" | "true/false" | "boolean":
            return bool(answer_tokens) and len(explanation_tokens) >= 3
        case "":
            return bool(answer_tokens)
        case _:
            if requires_worked_steps:
                return len(answer_tokens) >= 6 and answer_has_worked_steps(answer)
            return bool(answer_tokens)


def add_learner_answer_issues(data: ProofData, issues: list[Issue]) -> None:
    html_path = learner_html_path(data)
    html_label = str(html_path.relative_to(data.proof_dir)) if html_path is not None else ""
    rendered_text = learner_text(html_path) if html_path is not None else None
    if rendered_text is not None and question_text_is_placeholder(rendered_text):
        issues.append(
            Issue(
                IssueCode.PLACEHOLDER_QUESTION_TEXT,
                html_label,
                "learner HTML renders a compacted worker-report placeholder instead of source question text",
            )
        )
    marks_by_id = marks_by_question_id(data.question_inventory)
    for entry in ledger_entries(data.answer_ledger):
        status = normalized(text_field(entry, "status"))
        if status not in ANSWERED_STATUSES:
            continue
        question_id = text_field(entry, "question_id") or "<unknown question>"
        answer = text_field(entry, "answer")
        if answer is None:
            issues.append(
                Issue(
                    IssueCode.MODEL_ANSWER_LACKS_EXAM_STRUCTURE,
                    "answer-ledger.json",
                    f"{question_id} is answered but has no model answer text",
                )
            )
            continue
        if not answer_has_exam_structure(entry, marks_by_id.get(question_id)):
            issues.append(
                Issue(
                    IssueCode.MODEL_ANSWER_LACKS_EXAM_STRUCTURE,
                    "answer-ledger.json",
                    f"{question_id} model answer lacks question-type-specific exam structure",
                )
            )
        if rendered_text is not None and not answer_coverage_is_visible(rendered_text, answer):
            issues.append(
                Issue(
                    IssueCode.HTML_DROPS_MODEL_ANSWER,
                    html_label,
                    f"{question_id} learner HTML does not render the ledger model answer",
                )
            )
