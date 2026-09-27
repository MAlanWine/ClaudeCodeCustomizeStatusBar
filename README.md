# ClaudeCodeCustomizeStatusBar

**English** | [简体中文](README.zh-CN.md)

A custom status line for [Claude Code](https://claude.com/claude-code) that shows the current model, the thinking effort level, context usage, session cost, and your subscription's 5-hour and weekly usage limits, each with a progress bar and a countdown to the next reset.

```
Opus 5.5 · ⚡high · ctx 45.2k/167k(200k) · cost $3.46 · 5h ▕███     ▏ 37% ↻ 2h01m · week ▕██████▌ ▏ 82% ↻ 3d18h
```

## What it shows

| Item | Description |
| --- | --- |
| Model | Name of the current model, e.g. `Opus 5.5` |
| Effort | Current effort level, e.g. `⚡high`; shows `thinking off` when thinking is disabled and `default` when no level is set |
| `ctx` | Context usage as `used/auto-compact threshold(context window size)`, e.g. `45.2k/167k(200k)`. The middle number shows `off` when auto-compact is disabled |
| `cost` | Total cost of the current session in US dollars, e.g. `$3.46`, from Claude Code's `cost.total_cost_usd`. On a Pro or Max subscription this is an estimate at API prices, not money you're actually charged |
| `5h` | 5-hour limit: progress bar, percent used, and time left until reset |
| `week` | Weekly limit: progress bar, percent used, and time left until reset |

- **Progress bar**: 8 cells wide, and each cell is split into 8 steps (`▏▎▍▌▋▊▉█`). That's 64 steps in total, about 1.6% each.
- **Colors**: green below 50% used, yellow from 50%, red from 80%.
- **Context**: the used count is colored by how close it is to the auto-compact threshold, using the same thresholds. Claude Code doesn't pass the threshold to the script, so the script works it out the same way Claude Code does: window size, minus a 20k output reserve, minus a 13k buffer (so 167k for a 200k window and 967k for 1M). It also respects `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`, `CLAUDE_CODE_AUTO_COMPACT_WINDOW`, `CLAUDE_CODE_MAX_OUTPUT_TOKENS`, `DISABLE_AUTO_COMPACT` and `autoCompactEnabled` in `~/.claude/settings.json`.
- **Time left**: `3d18h` if it's more than a day, `2h01m` if it's less than a day, `45m` if it's less than an hour, and `now` once the reset time has passed.

## Requirements

- Claude Code. Its status line input must include the `effort` and `rate_limits` fields. Tested on version 2.1.282.
- Python 3.7 or later. The script uses only the standard library, so there's nothing to install.
- A terminal that supports ANSI colors and Unicode block characters.
- Usage limit data is only available when you're signed in with a Claude Pro or Max account. With an API key, Bedrock or Vertex, the limit sections show `--`.

## Installation

1. Clone the repository, copy the script into your Claude Code config directory, and make it executable:

   ```bash
   git clone https://github.com/MAlanWine/ClaudeCodeCustomizeStatusBar.git
   cp ClaudeCodeCustomizeStatusBar/statusline.py ~/.claude/statusline.py
   chmod +x ~/.claude/statusline.py
   ```

2. Add a `statusLine` entry to `~/.claude/settings.json`, keeping any settings that are already there:

   ```json
   {
     "statusLine": {
       "type": "command",
       "command": "~/.claude/statusline.py",
       "padding": 0
     }
   }
   ```

   On Windows, you can set `command` to `python C:/Users/<your-username>/.claude/statusline.py`.

3. Restart Claude Code or send a message, and the status line appears at the bottom.

## Try it locally

You can preview the output with sample data, without starting Claude Code:

```bash
echo '{"model":{"display_name":"Opus 5.5"},"effort":{"level":"high"},"rate_limits":{"five_hour":{"used_percentage":37,"resets_at":'$(( $(date +%s)+7300 ))'},"seven_day":{"used_percentage":82,"resets_at":"2026-12-31T08:00:00Z"}}}' | ~/.claude/statusline.py
```

## Customization

Edit these in `statusline.py`:

- `BAR_WIDTH`: width of the progress bar, in cells
- `autocompact_threshold()`: how the auto-compact threshold is calculated, if a future Claude Code version changes the formula
- `pct_color()`: the color thresholds
- `sep` in `main()`: the separator between items
- `parts` in `main()`: which items are shown, and in what order

## How it works

Each time Claude Code refreshes the status line, it sends the script a JSON object on stdin with fields such as `model`, `effort`, `context_window`, `cost` and `rate_limits`. The script prints one line of text, and that line becomes the status line. `resets_at` can be either a Unix timestamp or an ISO 8601 string.
