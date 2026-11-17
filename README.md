# claude-statusline

A compact status line for [Claude Code](https://claude.com/claude-code) that shows the model, context window usage and your 5-hour / 7-day usage limits with time until reset.

```
Opus 5.5:high · ctx 42.5% (85k/200k) · 5h 73% resets 2h04m · 7d 18%
```

- **Model and effort level**, plus `fast` when fast mode is on
- **Context window**: percent used and tokens used / window size
- **5h limit**: percent used and a countdown to the reset
- **7d limit**: percent used
- Percentages are colored green (<70%), amber (70–89%) and red (90%+)
- Warm truecolor palette (gold / amber / cream / brown)

Before the first response of a session, Claude Code doesn't send usage limits to the status line yet. The script then falls back to the cached values in `~/.claude.json`, marks them with `~` (`~5h`, `~7d`), and adds `(stale)` if they're more than an hour old.

## Requirements

- Python 3.9+ (standard library only)
- A terminal with truecolor support (kitty, alacritty, foot, wezterm, ...)

## Install

```sh
git clone https://github.com/Maksasj/claude-statusline.git
cp claude-statusline/statusline.py ~/.claude/statusline.py
```

Then add this to `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/statusline.py",
    "padding": 0
  }
}
```

Restart Claude Code, or start a new session, to see it.

## Customizing colors

The colors are hex values at the top of `statusline.py`:

```python
GOLD  = rgb("#ffbf10")   # model name
AMBER = rgb("#e8892b")   # effort level, warning percentages
MUTED = rgb("#8a6a4a")   # labels and separators
GREEN = rgb("#a6c48a")   # percentages under 70%
RED   = rgb("#e5533d")   # percentages at 90% and above
```

## Testing

Pipe sample JSON in to preview it without Claude Code:

```sh
echo '{"model":{"display_name":"Opus 5.5"},"effort":{"level":"high"},
"context_window":{"used_percentage":42.5,"context_window_size":200000,
"total_input_tokens":80000,"total_output_tokens":5000},
"rate_limits":{"five_hour":{"used_percentage":73,"resets_at":'"$(($(date +%s)+7500))"'},
"seven_day":{"used_percentage":18}}}' | python3 statusline.py; echo
```

## Credits

Layout based on [AlexShukel/claude-config](https://github.com/AlexShukel/claude-config)'s `statusline.sh`, rewritten in Python without Node.
