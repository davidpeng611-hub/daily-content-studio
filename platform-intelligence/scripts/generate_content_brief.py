#!/usr/bin/env python3
import argparse
import csv
import json
import re
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "production_profile.json"
OUTPUT_ROOT = ROOT / "daily_outputs"


def read_text(path):
    return Path(path).read_text(encoding="utf-8")


def load_config():
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def to_float(value, default=0.0):
    if value is None:
        return default
    text = str(value).strip().replace("%", "")
    if not text:
        return default
    try:
        number = float(text)
        if "%" in str(value):
            return number / 100
        return number
    except ValueError:
        return default


def load_rows(path):
    rows = []
    with Path(path).open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not any((v or "").strip() for v in row.values()):
                continue
            metric_keys = [
                "views", "likes", "comments", "saves", "shares", "followers", "dm",
                "retention_3s", "retention_5s", "completion_rate", "avg_watch_sec",
                "recommend_pct", "profile_visits",
            ]
            has_metrics = any(to_float(row.get(key)) > 0 for key in metric_keys)
            if not has_metrics and "替换成创作者中心真实数据" in (row.get("notes") or ""):
                continue
            rows.append(row)
    return rows


def norm_platform(platform):
    raw = (platform or "").strip().lower()
    if raw in {"抖音", "douyin", "dy"}:
        return "douyin"
    if raw in {"小红书", "xiaohongshu", "xhs", "rednote"}:
        return "xiaohongshu"
    if raw in {"视频号", "微信视频号", "wechat", "wechat_channels"}:
        return "wechat_channels"
    return raw or "unknown"


def score_row(row):
    views = to_float(row.get("views"))
    likes = to_float(row.get("likes"))
    comments = to_float(row.get("comments"))
    saves = to_float(row.get("saves"))
    shares = to_float(row.get("shares"))
    followers = to_float(row.get("followers"))
    dm = to_float(row.get("dm"))
    completion = to_float(row.get("completion_rate"))
    retention = to_float(row.get("retention_3s")) or to_float(row.get("retention_5s"))
    business = dm * 20 + comments * 3 + saves * 4 + shares * 4 + followers * 6
    spread = views + likes * 10 + comments * 25 + saves * 30 + shares * 35
    quality = completion * 100 + retention * 80
    return {
        "spread": spread,
        "business": business,
        "quality": quality,
        "total": spread + business * 8 + quality * 20,
    }


def top_by_platform(rows):
    grouped = defaultdict(list)
    for row in rows:
        row = dict(row)
        row["_platform"] = norm_platform(row.get("platform"))
        row["_score"] = score_row(row)
        grouped[row["_platform"]].append(row)
    for platform in grouped:
        grouped[platform].sort(key=lambda r: r["_score"]["total"], reverse=True)
    return grouped


def extract_bullets(md, section_title):
    pattern = rf"## {re.escape(section_title)}\s*(.*?)(?=\n## |\Z)"
    match = re.search(pattern, md, re.S)
    if not match:
        return []
    lines = []
    for line in match.group(1).splitlines():
        line = line.strip()
        if line.startswith("- "):
            lines.append(line[2:].strip())
    return lines


def choose_publish_times(rows, config):
    result = {}
    by_platform_hour = defaultdict(lambda: defaultdict(float))
    for row in rows:
        platform = norm_platform(row.get("platform"))
        time_text = (row.get("publish_time") or "").strip()
        hour = time_text[:2] if re.match(r"^\d{2}:", time_text) else ""
        if hour:
            by_platform_hour[platform][hour] += score_row(row)["total"]

    for platform, defaults in config["publishing_windows"].items():
        if by_platform_hour[platform]:
            best_hour = max(by_platform_hour[platform], key=by_platform_hour[platform].get)
            default_minute = defaults[-1].split(":")[1]
            result[platform] = f"{best_hour}:{default_minute}"
        else:
            result[platform] = defaults[-1]
    return result


