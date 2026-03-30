"""
Strict parsing for job posting dates. Used by scrapers for freshness filters.
Unknown or unparseable dates are treated as not fresh (exclude).
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Optional


def parse_iso_datetime(s: str) -> Optional[datetime]:
    """Parse ISO and common date-only strings from ATS / APIs."""
    if not s or not isinstance(s, str):
        return None
    s = s.strip()
    try:
        if s.endswith("Z"):
            s = s.replace("Z", "+00:00")
        return datetime.fromisoformat(s)
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def parse_relative_posted_at(s: str) -> Optional[datetime]:
    """
    Parse relative strings like '5 hours ago', '2 days ago', 'just now'.
    Returns an approximate UTC-naive datetime (good enough for age_days checks).
    """
    if not s or not isinstance(s, str):
        return None
    low = s.lower().strip()
    if not low:
        return None
    now = datetime.now()

    if "ago" not in low:
        return None

    if any(
        phrase in low
        for phrase in (
            "just now",
            "moments ago",
            "second ago",
            "seconds ago",
            "minute ago",
            "minutes ago",
        )
    ):
        return now

    m = re.match(r"^(\d+)\s+(\S+)", low)
    if m:
        num = int(m.group(1))
        unit = m.group(2)
        if "hour" in unit or unit.startswith("hr"):
            return now - timedelta(hours=num)
        if "day" in unit:
            return now - timedelta(days=num)
        if "week" in unit:
            return now - timedelta(weeks=num)
        if "month" in unit:
            return now - timedelta(days=num * 30)
        if "year" in unit:
            return now - timedelta(days=num * 365)
        return None

    if low.startswith("a ") and "day" in low:
        return now - timedelta(days=1)
    if low.startswith("an ") and "hour" in low:
        return now - timedelta(hours=1)
    return None


def age_days_since_posted(posted: datetime) -> int:
    """Whole calendar days between posted time and now (timezone-safe)."""
    if posted.tzinfo is not None:
        now = datetime.now(posted.tzinfo)
    else:
        now = datetime.now()
    delta = now - posted
    return max(0, delta.days)
