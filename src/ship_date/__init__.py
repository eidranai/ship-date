"""Read a vendor's email reply and pull out a new ship date and any delay signals.

Deliberately conservative: when the reply is ambiguous it flags it for a human
instead of guessing.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

from dateutil import parser as dateparser

__all__ = ["ReplyResult", "parse_reply"]
__version__ = "0.1.0"

DELAY_WORDS = re.compile(
    r"\b(delay(ed)?|push(ed)? (out|back)|slip(ped)?|backorder(ed)?|shortage|"
    r"reschedul(e|ed)|revised|new date|moved)\b",
    re.IGNORECASE,
)
SHIPPED_WORDS = re.compile(r"\b(shipped|delivered|in transit|tracking (number|#))\b", re.IGNORECASE)
DATE_CANDIDATE = re.compile(
    r"\b(\d{4}-\d{2}-\d{2}"
    r"|\d{1,2}/\d{1,2}/\d{2,4}"
    r"|(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.? \d{1,2}(,? \d{4})?)\b",
    re.IGNORECASE,
)
MAX_REPLY_CHARS = 20_000


@dataclass
class ReplyResult:
    """What the reply says about the order."""

    new_date: date | None
    delay_mentioned: bool
    shipped: bool
    needs_human: bool
    explanation: str


def parse_reply(text: str, today: date) -> ReplyResult:
    """Parse one vendor reply. `today` is used to ignore past and implausible dates."""
    text = (text or "")[:MAX_REPLY_CHARS]
    found: list[date] = []
    for match in DATE_CANDIDATE.finditer(text):
        try:
            parsed = dateparser.parse(match.group(0), default=dateparser.parse(f"{today.year}-01-01")).date()
        except (ValueError, OverflowError):
            continue
        if parsed.year < today.year - 1 or parsed.year > today.year + 5:
            continue
        found.append(parsed)

    delay = bool(DELAY_WORDS.search(text))
    shipped = bool(SHIPPED_WORDS.search(text))
    future = sorted({d for d in found if d >= today})

    if shipped:
        return ReplyResult(None, delay, True, False, "Vendor reports shipped or in transit")
    if len(future) == 1:
        return ReplyResult(future[0], delay, False, False, f"Ship date stated: {future[0].isoformat()}")
    if len(future) > 1:
        # Several dates usually means old-versus-new; the later one is the revised date
        # when the vendor signals a delay, otherwise ask a human.
        if delay:
            return ReplyResult(future[-1], True, False, False,
                               f"Delay mentioned; revised date taken as {future[-1].isoformat()}")
        return ReplyResult(None, False, False, True, "Several dates in reply; needs review")
    return ReplyResult(None, delay, False, True,
                       "No ship date found" + ("; delay mentioned" if delay else ""))