def make_hashtags(platform, trends):
    trend_text = " ".join(trends)
    if platform == "douyin" and ("喀麦隆" in trend_text or "格鲁吉亚" in trend_text or "团结杯" in trend_text):
        base = ["#篮球", "#国际团结杯", "#中国男篮", "#格鲁吉亚", "#篮球教学", "#AI拆球", "#彭sir在现场"]
    elif platform == "douyin" and ("粤BA" in trend_text or "群众篮球" in trend_text or "真实比赛" in trend_text):
        base = ["#篮球", "#粤BA", "#群众篮球", "#篮球教学", "#AI拆球", "#彭sir在现场"]
    else:
        base = {
            "douyin": ["#篮球", "#中国男篮", "#篮球教学", "#AI拆球", "#彭sir在现场"],
            "xiaohongshu": ["#体育哲学", "#普通人成长", "#低谷期", "#心理恢复", "#长期主义"],
            "wechat_channels": ["#青少年篮球", "#家长课堂", "#篮球训练", "#比赛复盘"],
        }[platform]
    if "日本" in trend_text and "生死战" not in trend_text and "输球后" not in trend_text:
        base.insert(1, "#中国男篮vs日本")
    if "喀麦隆" in trend_text or "格鲁吉亚" in trend_text or "团结杯" in trend_text:
        base.insert(1, "#国际团结杯")
    if "快攻" in trend_text:
        base.append("#快攻")
    if "挡拆" in trend_text:
        base.append("#挡拆")
    return list(dict.fromkeys(base))[:8]


def main_topic(trends):
    joined = " ".join(trends)
    if "喀麦隆" in joined or "格鲁吉亚" in joined or "团结杯" in joined:
        return "中国男篮大胜喀麦隆后迎战格鲁吉亚，真正该看的是赢球背后的提前量和下一场稳定性"
    if "粤BA" in joined or "群众篮球" in joined or "被看见" in joined or "真实比赛" in joined:
        return "粤BA半决赛打开群众篮球话题，真正值得讲的是普通人的比赛为什么也值得被看见"
    if "生死战" in joined or "输球后" in joined or "下一场" in joined or "重启" in joined:
        return "7月6日末轮生死战前，真正该看的不是上一场怎么输，而是输球后下一场怎么重启"
    if "中国男篮" in joined and "日本" in joined:
        return "中国男篮输日本，普通球友和家长真正该学的不是骂投篮，而是快攻、无球和提前判断"
    if "孩子" in joined or "家长" in joined:
        return "孩子训练很多但比赛不会用，问题常在提前判断和无球习惯"
    return "用一个篮球热点拆出普通球友明天能改的一个实战问题"


