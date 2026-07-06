# 创作者中心到 HeyGen 数字人视频 SOP

## 1. 看报表

你打开抖音/小红书/视频号创作者中心。

优先记录：

- 近 7 天总播放、涨粉、主页访问、私信。
- 最近 10 条作品的播放、点赞、评论、收藏、转发。
- 能看到的话，补 3 秒/5 秒留存、完播率、平均观看时长、推荐流量占比。

把数据填入：

`platform-intelligence/templates/report_input.csv`

## 2. 做热榜扫描

填入：

`platform-intelligence/templates/trend_scan.md`

热榜只记录能转成你账号内容的点：

- 篮球热点：能不能转成教练判断、训练问题、家长认知。
- 小红书情绪：只能转成体育哲学、心理症状命名、普通人成长、收藏清单。
- 视频号场景：能不能让家长愿意转发。

小红书硬边界：

- 不发篮球技战术。
- 不发青训诊断。
- 不发训练表和动作纠错。
- 不承接“发视频给我诊断”的 CTA。
- 只做体育哲学、心理恢复、普通人成长、低谷叙事。

## 3. 生成内容包

运行：

```bash
python3 platform-intelligence/scripts/generate_content_brief.py \
  --report platform-intelligence/templates/report_input.csv \
  --trends platform-intelligence/templates/trend_scan.md
```

输出位置：

`platform-intelligence/daily_outputs/YYYY-MM-DD/`

关键文件：

- `daily_review.md`：今天报表怎么解释。
- `copy_pack.md`：抖音、小红书、视频号文案。
- `heygen_script.txt`：数字人口播稿。
- `heygen_request.json`：HeyGen 生成请求。
- `production_checklist.md`：无字幕、无BGM、Luca球衣背景polo场景。
- `monetization.md`：今天可接广告和自有产品入口。

## 4. 生成 HeyGen 视频

只有你确认后才执行，避免浪费 HeyGen 额度。

干跑检查：

```bash
python3 platform-intelligence/scripts/create_heygen_video.py \
  platform-intelligence/daily_outputs/YYYY-MM-DD/heygen_request.json \
  --dry-run
```

确认生成：

```bash
python3 platform-intelligence/scripts/create_heygen_video.py \
  platform-intelligence/daily_outputs/YYYY-MM-DD/heygen_request.json \
  --wait
```

固定要求：

- 使用 Luca 数字人。
- 只使用两个球衣墙形象：
  - 深色 polo：默认优先，用于犀利篮球观点、热点拆解、诊断转化。
  - 白色 polo：备用，用于家长向、课程感、青训讲解。
- 使用中文 Luca 声音。
- HeyGen 内不加字幕。
- HeyGen 内不加背景音乐。

## 5. 字幕选择

默认不在 HeyGen 里加字幕。

成片出来后有两种路线：

1. Codex 加字幕：适合快速发，统一输出 `.srt` 或 `.ass`。
2. 你去剪映操作：适合要克隆声音精修、字幕样式精修、平台原生字幕。

## 6. 发布时间

三个平台都按每天 1 条执行：

- 抖音：1 条，篮球热点/实战判断/AI拆球。
- 小红书：1 条，体育哲学/心理症状命名/普通人成长。
- 视频号：1 条，家长信任/青训判断/比赛诊断。

同一天可以共用一个大主题，但必须平台化改写，不允许一稿三发。

第一天数据不够时用默认窗口：

- 抖音：21:30
- 小红书：21:30
- 视频号：20:30

当 `report_input.csv` 积累真实数据后，脚本会按每个平台历史高分内容的发布时间小时，自动校准建议发布时间。

## 7. 广告和变现判断

每天只推和账号信任一致的广告：

- 篮球馆
- 青训机构
- 训练器材
- 运动康复/体能
- 赛事/球局组织
- AI工具/教育工具

每天必须带一个自有转化口：

- 评论「诊断」
- 私信「比赛」
- 私信「智能体」
- 小红书只用「恢复」「低谷」「共鸣」这类体育哲学入口，不用「诊断」「比赛」。
