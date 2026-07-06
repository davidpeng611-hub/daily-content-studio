# 篮球快剪

本地篮球比赛片段裁剪工具。

## 使用方式

1. 启动服务：

   ```bash
   PATH="/Users/luca/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH" /Users/luca/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/pnpm start
   ```

2. 打开：

   http://localhost:5177

3. 操作：

   - 选择比赛视频。
   - 播放到片段开始位置，按 `S`。
   - 播放到片段结束位置，按 `E`。
   - 片段会自动保存，并出现在页面下方的「已保存片段」里。

导出的片段会放在：

```text
basketball-quick-cut/exports
```

## 说明

- 默认导出原始横屏比例，会尽量无损快速裁切。
- 勾选「同时转成9:16竖屏」时，会重新编码并裁成抖音竖屏。