def build_script(topic, trends):
    joined = " ".join(trends)
    if "喀麦隆" in joined or "格鲁吉亚" in joined or "团结杯" in joined:
        return """开头：
中国男篮113比79赢喀麦隆，别只看34分，也别急着喊复兴。

正文：
这场球真正有价值的，不是比分好看，而是三个细节：
第一，球转得快，全队助攻多，说明大家不是拿球才想。
第二，外线机会出来得早，很多投篮不是硬拔，是提前跑位带出来的。
第三，12个人都有参与感，这比某一个人爆发更重要。

但今晚打格鲁吉亚，考验会完全不同。
强队不会让你轻松起速，也不会让你每次都舒服出手。

普通球友和孩子比赛也一样。
一场大胜最容易骗你，让你以为自己什么都会了。
真正要复盘的是：机会是怎么提前创造出来的？被限制后，还能不能继续做正确选择？

转化：
所以我看比赛视频，不只看你进了几个球。
我更看接球前、无球时、被防住后的三个反应。
想让我帮你拆一段比赛，评论「诊断」。"""

    if "粤BA" in joined or "群众篮球" in joined or "被看见" in joined or "真实比赛" in joined:
        return """开头：
很多人只盯国家队和职业比赛，但真正能让普通球友学到东西的，反而是这种群众篮球。

正文：
粤BA这种比赛好看，不是因为每个人技术都多完美。
它好看在四个地方：
第一，防守是真拼的。
第二，转换是真快的。
第三，每个城市都有自己的荣誉感。
第四，观众知道自己在支持谁。

普通球友最该学的，也不是模仿职业球员的高难度动作。
而是看一场真实比赛里，谁愿意回防，谁敢对抗，谁能在乱局里做正确选择。

训练课能教动作。
真实比赛，才会暴露你的情绪、责任和判断。

转化：
所以我看普通比赛，不只看谁得分多。
我更看这个人有没有让队友更好打。
想让我帮你拆一场普通比赛，评论「球局」。"""

    if "生死战" in joined or "输球后" in joined or "下一场" in joined or "重启" in joined:
        return """开头：
明天这场生死战，真正考验的不是中国男篮会不会骂醒，而是能不能从上一场里走出来。

正文：
很多球队输完球，最容易犯一个错：第二场一上来就想证明自己。
越想证明，动作越急；越怕再错，选择越保守。
普通球员也是一样。上一场投丢了，下一场不敢投；上一场失误了，下一场接球就慌。
教练这时候最该看的，不是他说了多少狠话，而是三个细节：
第一，接球后还敢不敢做正确选择。
第二，丢球后能不能马上回到防守。
第三，队友犯错后，全队会不会继续执行。

转化：
所以我看孩子比赛，不只看技术，更看输球后的下一场反应。
家长想让我帮你看孩子比赛视频，评论「比赛」。"""

    return f"""开头：
很多人看中国男篮输球，只盯着投篮准不准。但真正值得普通球友学的，是这三个字：提前量。

正文：
快攻不是跑得快就行，是你在队友抢到球之前，就知道自己该往哪里跑。
挡拆也不是只做一个掩护，是掩护之后，持球人、顺下人、弱侧队友，能不能同时给防守压力。
普通球友和青少年比赛里，最常见的问题不是不会技术，而是永远等球到手才开始想。
等你开始想，防守已经回来了，机会也没了。

转化：
所以我看一段比赛视频，最先不看进不进球，而是看接球前、丢球后、无球时这三个瞬间。
想让我帮你看一段比赛或投篮视频，评论「诊断」。"""


