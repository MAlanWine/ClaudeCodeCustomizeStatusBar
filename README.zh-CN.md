# ClaudeCodeCustomizeStatusBar

[English](README.md) | **简体中文**

一个自定义的 [Claude Code](https://claude.com/claude-code) 底部状态栏，显示当前模型、思考强度，以及订阅套餐的 5 小时与每周限额用量（带进度条和重置倒计时）。

```
Opus 5.5 · ⚡high · 5h ▕███     ▏ 37% ↻ 2h01m · week ▕██████▌ ▏ 82% ↻ 3d18h
```

## 显示内容

| 项目 | 说明 |
| --- | --- |
| 模型 | 当前使用的模型名称，如 `Opus 5.5` |
| 思考强度 | 当前的 effort 等级，如 `⚡high`；关闭思考时显示 `thinking off`，没有等级时显示 `default` |
| `5h` | 5 小时限额：进度条 + 已用百分比 + 距离重置的剩余时长 |
| `week` | 每周限额：进度条 + 已用百分比 + 距离重置的剩余时长 |

- **进度条**：宽 8 格，每格再细分 8 阶（`▏▎▍▌▋▊▉█`），共 64 阶，精度约 1.6%。
- **颜色**：已用低于 50% 为绿色，50% 起为黄色，80% 起为红色。
- **剩余时长格式**：超过 1 天为 `3d18h`，不足 1 天为 `2h01m`，不足 1 小时为 `45m`，已到期为 `now`。

## 环境要求

- Claude Code（状态栏输入中需包含 `effort` 和 `rate_limits` 字段，在 2.1.282 版本上测试通过）
- Python 3.7+（仅使用标准库，无需安装依赖）
- 支持 ANSI 颜色和 Unicode 方块字符的终端
- 限额数据仅在使用 Claude Pro / Max 账号登录时提供；使用 API Key、Bedrock、Vertex 时，限额部分显示 `--`

## 安装

1. 克隆仓库，把脚本复制到 Claude Code 配置目录并赋予执行权限：

   ```bash
   git clone https://github.com/MAlanWine/ClaudeCodeCustomizeStatusBar.git
   cp ClaudeCodeCustomizeStatusBar/statusline.py ~/.claude/statusline.py
   chmod +x ~/.claude/statusline.py
   ```

2. 编辑 `~/.claude/settings.json`，加入 `statusLine` 配置（保留原有的其他字段）：

   ```json
   {
     "statusLine": {
       "type": "command",
       "command": "~/.claude/statusline.py",
       "padding": 0
     }
   }
   ```

   Windows 上可以把 `command` 写成 `python C:/Users/<你的用户名>/.claude/statusline.py`。

3. 重启 Claude Code，或发送一条消息，底部就会出现状态栏。

## 本地测试

不启动 Claude Code 也可以用模拟数据预览效果：

```bash
echo '{"model":{"display_name":"Opus 5.5"},"effort":{"level":"high"},"rate_limits":{"five_hour":{"used_percentage":37,"resets_at":'$(( $(date +%s)+7300 ))'},"seven_day":{"used_percentage":82,"resets_at":"2026-12-31T08:00:00Z"}}}' | ~/.claude/statusline.py
```

## 自定义

打开 `statusline.py` 修改：

- `BAR_WIDTH`：进度条宽度（格数）
- `pct_color()`：颜色阈值
- `main()` 中的 `sep`：各项之间的分隔符
- `main()` 中的 `parts`：显示哪些项目以及顺序

## 工作原理

Claude Code 每次刷新状态栏时，会通过 stdin 向脚本传入一段 JSON（包含 `model`、`effort`、`rate_limits` 等字段），脚本把它格式化后输出一行文本，这一行就是状态栏的内容。`resets_at` 同时支持 Unix 时间戳和 ISO 8601 字符串。
