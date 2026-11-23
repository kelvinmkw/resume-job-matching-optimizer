"""Conservative validator for a single proposed resume-sentence edit.

A successful heuristic check means only accepted_pending_manual_review. The
caller must show the source and full resume to a human reviewer.
"""
from collections import Counter
import json
import re
from dataclasses import dataclass

TOKEN = re.compile(r"[A-Za-z0-9]+(?:[+#./'-][A-Za-z0-9+#./'-]*)?")
FUNCTION_WORDS = set("a an the i me my am is are be been to in of for with on by at as that this these those where which along while into within currently it its".split())
ALIASES = {"seeking": "looking", "looking": "looking"}
LOGIC = {"no", "not", "never", "without", "and", "or", "only", "must", "can", "will", "may"}

@dataclass
class EditAssessment:
    status: str
    original_text: str
    draft_text: str | None
    effective_text: str
    violations: list[str]


def tokens(text):
    return [match.group().rstrip(".").casefold() for match in TOKEN.finditer(text)]

def _content_counts(text):
    return Counter(ALIASES.get(word, word) for word in tokens(text) if word not in FUNCTION_WORDS)

def validate_edit(original_resume, start, end, payload):
    """Validate a JSON-like {source,replacement,evidence_quote} edit proposal.

    `start:end` is an explicit character span in original_resume. No automatic
    parser or model is trusted to choose this span. Invalid proposals retain the
    exact original text as effective_text; drafts are returned for inspection.
    """
    if not isinstance(original_resume, str) or not isinstance(start, int) or not isinstance(end, int):
        raise TypeError("resume must be text and span offsets must be integers")
    if not 0 <= start < end <= len(original_resume):
        raise ValueError("invalid source span")
    source = original_resume[start:end]
    if not isinstance(payload, dict) or set(payload) != {"source", "replacement", "evidence_quote"} or not all(isinstance(v, str) for v in payload.values()):
        return EditAssessment("rejected_response", original_resume, None, original_resume, ["invalid_response_schema"])
    replacement = payload["replacement"]
    draft = original_resume[:start] + replacement + original_resume[end:]
    flags = []
    if payload["source"] != source or payload["evidence_quote"] != source:
        flags.append("source_or_evidence_mismatch")
    if not replacement.strip() or replacement != replacement.strip() or "\n" in replacement:
        flags.append("invalid_replacement_shape")
    if re.search(r"[.!?]\s+[A-Z]", replacement.rstrip(".!?")):
        flags.append("multiple_sentences")
    if _content_counts(source) != _content_counts(replacement):
        flags.append("content_words_changed")
    if re.findall(r"\d[\d.,%/-]*", source) != re.findall(r"\d[\d.,%/-]*", replacement):
        flags.append("numeric_claim_changed")
    if Counter(word for word in tokens(source) if word in LOGIC) != Counter(word for word in tokens(replacement) if word in LOGIC):
        flags.append("logical_qualifiers_changed")
    if flags:
        return EditAssessment("rejected", original_resume, draft, original_resume, list(dict.fromkeys(flags)))
    status = "unchanged" if replacement == source else "accepted_pending_manual_review"
    return EditAssessment(status, original_resume, draft, draft, [])


def validate_json(raw_response, original_resume, start, end):
    """Parse strict JSON, then apply the same conservative checks."""
    try:
        payload = json.loads(raw_response)
    except (json.JSONDecodeError, TypeError):
        return EditAssessment("rejected_response", original_resume, None, original_resume, ["invalid_json"])
    return validate_edit(original_resume, start, end, payload)