def build_xhs_sports_philosophy_copy(trends, publish_time):
    joined = " ".join(trends)
    if "台风" in joined or "延期" in joined or "红霞" in joined:
        symptom = "人生替补期"
        title = "计划被打断，不代表你输了"
        body = """很多人最怕的，不是失败。
是明明已经准备好了，结果突然被迫暂停。

比赛会延期。
面试会改期。
项目会卡住。
一段关系也可能突然没有回应。

普通人最容易在这种时候怀疑自己：
是不是我不够好，所以才一直轮不到我？

但体育里有一种能力，叫等待比赛重新开始。
真正成熟的人，不是在风雨里硬上场，
而是在暂停期里保护状态、整理动作、保持节奏。

你不是被淘汰了。
你只是进入一段人生替补期。

今天的小动作：
把今天原本要做、但被打断的一件事，改成一个15分钟的保底动作。
别证明自己很强，先证明自己还在场。"""
        tags = "#体育哲学 #心理学 #普通人成长 #人生替补期 #计划被打断 #情绪恢复 #低谷期"
        return symptom, f"""标题：
{title}

正文：
{body}

建议发布时间：{publish_time}
{tags}"""

    if "粤BA" in joined or "群众篮球" in joined or "被看见" in joined or "真实比赛" in joined:
        symptom = "被看见焦虑"
        title = "普通人的比赛，也值得被看见"
        body = """很多人不是不热爱。
只是他热爱的东西，从来没有被认真看见过。

体育里不只有国家队、职业队和聚光灯。
也有很多普通人，在一个很小的场地里，
为了一个篮板、一回合防守、一次回防认真到发狠。

普通人最容易低估自己的努力。
因为没有观众，没有掌声，没有数据榜，
就以为这一切不算数。

可人生很多真正重要的比赛，
本来就不是打给所有人看的。

你不一定要站上最大的赛场。
先认真打好你现在这一场。

今天的小动作：
写下一个你正在认真做、但暂时没人看见的事情。
然后告诉自己：没人看见，不等于没有价值。"""
        tags = "#体育哲学 #心理学 #普通人成长 #被看见焦虑 #人生替补期 #热爱 #长期主义"
        return symptom, f"""标题：
{title}

正文：
{body}

建议发布时间：{publish_time}
{tags}"""

    if "输球后" in joined or "生死战" in joined or "下一场" in joined or "恢复" in joined:
        symptom = "心理恢复期"
        title = "你不是输不起，是还没恢复"
        body = """很多人以为自己怕的是下一场失败。
其实你怕的是，上一场失败还在身体里。

运动员输完比赛，最难的不是复盘技术，
而是把自己从“我不行”的情绪里拉回来。

普通人也一样。
一次面试失败、一段关系结束、一次努力没结果，
真正拖住你的，往往不是那件事本身，
而是你一直在用上一场的失败，惩罚下一场的自己。

体育里真正重要的，不只是上场，
也包括承认自己还在恢复期。

今天的小动作：
写下一个你还没走出来的失败，
再写一句：下一场，我只先做好一个动作。"""
        tags = "#体育哲学 #心理学 #普通人成长 #心理恢复期 #低谷期 #内耗 #恢复力"
    elif "怕" in joined or "赢" in joined:
        symptom = "怕输型人格"
        title = "你不是想赢，你只是输不起"
        body = """有些人看起来胜负欲很强。
但真正折磨他的，不是想赢，
而是只要一输，就会觉得自己整个人都不行了。

体育里，失败本来只是一次结果。
可普通人最容易把一次结果，变成对自己的判决。

考试没考好，就觉得自己没前途。
工作没做好，就觉得自己没价值。
关系失败了，就觉得自己不值得被爱。

你要练的不是永远赢，
而是输完以后，还能把自己从结果里拿回来。

今天的小动作：
把“我不行”改成“这一场我哪里变形了”。"""
        tags = "#体育哲学 #心理学 #普通人成长 #怕输型人格 #表现焦虑 #内耗"
    else:
        symptom = "人生替补期"
        title = "你不是没用，你在替补期"
        body = """很多人最难熬的，不是失败。
是站在场边，看别人都在上场。

体育里有替补席。
人生也有替补期。

你会看着同龄人升职、赚钱、恋爱、成家，
然后开始怀疑：是不是只有我被落下了。

但替补期不是废掉。
它也可能是重新看懂比赛、修正动作、等身体恢复的阶段。

今天的小动作：
别问自己什么时候轮到我。
先问：我现在能把哪一个动作练稳。"""
        tags = "#体育哲学 #心理学 #普通人成长 #人生替补期 #低谷期 #长期主义"

    return symptom, f"""标题：
{title}

正文：
{body}

建议发布时间：{publish_time}
{tags}"""


def build_heygen_prompt(script, config):
    heygen = config["heygen"]
    allowed_scenes = "\n".join(f"- {scene}" for scene in heygen.get("allowed_scenes", []))
    return f"""Create a vertical Chinese talking-head short video for Douyin.

Use the existing creator avatar named {heygen.get('avatar_group_name', 'Luca')} if available.
Use the preferred scene: {heygen.get('preferred_scene', 'basketball creator talking-head scene')}.
Allowed avatar scenes:
{allowed_scenes}
Keep the visual clean and simple.

Hard requirements:
- Aspect ratio: {heygen['aspect_ratio']}
- Resolution: {heygen['resolution']}
- No captions or subtitles inside HeyGen.
- No background music.
- No stock b-roll.
- Presenter speaks directly to camera with calm but sharp coach energy.
- Do not change to a different presenter.
- Do not change to a generic office, studio, classroom, or news background.
- Use only one of the two allowed jersey-wall polo scenes.
- Prefer the dark polo scene for sharp Douyin basketball hot-take content.
- Use the white polo scene for calmer parent-facing or course-like explanations.

Chinese script:
{script}
"""


