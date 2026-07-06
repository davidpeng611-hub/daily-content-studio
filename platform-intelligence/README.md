# 三平台半自动内容智库

目标：把抖音、小红书、微信视频号的报表数据，转成第二天能直接执行的内容方案。

第一版流程：

1. 你打开创作者中心，看报表。
2. 把关键数据填到 `templates/report_input.csv` 的同款表格里。
3. 把当天热点填到 `templates/trend_scan.md` 的同款文件里。
4. 运行：

```bash
python3 platform-intelligence/scripts/generate_content_brief.py \
  --report platform-intelligence/templates/report_input.csv \
  --trends platform-intelligence/templates/trend_scan.md
```

脚本会生成：

- 每日复盘
- 抖音/小红书/视频号文案
- HeyGen 数字人口播稿
- 发布时间建议
- 热点标签
- 广告合作和诊断/智能体变现入口

## 执行原则

- 发布频率：三个平台都按每天 1 条执行。抖音 1 条、小红书 1 条、视频号 1 条。
- 同一天可以共用一个大主题，但必须按平台定位改写，不允许一稿三发。
- 抖音主打：篮球热点 + AI拆球 + 教练判断 + 诊断转化。
- 小红书主打：体育哲学 + 心理症状命名 + 普通人成长 + 收藏共鸣；不做篮球技战术和青训诊断。
- 视频号主打：家长信任 + 青训判断 + 转发友好。
- HeyGen 只出无字幕、无背景音乐的干净数字人口播视频。
- 字幕后置处理：默认由 Codex 生成字幕文件；如果你有时间，也可以去剪映做克隆声音、字幕和精修。
- 公开视频发布前仍然需要你确认。

## 目录

- `config/production_profile.json`：默认生产配置。
- `templates/report_input.csv`：创作者中心数据录入模板。
- `templates/trend_scan.md`：当天热榜和平台趋势模板。
- `scripts/generate_content_brief.py`：日报、文案、HeyGen脚本生成器。
- `scripts/create_heygen_video.py`：确认后调用 HeyGen 生成干净数字人口播视频。
- `scripts/notify_user.py`：把自动化报告推送到微信通知通道。
- `playbooks/creator_center_to_heygen_sop.md`：从创作者中心到 HeyGen 成片的执行 SOP。
- `playbooks/xiaohongshu_sports_philosophy_agent_bridge.md`：小红书接入体育哲学智能体的桥接规则。
- `playbooks/wechat_notification_sop.md`：微信通知配置说明。
- `daily_outputs/`：每天自动生成的结果。
