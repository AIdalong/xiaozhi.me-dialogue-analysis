#!/usr/bin/env python3
"""自动生成报告框架：填入统计数字，供人工补充定性观察
用法: python3 scripts/report_generator.py [data.json] [out.md]
输出: output/report_YYYYMMDD.md（或指定路径）
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA = os.path.join(BASE, "..", "raw", "all_messages.json")
DEFAULT_TEMPLATE = os.path.join(BASE, "..", "templates", "report_template.md")
CONFIG = os.path.join(BASE, "..", "config", "themes.json")


def load_data(path=None):
    path = path or DEFAULT_DATA
    if not os.path.exists(path):
        sys.exit(f"未找到数据文件: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    data_path = sys.argv[1] if len(sys.argv) > 1 else None
    out_path = sys.argv[2] if len(sys.argv) > 2 else None
    chats = load_data(data_path)

    with open(CONFIG, "r", encoding="utf-8") as f:
        config = json.load(f)
    themes = config["themes"]
    pos_emoji = config.get("emoji_positive", [])
    neg_emoji = config.get("emoji_negative", [])

    # 收集用户消息
    user_msgs = []
    for c in chats:
        for m in c["messages"]:
            if m["role"] == "user":
                user_msgs.append({"time": m.get("created_at", ""), "content": m.get("content", "")})
    user_msgs.sort(key=lambda x: x["time"])

    n_chats = len(chats)
    n_msgs = sum(len(c["messages"]) for c in chats)
    n_user = len(user_msgs)
    n_days = len(set(um["time"][:10] for um in user_msgs if um["time"]))
    all_text = "\n".join(um["content"] for um in user_msgs)

    # 时间范围
    times = sorted(um["time"] for um in user_msgs if um["time"])
    t_start = times[0][:10] if times else "?"
    t_end = times[-1][:10] if times else "?"

    # 每天消息数（找最长单日）
    day_counts = Counter(um["time"][:10] for um in user_msgs if um["time"])
    max_day = max(day_counts.items(), key=lambda x: x[1]) if day_counts else ("?", 0)

    # 每天时长
    day_dur = defaultdict(float)
    for c in chats:
        msgs = c["messages"]
        if len(msgs) >= 2:
            try:
                d0 = datetime.fromisoformat(msgs[0]["created_at"].replace("Z", "+00:00"))
                d1 = datetime.fromisoformat(msgs[-1]["created_at"].replace("Z", "+00:00"))
                day_dur[msgs[0]["created_at"][:10]] += (d1 - d0).total_seconds() / 3600
            except Exception:
                pass
    max_day_dur = day_dur.get(max_day[0], 0)

    # 时段高峰
    hour_counter = Counter()
    for um in user_msgs:
        if um["time"]:
            hour_counter[(int(um["time"][11:13]) + 8) % 24] += 1
    peak_hour = hour_counter.most_common(1)[0][0] if hour_counter else 0

    # 语长
    lens = [len(um["content"]) for um in user_msgs]
    avg_len = sum(lens) / len(lens) if lens else 0
    max_len = max(lens) if lens else 0

    # 主题统计
    theme_counts = {t: sum(all_text.count(w) for w in words) for t, words in themes.items()}

    # 表情统计
    all_emoji = re.findall(r'[\U0001F600-\U0001F64F\U0001F910-\U0001F9FF]', all_text)
    emoji_counter = Counter(all_emoji)
    pos_cnt = sum(emoji_counter.get(e, 0) for e in pos_emoji)
    neg_cnt = sum(emoji_counter.get(e, 0) for e in neg_emoji)

    # 真实朋友（粗略：常见"朋友/同学"上下文，人工补充）
    friends = len(re.findall(r'(?:朋友|同学)[^。！？]{0,10}(?:牛|曹|曲|马|陈|王|李|张|刘|达|佳|彤)', all_text))

    # 读取模板
    with open(DEFAULT_TEMPLATE, "r", encoding="utf-8") as f:
        template = f.read()

    # 替换占位符
    today = datetime.now().strftime("%Y-%m-%d")
    replacements = {
        "{平台/智能体名称}": "待填写（平台/智能体）",
        "{角色描述}": "待填写",
        "{YYYY-MM-DD}": today,
        "{起}": t_start, "{止}": t_end,
        "{N} 天": f"{n_days} 天",
        "{M} 段": f"{n_chats} 段",
        "{K} 条": f"{n_msgs} 条",
        "{C} 条": f"{n_user} 条",
        "{D} 条": f"{n_user // max(n_days, 1)} 条",
        "{日期}": max_day[0], "{X} 条": f"{max_day[1]} 条", "{H} 小时": f"{max_day_dur:.1f} 小时",
        "{时段}": f"{peak_hour:02d}:00-{peak_hour:02d}:59",
        "{L} 字/条": f"{avg_len:.1f} 字/条", "{MAX} 字": f"{max_len} 字",
        "{N}天": f"{n_days}天", "{K}条消息": f"{n_msgs}条消息",
        "{X}次": f"{pos_cnt}次", "{Y}次": f"{neg_cnt}次",
        "{Z}次": f"{neg_cnt}次", "{A}次": f"{theme_counts.get('战斗/攻击游戏', 0)}次",
        "{B}次": f"{theme_counts.get('脏话/屎尿屁', 0)}次",
        "{F}次": f"{theme_counts.get('幻想伙伴', 0)}次",
        "{P}个": f"{max(friends, 1)}个",
    }
    for k, v in replacements.items():
        template = template.replace(k, v)

    # 主题表格填充
    theme_rows = "\n".join(f"| {t} | {c} | |" for t, c in sorted(theme_counts.items(), key=lambda x: -x[1])[:10])
    template = template.replace("{主题} | {次数} | {观察}", theme_rows)

    # 输出
    if not out_path:
        out_dir = os.path.join(BASE, "..", "output")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"report_{today}.md")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(template)

    print(f"报告框架已生成: {out_path}")
    print("请人工补充定性观察（通读 user_messages.txt 后填写）")


if __name__ == "__main__":
    main()