def build_copy(topic, trends, times):
    joined = " ".join(trends)
    douyin_tags = " ".join(make_hashtags("douyin", trends))
    xhs_tags = " ".join(make_hashtags("xiaohongshu", trends))
    wechat_tags = " ".join(make_hashtags("wechat_channels", trends))
    xhs_symptom, xhs_copy = build_xhs_sports_philosophy_copy(trends, times["xiaohongshu"])
    if "喀麦隆" in joined or "格鲁吉亚" in joined or "团结杯" in joined:
        return {
            "douyin": f"""标题：
赢喀麦隆别只看比分，今晚才是真检验

正文：
113比79当然值得高兴，但真正能拆给普通球友的，是提前量：提前跑位、提前传球、提前做选择。

今晚打格鲁吉亚，如果对抗更强、节奏更慢，中国男篮还能不能继续把球转起来，这才是重点。

评论「诊断」，发一段你的比赛视频，我帮你看接球前、无球时、被防住后的三个反应。

建议发布时间：{times['douyin']}
{douyin_tags}""",
            "xiaohongshu": xhs_copy,
            "wechat_channels": f"""标题：
孩子大胜之后，家长更该看这一点

正文：
孩子赢球后，家长不要只夸得分。
真正能持续进步的孩子，是大胜之后还知道复盘：机会怎么来的，队友怎么被带动，被限制后还能不能做正确选择。

今晚中国男篮打格鲁吉亚，也是同一个道理。
能赢弱一档对手不稀奇，强对抗下还能不能稳定执行，才是训练有没有用的证明。

需要孩子比赛视频诊断，可以私信「比赛」。

建议发布时间：{times['wechat_channels']}
{wechat_tags} #中国男篮 #青训""",
        }
    if "生死战" in joined or "输球后" in joined or "下一场" in joined or "重启" in joined:
        return {
            "douyin": f"""标题：
生死战前，最怕的不是输球，是还没走出来

正文：
上一场已经发过复盘，今天换个角度：输球后的下一场，教练最该看什么？

不是狠话，不是表态，而是接球选择、丢球反应、全队执行。

评论「比赛」，发一段孩子或球队比赛视频，我帮你看他有没有从上一场走出来。

建议发布时间：{times['douyin']}
{douyin_tags} #世预赛 #生死战 #篮球心理""",
            "xiaohongshu": xhs_copy,
            "wechat_channels": f"""标题：
孩子输完球，下一场更关键

正文：
家长不要只问孩子为什么输。
更应该看他下一场有没有恢复：敢不敢接球、失误后回不回防、还听不听教练安排。

需要孩子比赛视频诊断，可以私信「比赛」。

建议发布时间：{times['wechat_channels']}
{wechat_tags} #赛后复盘 #青训""",
        }
    if "粤BA" in joined or "群众篮球" in joined or "被看见" in joined or "真实比赛" in joined:
        return {
            "douyin": f"""标题：
为什么粤BA比很多职业比赛更有烟火气？

正文：
群众篮球好看，不是因为动作更高级，而是因为它有真实对抗、城市荣誉、现场情绪和普通人的责任感。

训练课能教动作，真实比赛才会暴露情绪、对抗、选择和责任。

评论「球局」，我帮你看一场普通比赛到底哪里好看、哪里该改。

建议发布时间：{times['douyin']}
{douyin_tags} #粤BA #群众篮球 #球局""",
            "xiaohongshu": xhs_copy,
            "wechat_channels": f"""标题：
孩子为什么需要多打真实比赛？

正文：
训练课教动作，真实比赛教情绪、对抗、选择和责任。

孩子平时练得好，不代表一到比赛就能用出来。
真实比赛会暴露：他敢不敢对抗、会不会回防、能不能做选择、愿不愿意承担责任。

需要孩子比赛视频诊断，可以私信「比赛」。

建议发布时间：{times['wechat_channels']}
{wechat_tags} #真实比赛 #青训 #篮球家长""",
        }
    return {
        "douyin": f"""标题：
输日本别只骂投篮，真正差在提前量

正文：
这场球最值得普通球友学的，不是情绪，而是三个细节：快攻提前跑、挡拆后续选择、无球站位。

评论「诊断」，发一段你的投篮/比赛视频，我帮你找一个最该改的问题。

建议发布时间：{times['douyin']}
{douyin_tags}""",
        "xiaohongshu": xhs_copy,
        "wechat_channels": f"""标题：
孩子打比赛，别只看他进了几个球

正文：
家长看比赛，最容易只看得分。
但真正决定孩子能不能进步的，是无球时会不会提前跑、丢球后会不会马上反应、接球前有没有准备。

需要孩子比赛视频诊断，可以私信「比赛」。

建议发布时间：{times['wechat_channels']}
{wechat_tags}""",
    }


