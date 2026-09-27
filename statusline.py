#!/usr/bin/env python3
"""Claude Code status line: model · effort · context · 5h usage + reset · weekly usage + reset."""
import json
import os
import sys
from datetime import datetime, timezone

RESET = "\033[0m"
DIM = "\033[2m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"


def pct_color(p):
    if p >= 80:
        return RED
    if p >= 50:
        return YELLOW
    return GREEN


def parse_time(v):
    """resets_at may be epoch seconds or an ISO 8601 string."""
    if v is None:
        return None
    try:
        if isinstance(v, (int, float)) or str(v).isdigit():
            return datetime.fromtimestamp(float(v), tz=timezone.utc)
        return datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except (ValueError, OSError):
        return None


def fmt_reset(v):
    t = parse_time(v)
    if t is None:
        return "--"
    secs = int((t - datetime.now(timezone.utc)).total_seconds())
    if secs <= 0:
        left = "now"
    else:
        d, rem = divmod(secs, 86400)
        h, rem = divmod(rem, 3600)
        m = rem // 60
        left = f"{d}d{h}h" if d else (f"{h}h{m:02d}m" if h else f"{m}m")
    return left


BAR_WIDTH = 8
EIGHTHS = " ▏▎▍▌▋▊▉█"


def bar(p):
    """Bar with 1/8-cell resolution (8 sub-steps per cell)."""
    steps = round(max(0.0, min(100.0, p)) / 100 * BAR_WIDTH * 8)
    full, part = divmod(steps, 8)
    s = "█" * full
    if full < BAR_WIDTH:
        s += EIGHTHS[part] + " " * (BAR_WIDTH - full - 1)
    return f"{DIM}▕{RESET}{pct_color(p)}{s}{RESET}{DIM}▏{RESET}"


def limit_segment(label, entry):
    if not entry:
        return f"{label} {DIM}--{RESET}"
    p = entry.get("used_percentage")
    ptxt = f"{bar(p)} {pct_color(p)}{p:.0f}%{RESET}" if isinstance(p, (int, float)) else "--"
    return f"{label} {ptxt} {DIM}↻ {fmt_reset(entry.get('resets_at'))}{RESET}"


def fmt_tokens(n):
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}".rstrip("0").rstrip(".") + "M"
    if n >= 1000:
        return f"{n / 1000:.1f}".rstrip("0").rstrip(".") + "k"
    return str(n)


def env_int(name):
    try:
        v = int(float(os.environ.get(name, "")))
        return v if v > 0 else None
    except ValueError:
        return None


def autocompact_enabled():
    if os.environ.get("DISABLE_AUTO_COMPACT") or os.environ.get("DISABLE_COMPACT"):
        return False
    try:
        with open(os.path.expanduser("~/.claude/settings.json")) as f:
            return json.load(f).get("autoCompactEnabled", True) is not False
    except (OSError, ValueError):
        return True


def autocompact_threshold(window):
    """Mirrors Claude Code's formula: window - min(max_output, 20k) reserve - 13k buffer."""
    cap = env_int("CLAUDE_CODE_AUTO_COMPACT_WINDOW")
    if cap:
        window = min(window, cap)
    reserve = min(env_int("CLAUDE_CODE_MAX_OUTPUT_TOKENS") or 20000, 20000)
    effective = window - reserve
    threshold = effective - 13000
    try:
        pct = float(os.environ.get("CLAUDE_AUTOCOMPACT_PCT_OVERRIDE", ""))
        if 0 < pct <= 100:
            threshold = min(int(effective * pct / 100), threshold)
    except ValueError:
        pass
    return threshold


def context_segment(cw):
    size = cw.get("context_window_size")
    if not isinstance(size, int) or size <= 0:
        return f"ctx {DIM}--{RESET}"
    u = cw.get("current_usage") or {}
    used = sum(u.get(k) or 0 for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
    if autocompact_enabled():
        limit = autocompact_threshold(size)
        limit_txt = fmt_tokens(limit)
    else:
        limit, limit_txt = size, "off"
    color = pct_color(used / limit * 100) if limit > 0 else ""
    return f"ctx {color}{fmt_tokens(used)}{RESET}/{limit_txt}{DIM}({fmt_tokens(size)}){RESET}"


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    model = (data.get("model") or {}).get("display_name") or "?"
    effort = (data.get("effort") or {}).get("level")
    if not effort:
        effort = "thinking off" if (data.get("thinking") or {}).get("enabled") is False else "default"

    rl = data.get("rate_limits") or {}
    sep = f" {DIM}·{RESET} "
    parts = [
        f"{CYAN}{model}{RESET}",
        f"{MAGENTA}⚡{effort}{RESET}",
        context_segment(data.get("context_window") or {}),
        limit_segment("5h", rl.get("five_hour")),
        limit_segment("week", rl.get("seven_day")),
    ]
    print(sep.join(parts))


if __name__ == "__main__":
    main()
