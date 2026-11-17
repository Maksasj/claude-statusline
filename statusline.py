#!/usr/bin/env python3
"""Claude Code status line: model/effort · context window · 5h and 7d usage limits.

Reads the status line JSON from stdin. Warm palette to match kitty/waybar/wofi.
Based on the layout of AlexShukel/claude-config's statusline.sh, rewritten
without Node.
"""
import json
import os
import sys
import time


def rgb(hex_color):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return f"\033[38;2;{r};{g};{b}m"


GOLD = rgb("#ffbf10")
AMBER = rgb("#e8892b")
CREAM = rgb("#f5e6d3")
MUTED = rgb("#8a6a4a")
GREEN = rgb("#a6c48a")
RED = rgb("#e5533d")
RESET = "\033[0m"
SEP = f"{MUTED} · {RESET}"


def num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def pct_color(p):
    if p >= 90:
        return RED
    if p >= 70:
        return AMBER
    return GREEN


def fmt_pct(p):
    return f"{round(p, 1):g}%"


def human(n):
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1000:
        return f"{n // 1000}k"
    return str(n)


def epoch(v):
    """resets_at may be epoch seconds or an ISO timestamp."""
    if num(v):
        return float(v)
    if isinstance(v, str):
        from datetime import datetime
        try:
            return datetime.fromisoformat(v.replace("Z", "+00:00")).timestamp()
        except ValueError:
            return None
    return None


def time_left(target):
    if target is None:
        return ""
    diff = int(target - time.time())
    if diff <= 0:
        return "now"
    h, m = diff // 3600, (diff % 3600) // 60
    if h:
        return f"{h}h{m:02d}m"
    return f"{m}m" if m else "<1m"


try:
    data = json.load(sys.stdin)
except (json.JSONDecodeError, ValueError):
    data = {}

parts = []

# Model + effort (+ fast mode)
model = (data.get("model") or {}).get("display_name") or "?"
seg = f"{GOLD}{model}{RESET}"
effort = (data.get("effort") or {}).get("level")
if effort:
    seg += f"{MUTED}:{RESET}{AMBER}{effort}{RESET}"
if data.get("fast_mode") is True:
    seg += f" {GOLD}fast{RESET}"
parts.append(seg)

# Context window
cw = data.get("context_window") or {}
used, size = cw.get("used_percentage"), cw.get("context_window_size")
if num(used) and num(size):
    tokens = sum(cw.get(k, 0) for k in ("total_input_tokens", "total_output_tokens") if num(cw.get(k)))
    parts.append(
        f"{MUTED}ctx{RESET} {pct_color(used)}{fmt_pct(used)}{RESET} "
        f"{MUTED}({human(tokens)}/{human(size)}){RESET}"
    )

# Usage limits: live from stdin; before the first response, fall back to the
# snapshot in ~/.claude.json and mark it with ~ (and "stale" if over an hour old).
five = seven = None
mark = stale = ""
rl = data.get("rate_limits") or {}
if rl.get("five_hour") or rl.get("seven_day"):
    if rl.get("five_hour"):
        five = (rl["five_hour"].get("used_percentage"), rl["five_hour"].get("resets_at"))
    if rl.get("seven_day"):
        seven = (rl["seven_day"].get("used_percentage"), rl["seven_day"].get("resets_at"))
else:
    try:
        with open(os.path.expanduser("~/.claude.json")) as f:
            store = json.load(f).get("cachedUsageUtilization") or {}
        u = store.get("utilization") or {}
        if num((u.get("five_hour") or {}).get("utilization")):
            five = (u["five_hour"]["utilization"], u["five_hour"].get("resets_at"))
        if num((u.get("seven_day") or {}).get("utilization")):
            seven = (u["seven_day"]["utilization"], u["seven_day"].get("resets_at"))
        if five or seven:
            mark = "~"
            fetched = store.get("fetchedAtMs")
            if num(fetched) and time.time() * 1000 - fetched > 3_600_000:
                stale = f" {MUTED}(stale){RESET}"
    except (OSError, ValueError, AttributeError):
        pass

if five and num(five[0]):
    seg = f"{MUTED}{mark}5h{RESET} {pct_color(five[0])}{fmt_pct(five[0])}{RESET}"
    left = time_left(epoch(five[1]))
    if left:
        seg += f" {MUTED}resets {left}{RESET}"
    parts.append(seg)

if seven and num(seven[0]):
    parts.append(f"{MUTED}{mark}7d{RESET} {pct_color(seven[0])}{fmt_pct(seven[0])}{RESET}")

print(SEP.join(parts) + stale, end="")