def build_sports_philosophy_agent_brief(config, trends, times):
    agent = config["sports_philosophy_agent"]
    symptom, xhs_copy = build_xhs_sports_philosophy_copy(trends, times["xiaohongshu"])
    lines = [
        "# 小红书体育哲学智能体简报",
        "",
        f"定位：{agent['positioning']}",
        "",
        "## 调用来源",
        "",
    ]
    lines += [f"- {path}" for path in agent["source_files"]]
    lines += [
        "",
        "## 今日症状命名",
        "",
        f"- {symptom}",
        "",
        "## 硬边界",
        "",
    ]
    lines += [f"- {item}" for item in agent["hard_boundaries"]]
    lines += [
        "",
        "## 脚本结构要求",
        "",
    ]
    lines += [f"- {item}" for item in agent["required_structure"]]
    lines += [
        "",
        "## 今日小红书文案",
        "",
        xhs_copy,
    ]
    return "\n".join(lines)


def build_monetization(config, trends):
    ad_targets = [
        "本地篮球馆：用探馆/训练场景换广告或团购合作。",
        "青训机构：卖家长信任内容和孩子比赛诊断入口。",
        "篮球训练器材：护具、训练锥、弹力带、投篮辅助器，适合挂在训练清单内容后。",
        "运动康复/体能训练工作室：承接膝踝伤、体能恢复、青少年体态话题。",
        "赛事/球局组织方：用热点复盘和现场观察换同城曝光合作。",
        "AI工具/教育工具：包装成教练智能体、训练反馈效率工具，不讲抽象AI。",
    ]
    products = config["monetization_products"]
    lines = ["# 变现与广告机会", "", "## 今天可接广告方向", ""]
    lines += [f"- {item}" for item in ad_targets]
    lines += ["", "## 今天主推自有产品", ""]
    for product in products:
        lines.append(f"- {product['name']}：{product['price']} 元。CTA：{product['cta']}")
    lines += [
        "",
        "## 严格筛选",
        "",
        "- 不接和篮球、训练、青训、装备、AI效率无关的泛广告。",
        "- 不接会削弱教练专业感的低质带货。",
        "- 广告必须能自然嵌入一个训练问题或家长问题。",
    ]
    return "\n".join(lines)


