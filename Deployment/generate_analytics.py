#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

LOG_CANDIDATES = [
    Path("/var/log/nginx/machinaos.access.log"),
    Path("/var/log/nginx/access.log"),
]
OUTPUT_PATH = Path("/var/www/machinaos/private-analytics/summary.json")
WINDOW_DAYS = 30
SESSION_WINDOW_MINUTES = 30
SITE_HOSTS = {"machinaos.ai", "www.machinaos.ai"}
EXCLUDED_PREFIXES = ("/private-analytics/", "/ops-console-8c7f43d1.html")
STATIC_EXTENSIONS = {
    ".css", ".js", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".ico", ".woff", ".woff2", ".ttf", ".map", ".json",
}
BOT_RE = re.compile(
    r"bot|spider|crawl|slurp|preview|scanner|monitor|headless|facebookexternalhit|whatsapp|telegrambot|discordbot|linkedinbot|applebot|"
    r"bingbot|googlebot|adsbot|duckduckbot|yandex|ahrefs|semrush|petalbot|bytespider|claudebot|gptbot|perplexitybot|curl|wget|python-requests|go-http-client",
    re.IGNORECASE,
)
LOG_RE = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] "(?P<method>[A-Z]+) (?P<path>[^ ]+) (?P<protocol>[^"]+)" (?P<status>\d{3}) (?P<size>\S+) "(?P<referrer>[^"]*)" "(?P<ua>[^"]*)"'
)


@dataclass
class RequestEntry:
    ip: str
    timestamp: datetime
    method: str
    path: str
    status: int
    referrer: str
    user_agent: str
    is_bot: bool
    is_pageview: bool


def pick_log() -> tuple[Path, str | None]:
    for candidate in LOG_CANDIDATES:
        if candidate.exists():
            if candidate.name != "machinaos.access.log":
                return candidate, "Dedicated MachinaOS log not found yet. Data currently falls back to the shared nginx access log and may include partial noise until the dedicated log fills."
            return candidate, None
    raise FileNotFoundError("No nginx access log found.")


def parse_time(raw: str) -> datetime:
    return datetime.strptime(raw, "%d/%b/%Y:%H:%M:%S %z")


def normalize_path(raw_path: str) -> str:
    parsed = urlparse(raw_path)
    path = parsed.path or "/"
    if path == "/index.html":
        return "/"
    return path


def is_pageview_path(path: str) -> bool:
    lowered = path.lower()
    if lowered.startswith(EXCLUDED_PREFIXES):
        return False
    suffix = Path(lowered).suffix
    if suffix in STATIC_EXTENSIONS:
        return False
    return True


def is_internal_referrer(referrer: str) -> bool:
    if not referrer or referrer == "-":
        return False
    parsed = urlparse(referrer)
    return parsed.netloc in SITE_HOSTS


def mask_ip(ip: str) -> str:
    if ":" in ip:
        parts = ip.split(":")
        return ":".join(parts[:3]) + ":*"
    parts = ip.split(".")
    if len(parts) == 4:
        return ".".join(parts[:3]) + ".x"
    return ip


def classify_agent(user_agent: str) -> bool:
    return bool(BOT_RE.search(user_agent or ""))


def parse_log(lines: Iterable[str]) -> list[RequestEntry]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=WINDOW_DAYS)
    entries: list[RequestEntry] = []

    for line in lines:
        match = LOG_RE.match(line.strip())
        if not match:
            continue

        timestamp = parse_time(match.group("time"))
        if timestamp < cutoff:
            continue

        path = normalize_path(match.group("path"))
        if path.startswith(EXCLUDED_PREFIXES):
            continue

        user_agent = match.group("ua")
        entry = RequestEntry(
            ip=match.group("ip"),
            timestamp=timestamp,
            method=match.group("method"),
            path=path,
            status=int(match.group("status")),
            referrer=match.group("referrer"),
            user_agent=user_agent,
            is_bot=classify_agent(user_agent),
            is_pageview=match.group("method") == "GET" and is_pageview_path(path),
        )
        entries.append(entry)

    return entries


