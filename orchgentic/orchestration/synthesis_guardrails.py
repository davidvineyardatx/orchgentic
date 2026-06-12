"""Team synthesis quality guardrails.

These helpers keep team finalization grounded in the current team's work and
prevent common synthetic artifacts such as placeholder links/resources.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Iterable

PLACEHOLDER_PATTERNS = [
    re.compile(r"\[[^\]]*link[^\]]*\]", re.IGNORECASE),
    re.compile(r"\bplaceholder\b", re.IGNORECASE),
    re.compile(r"\bTBD\b", re.IGNORECASE),
    re.compile(r"\bTODO\b", re.IGNORECASE),
]

INTERNAL_SYNTHESIS_NOTE_PATTERNS = [
    re.compile(r"^\s*note\s*:\s*.*\b(writer|reviewer|draft|team outputs?|current outputs?|synthesis)\b", re.IGNORECASE),
    re.compile(r"\bwhile the writer'?s draft mentioned\b", re.IGNORECASE),
    re.compile(r"\bnot available in the current team outputs\b", re.IGNORECASE),
    re.compile(r"\binternal (?:team|reviewer|synthesis)\b", re.IGNORECASE),
]

SOURCE_VERIFICATION_PATTERNS = [
    # Bounded phrase rewrites. These avoid matching across sentences or
    # unrelated parentheticals such as AR/VR.
    re.compile(r"\baccording to\s+(?:a|an|the)?\s*(?:survey|study|report|research)?\s*(?:by|from)\s+([A-Z][A-Za-z& .-]{1,60}?)(?=\s*(?:\([^)]*\))?[,.;])", re.IGNORECASE),
    re.compile(r"\bas found by\s+(?:a|an|the)?\s*(?:survey|study|report|research)?\s*(?:by|from)?\s+([A-Z][A-Za-z& .-]{1,60}?)(?=\s*(?:\([^)]*\))?[,.;])", re.IGNORECASE),
    re.compile(r"\bas reported by\s+([A-Z][A-Za-z& .-]{1,60}?)(?=\s*(?:\([^)]*\))?[,.;])", re.IGNORECASE),
    re.compile(r"\bas cited by\s+([A-Z][A-Za-z& .-]{1,60}?)(?=\s*(?:\([^)]*\))?[,.;])", re.IGNORECASE),
]

SOURCE_LEADING_CLAIM_PATTERNS = [
    re.compile(r"\bA\s+(?:survey|study|report|research)\s+by\s+([A-Z][A-Za-z& .-]{1,60}?)\s+found\s+that\b", re.IGNORECASE),
    re.compile(r"\bA\s+(?:survey|study|report|research)\s+from\s+([A-Z][A-Za-z& .-]{1,60}?)\s+found\s+that\b", re.IGNORECASE),
]


GENERIC_RESOURCE_TITLES = [
    "AI in Retail Report",
    "AI-powered Customer Shopping Webinar",
    "AI Ethics Guidelines",
]


DEBUG_SECTION_HEADERS = {"RUN ID", "MEMORY", "KNOWLEDGE", "PLAN", "TOOLS", "ANSWER", "REFLECTION"}


def _unwrap_structured_final(text: str) -> str:
    """Extract the user-facing answer from structured final JSON when present.

    Some agents return OpenAI-style structured text such as
    {"action":"final","answer":"..."}. Team handoffs and final rendering
    should use the answer value, not the raw JSON envelope.
    """
    candidate = (text or "").strip()
    if not candidate:
        return ""

    # Handle fenced JSON defensively.
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        if len(lines) >= 3 and lines[0].strip().startswith("```") and lines[-1].strip() == "```":
            candidate = "\n".join(lines[1:-1]).strip()

    try:
        parsed = json.loads(candidate)
    except Exception:
        return text.strip()

    if isinstance(parsed, dict):
        answer = parsed.get("answer")
        if isinstance(answer, str) and answer.strip():
            return answer.strip()

    return text.strip()


def extract_answer_for_handoff(output: str) -> str:
    """Return only the agent's answer from a debug transcript or raw output.

    Team members may be run with debug=True during CLI diagnostics. Passing the
    whole debug transcript to the next agent balloons token usage and recursively
    nests RUN ID / PLAN / REFLECTION blocks. This helper keeps team handoffs
    compact by forwarding only the ANSWER block. It also unwraps structured
    final JSON envelopes so downstream agents see plain answer text.
    """
    text = (output or "").strip()
    if not text:
        return ""

    lines = text.splitlines()
    answer_start = None
    for idx, line in enumerate(lines):
        if line.strip() == "ANSWER":
            answer_start = idx + 1

    if answer_start is None:
        return _unwrap_structured_final(text)

    collected: list[str] = []
    for line in lines[answer_start:]:
        if line.strip() in DEBUG_SECTION_HEADERS - {"ANSWER"}:
            break
        collected.append(line)

    answer = "\n".join(collected).strip()
    return _unwrap_structured_final(answer or text)

def format_team_outputs_for_prompt(messages: Iterable[dict]) -> str:
    """Render compact current-run team outputs for member/synthesis prompts."""
    lines: list[str] = []
    for message in messages:
        sender = message.get("sender", "agent")
        recipient = message.get("recipient", "team")
        content = extract_answer_for_handoff(str(message.get("content", ""))).strip()
        if not content:
            continue
        lines.append(f"{sender} -> {recipient}: {content}")
    return "\n".join(lines)


@dataclass(slots=True)
class SynthesisQualityResult:
    answer: str
    removed_placeholder_sections: bool = False
    removed_placeholder_lines: int = 0
    notes: list[str] | None = None

    def to_dict(self) -> dict:
        return {
            "removed_placeholder_sections": self.removed_placeholder_sections,
            "removed_placeholder_lines": self.removed_placeholder_lines,
            "notes": self.notes or [],
        }


def build_synthesis_task(team_task: str, team_outputs: str) -> str:
    """Build a stricter synthesis prompt for final team responses."""
    return (
        "Create a final team response for this task:\n"
        f"{team_task}\n\n"
        "Team outputs from this run:\n"
        f"{team_outputs}\n\n"
        "Synthesis requirements:\n"
        "1. Use the current team outputs above as the primary source of truth.\n"
        "2. Do not rely on unrelated prior memory or prior team runs.\n"
        "3. Apply reviewer feedback when it improves the final answer.\n"
        "4. Do not invent citations, reports, links, webinars, ebooks, examples, company names, or additional resources.\n"
        "5. Do not include placeholder links such as [link to article or resource].\n"
        "6. If statistics are included, keep only statistics already present in the current team outputs and preserve any source labels provided there.\n"
        "7. Treat source labels without URLs as source labels, not verified citations. Do not claim citation verification unless a URL or retrieved document is present.\n"
        "8. If reviewer feedback asks for examples or sources that are not present in current outputs, omit those additions instead of explaining the internal limitation.\n"
        "9. Do not include internal reviewer notes, synthesis notes, or comments about what the Writer/Reviewer requested.\n"
        "10. Return only the final polished response as plain text, not JSON and not internal team process notes.\n"
        "11. When source labels are present without URLs, prefer phrasing such as: The team's source-labeled research cites X for..."
    )


def build_member_task(team_task: str, shared_context: str, member: str) -> str:
    """Build a role-specific contribution prompt with quality constraints."""
    lower_member = member.lower()
    base = (
        f"Team task: {team_task}\n\n"
        f"Shared context from this run only:\n{shared_context}\n\n"
        f"Provide your specialist contribution as {member}.\n"
    )
    if "research" in lower_member:
        return base + (
            "Research contribution requirements:\n"
            "- Provide actual findings, trends, data points, and implications.\n"
            "- Do not merely say that research has been completed.\n"
            "- If you include statistics, include the source label when available.\n"
            "- Do not invent URLs or placeholder resources.\n"
        )
    if "writer" in lower_member:
        return base + (
            "Writer contribution requirements:\n"
            "- Draft the requested deliverable using the current research.\n"
            "- Do not add placeholder links or fake resources.\n"
            "- Preserve source labels for statistics when present.\n"
        )
    if "review" in lower_member:
        return base + (
            "Reviewer contribution requirements:\n"
            "- Review for accuracy, clarity, strategic relevance, and unsupported claims.\n"
            "- Flag placeholder links/resources, invented citations, or unsupported statistics.\n"
            "- Give concrete revision instructions the final synthesis can apply.\n"
        )
    return base + (
        "Contribution requirements:\n"
        "- Stay grounded in this team's current task and shared context.\n"
        "- Do not add placeholder links or fake resources.\n"
    )


def has_placeholder(text: str) -> bool:
    return any(pattern.search(text or "") for pattern in PLACEHOLDER_PATTERNS)


def _is_heading(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("#") or stripped.endswith(":")


def _looks_like_additional_resources_heading(line: str) -> bool:
    stripped = line.strip().lower().strip("# ")
    return stripped in {
        "additional resources",
        "resources",
        "further reading",
        "references",
    }


def _line_has_real_url(line: str) -> bool:
    return "http://" in line.lower() or "https://" in line.lower()


def _has_real_url(text: str) -> bool:
    return "http://" in (text or "").lower() or "https://" in (text or "").lower()


def _is_internal_synthesis_note(line: str) -> bool:
    return any(pattern.search(line or "") for pattern in INTERNAL_SYNTHESIS_NOTE_PATTERNS)


def _clean_source_label(label: str) -> str:
    label = (label or "").strip(" ,.;")
    # Drop trailing generic words accidentally captured by permissive regexes.
    label = re.sub(r"\s+(found|reported|said|shows?)$", "", label, flags=re.IGNORECASE).strip()
    return label


def _soften_unverified_source_phrasing(text: str) -> tuple[str, int]:
    """Avoid implying source verification when only source labels are present.

    Team members often produce labels like ``(Oracle, 2020)`` without a URL or
    retrieved source document. The final synthesis may preserve those labels,
    but should not describe them as verified surveys/studies/reports. Rewrites
    are deliberately local and bounded so they do not splice unrelated clauses.
    """
    if not text or _has_real_url(text):
        return text, 0

    replacements = 0
    cleaned = text

    def leading_repl(match: re.Match) -> str:
        nonlocal replacements
        replacements += 1
        label = _clean_source_label(match.group(1))
        return f"The team's source-labeled research cites {label} for the finding that"

    for pattern in SOURCE_LEADING_CLAIM_PATTERNS:
        cleaned = pattern.sub(leading_repl, cleaned)

    def inline_repl(match: re.Match) -> str:
        nonlocal replacements
        replacements += 1
        label = _clean_source_label(match.group(1))
        return f"with a source label of {label}"

    for pattern in SOURCE_VERIFICATION_PATTERNS:
        cleaned = pattern.sub(inline_repl, cleaned)

    return cleaned, replacements


def sanitize_final_answer(answer: str) -> SynthesisQualityResult:
    """Remove placeholder sections/lines from a final team synthesis answer.

    This is intentionally conservative: it removes obvious placeholder links and
    generic resource sections without real URLs. It does not try to fact-check
    content; it prevents known bad artifacts from leaving the synthesis stage.
    """
    if not answer:
        return SynthesisQualityResult(answer="", notes=["empty_answer"])

    lines = answer.splitlines()
    output: list[str] = []
    removed_lines = 0
    removed_sections = False
    skip_resource_section = False

    for idx, line in enumerate(lines):
        if _looks_like_additional_resources_heading(line):
            # Drop generic resource sections unless they contain real URLs before
            # the next heading. This prevents fabricated resource placeholders.
            section_lines = []
            for following in lines[idx + 1 :]:
                if _is_heading(following) and following.strip():
                    break
                section_lines.append(following)
            if not any(_line_has_real_url(section_line) for section_line in section_lines):
                skip_resource_section = True
                removed_sections = True
                removed_lines += 1
                continue

        if skip_resource_section:
            if _is_heading(line) and line.strip():
                skip_resource_section = False
            else:
                removed_lines += 1
                continue

        if has_placeholder(line):
            removed_lines += 1
            continue

        if _is_internal_synthesis_note(line):
            removed_lines += 1
            continue

        if any(title.lower() in line.lower() for title in GENERIC_RESOURCE_TITLES) and not _line_has_real_url(line):
            removed_lines += 1
            continue

        output.append(line)

    cleaned = "\n".join(output).strip()
    cleaned, softened_source_phrases = _soften_unverified_source_phrasing(cleaned)
    notes = []
    if removed_sections:
        notes.append("removed_placeholder_resource_section")
    if removed_lines:
        notes.append("removed_placeholder_or_internal_lines")
    if softened_source_phrases:
        notes.append("softened_unverified_source_phrasing")
    return SynthesisQualityResult(
        answer=cleaned,
        removed_placeholder_sections=removed_sections,
        removed_placeholder_lines=removed_lines,
        notes=notes,
    )