def render_daily_review(rows, grouped, trends, topic, times):
    lines = ["# 每日三平台复盘", "", f"日期：{date.today().isoformat()}", "", "## 今日结论", ""]
    if rows:
        lines.append("- 已根据报表数据生成平台建议；后续数据越完整，发布时间会越精准。")
    else:
        lines.append("- 今天没有输入报表数据，先按账号策略和热点生成内容方案。")
    lines += ["", f"- 今日主线：{topic}", "", "## 平台数据判断", ""]
    for platform, items in grouped.items():
        best = items[0]
        score = best["_score"]
        lines.append(f"- {platform}：表现最好的是《{best.get('title','')}》，播放 {best.get('views','')}，私信 {best.get('dm','')}，商业分 {score['business']:.1f}。")
    if not grouped:
        lines.append("- 暂无逐条数据。先重点补：播放、完播、3秒留存、收藏、转发、私信。")
    lines += ["", "## 发布时间建议", ""]
    for platform, publish_time in times.items():
        lines.append(f"- {platform}：{publish_time}，每日 1 条。")
    lines += [
        "",
        "## 今日发布标准",
        "",
        "- 抖音：1 条，篮球热点/实战判断/AI拆球。",
        "- 小红书：1 条，体育哲学/心理症状命名/普通人成长。",
        "- 视频号：1 条，家长信任/青训判断/比赛诊断。",
        "- 同一主题必须平台化改写，不允许一稿三发。",
    ]
    lines += ["", "## 热点依据", ""]
    lines += [f"- {item}" for item in trends[:8]]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate platform content brief from creator-center data.")
    parser.add_argument("--report", required=True, help="CSV exported or filled from creator-center reports")
    parser.add_argument("--trends", required=True, help="Markdown trend scan")
    parser.add_argument("--date", default=date.today().isoformat(), help="output date, YYYY-MM-DD")
    args = parser.parse_args()

    config = load_config()
    rows = load_rows(args.report)
    trends_md = read_text(args.trends)
    trends = extract_bullets(trends_md, "篮球热点") + extract_bullets(trends_md, "小红书/视频号情绪热点") + extract_bullets(trends_md, "今天主推商业入口")
    if not trends:
        trends = ["篮球热点", "普通球友实战问题", "家长青训痛点"]

    grouped = top_by_platform(rows)
    times = choose_publish_times(rows, config)
    topic = main_topic(trends)
    script = build_script(topic, trends)
    heygen_prompt = build_heygen_prompt(script, config)
    copy = build_copy(topic, trends, times)

    out_dir = OUTPUT_ROOT / args.date
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "daily_review.md").write_text(render_daily_review(rows, grouped, trends, topic, times), encoding="utf-8")
    (out_dir / "heygen_script.txt").write_text(script, encoding="utf-8")
    heygen_request = {
        "prompt": heygen_prompt,
        "orientation": "portrait",
        "voice_id": config["heygen"]["default_voice_id"],
        "voice_name": config["heygen"]["default_voice_name"],
        "avatar_group_id": config["heygen"].get("avatar_group_id", ""),
        "avatar_group_name": config["heygen"].get("avatar_group_name", ""),
        "preferred_scene": config["heygen"].get("preferred_scene", ""),
        "allowed_scenes": config["heygen"].get("allowed_scenes", []),
        "avatar_id": config["heygen"].get("avatar_id", ""),
        "caption": "off",
        "background_music": "off",
        "resolution": config["heygen"]["resolution"],
        "aspect_ratio": config["heygen"]["aspect_ratio"],
    }
    (out_dir / "heygen_request.json").write_text(json.dumps(heygen_request, ensure_ascii=False, indent=2), encoding="utf-8")
    avatar_arg = config["heygen"].get("avatar_id") or config["heygen"].get("avatar_group_id", "")
    command = [
        "$HOME/.local/bin/heygen video-agent create",
        "--mode generate",
        "--orientation portrait",
        f"--voice-id {config['heygen']['default_voice_id']}",
    ]
    if avatar_arg:
        command.append(f"--avatar-id {avatar_arg}")
    command.append("--prompt \"$(python3 - <<'PY'\nimport json\nprint(json.load(open('heygen_request.json', encoding='utf-8'))['prompt'])\nPY\n)\"")
    command.append("--wait")
    (out_dir / "heygen_cli_command.txt").write_text(" \\\n  ".join(command) + "\n", encoding="utf-8")
    (out_dir / "copy_pack.md").write_text(
        "# 三平台发布文案\n\n"
        "## 抖音\n\n" + copy["douyin"] + "\n\n"
        "## 小红书\n\n" + copy["xiaohongshu"] + "\n\n"
        "## 微信视频号\n\n" + copy["wechat_channels"] + "\n",
        encoding="utf-8",
    )
    (out_dir / "sports_philosophy_agent_brief.md").write_text(
        build_sports_philosophy_agent_brief(config, trends, times),
        encoding="utf-8",
    )
    (out_dir / "production_checklist.md").write_text(
        "# HeyGen 生产清单\n\n"
        "- 使用 HeyGen 已有数字人模板。\n"
        f"- 默认数字人：{config['heygen'].get('avatar_group_name', '')} / {config['heygen'].get('avatar_group_id', '')}。\n"
        f"- 固定场景：{config['heygen'].get('preferred_scene', '')}。\n"
        "- 可用形象：深色 polo 球衣墙；白色 polo 球衣墙。\n"
        f"- 默认声音：{config['heygen']['default_voice_name']} / {config['heygen']['default_voice_id']}。\n"
        "- 画幅：9:16。\n"
        "- 清晰度：1080p。\n"
        "- 不要 HeyGen 字幕。\n"
        "- 不要背景音乐。\n"
        "- 生成干净口播视频后，再决定：Codex 加字幕，或用户去剪映做字幕/声音精修。\n"
        "- 发布前必须人工确认。\n",
        encoding="utf-8",
    )
    (out_dir / "monetization.md").write_text(build_monetization(config, trends), encoding="utf-8")
    print(out_dir)


if __name__ == "__main__":
    main()
