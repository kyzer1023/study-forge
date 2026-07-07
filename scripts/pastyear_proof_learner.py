from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
from typing import Final, override

from scripts.pastyear_proof_common import ANSWERED_STATUSES, normalized, question_text_is_placeholder, text_field
from scripts.pastyear_proof_inventory import inventory_subparts, ledger_entries
from scripts.pastyear_proof_model import Issue, IssueCode, JsonObject, JsonValue, ProofData

TOKEN_RE: Final[re.Pattern[str]] = re.compile(r"[a-z0-9]+")
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


def answer_has_exam_structure(entry: JsonObject, marks: float | None) -> bool:
    answer = text_field(entry, "answer") or ""
    explanation = text_field(entry, "student_explanation") or ""
    question_type = normalized(text_field(entry, "question_type"))
    answer_lower = answer.casefold()
    explanation_tokens = normalized_tokens(explanation)
    match question_type:
        case "coding" | "code" | "pseudocode" | "algorithm":
            return any(marker in answer_lower for marker in CODING_MARKERS)
        case "trace" | "tracing":
            return any(marker in answer_lower for marker in TRACE_MARKERS)
        case "structured" | "essay" | "long_answer" | "long answer":
            return len(normalized_tokens(answer)) >= 6 and any(marker in answer_lower for marker in REASONING_MARKERS)
        case "objective" | "mcq" | "multiple_choice" | "multiple choice":
            return bool(normalized_tokens(answer)) and len(explanation_tokens) >= 4
        case "definition" | "short_answer" | "short answer":
            return bool(normalized_tokens(answer)) and (marks is not None and marks <= 2 or len(normalized_tokens(answer)) >= 6)
        case "true_false" | "true/false" | "boolean":
            return bool(normalized_tokens(answer)) and len(explanation_tokens) >= 3
        case "":
            return bool(normalized_tokens(answer))
        case _:
            return bool(normalized_tokens(answer))


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