def count_sessions(entries: list[RequestEntry]) -> dict[str, int]:
    grouped: dict[tuple[str, str, bool], list[datetime]] = defaultdict(list)
    for entry in entries:
        if not entry.is_pageview:
            continue
        grouped[(entry.ip, entry.user_agent, entry.is_bot)].append(entry.timestamp)

    counts = {"all": 0, "human": 0, "bot": 0}
    session_gap = timedelta(minutes=SESSION_WINDOW_MINUTES)

    for (_, _, is_bot), times in grouped.items():
        times.sort()
        previous = None
        for current in times:
            if previous is None or current - previous > session_gap:
                counts["all"] += 1
                counts["bot" if is_bot else "human"] += 1
            previous = current

    return counts


def build_summary(entries: list[RequestEntry], note: str | None, log_source: str) -> dict:
    pageviews = [entry for entry in entries if entry.is_pageview]
    humans = [entry for entry in entries if not entry.is_bot]
    bots = [entry for entry in entries if entry.is_bot]
    human_pageviews = [entry for entry in pageviews if not entry.is_bot]
    bot_pageviews = [entry for entry in pageviews if entry.is_bot]

    totals = {
        "requests": {"all": len(entries), "human": len(humans), "bot": len(bots)},
        "pageviews": {"all": len(pageviews), "human": len(human_pageviews), "bot": len(bot_pageviews)},
        "unique_visitors": {
            "all": len({entry.ip for entry in pageviews}),
            "human": len({entry.ip for entry in human_pageviews}),
            "bot": len({entry.ip for entry in bot_pageviews}),
        },
        "visits": count_sessions(entries),
    }

    top_pages = Counter(entry.path for entry in human_pageviews).most_common(12)
    top_referrers = Counter(
        urlparse(entry.referrer).netloc or entry.referrer
        for entry in human_pageviews
        if entry.referrer not in {"", "-"} and not is_internal_referrer(entry.referrer)
    ).most_common(12)
    status_codes = Counter(str(entry.status) for entry in entries).most_common()
    bot_agents = Counter(entry.user_agent.strip() or "Unknown bot" for entry in bots).most_common(12)

    today = datetime.now(timezone.utc).date()
    daily_map: dict[str, dict[str, int]] = {}
    for offset in range(13, -1, -1):
        day = today - timedelta(days=offset)
        daily_map[day.isoformat()] = {"human_pageviews": 0, "bot_pageviews": 0}

    for entry in pageviews:
        day_key = entry.timestamp.date().isoformat()
        if day_key not in daily_map:
            continue
        bucket_key = "bot_pageviews" if entry.is_bot else "human_pageviews"
        daily_map[day_key][bucket_key] += 1

    daily = [
        {
            "day": datetime.fromisoformat(day_key).strftime("%b %d"),
            "human_pageviews": values["human_pageviews"],
            "bot_pageviews": values["bot_pageviews"],
        }
        for day_key, values in daily_map.items()
    ]

    recent_human_activity = [
        {
            "time": entry.timestamp.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "path": entry.path,
            "ip": mask_ip(entry.ip),
            "referrer": "Direct" if entry.referrer in {"", "-"} else (urlparse(entry.referrer).netloc or entry.referrer),
        }
        for entry in sorted(human_pageviews, key=lambda item: item.timestamp, reverse=True)[:25]
    ]

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "log_source": str(log_source),
        "window_days": WINDOW_DAYS,
        "session_window_minutes": SESSION_WINDOW_MINUTES,
        "note": note,
        "totals": totals,
        "daily": daily,
        "top_pages": [{"path": path, "views": count} for path, count in top_pages],
        "top_referrers": [{"referrer": referrer, "visits": count} for referrer, count in top_referrers],
        "status_codes": [{"status": status, "count": count} for status, count in status_codes],
        "bot_agents": [{"agent": agent[:110], "count": count} for agent, count in bot_agents],
        "recent_human_activity": recent_human_activity,
    }


def main() -> None:
    log_path, note = pick_log()
    entries = parse_log(log_path.read_text(encoding="utf-8", errors="replace").splitlines())
    if log_path.name == "machinaos.access.log" and len(entries) < 10:
        started_at = datetime.fromtimestamp(log_path.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        note = f"Dedicated MachinaOS analytics logging was enabled recently. Reliable per-site totals start from {started_at}."
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    summary = build_summary(entries, note, str(log_path))
    OUTPUT_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    os.chmod(OUTPUT_PATH, 0o644)
    print(f"Wrote analytics to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
