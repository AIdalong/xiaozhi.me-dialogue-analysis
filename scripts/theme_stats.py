#!/usr/bin/env python3
"""主题/表情/消息长度统计（主题关键词从 config/themes.json 读取）
用法: python3 scripts/theme_stats.py [data.json]
"""
import json
import os
import re
import sys
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA = os.path.join(BASE, "..", "raw", "all_messages.json")
CONFIG = os.path.join(BASE, "..", "config", "themes.json")


def load_data(path=None):
    path = path or DEFAULT_DATA
    if not os.path.exists(path):
        sys.exit(f"未找到数据文件: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_user_msgs(chats):
    user_msgs = []
    for c in chats:
        for m in c["messages"]:
            if m["role"] == "user":
                user_msgs.append({"time": m.get("created_at", ""), "content": m.get("content", "")})
    user_msgs.sort(key=lambda x: x["time"])
    return user_msgs


def main():
    data_path = sys.argv[1] if len(sys.argv) > 1 else None
    chats = load_data(data_path)
    user_msgs = get_user_msgs(chats)
    all_text = "\n".join(um["content"] for um in user_msgs)

    # 读取主题配置
    with open(CONFIG, "r", encoding="utf-8") as f:
        config = json.load(f)
    themes = config["themes"]

    print("=== 主题词频（用户消息中出现次数）===")
    for theme, words in themes.items():
        cnt = sum(all_text.count(w) for w in words)
        print(f"{theme}: {cnt}")

    # 表情统计
    all_emoji = re.findall(r'[\U0001F600-\U0001F64F\U0001F910-\U0001F9FF]', all_text)
    emoji_counter = Counter(all_emoji)
    pos = config.get("emoji_positive", [])
    neg = config.get("emoji_negative", [])
    pos_cnt = sum(emoji_counter.get(e, 0) for e in pos)
    neg_cnt = sum(emoji_counter.get(e, 0) for e in neg)
    print(f"\n=== 情绪表情统计 ===")
    print(f"积极表情: {pos_cnt}次  ({', '.join(pos[:6])})")
    print(f"消极表情: {neg_cnt}次  ({', '.join(neg[:6])})")
    print("\nTop 15 表情:")
    for e, c in emoji_counter.most_common(15):
        print(f"  {e}: {c}")

    # 平均用户消息长度
    lens = [len(um["content"]) for um in user_msgs]
    if lens:
        print(f"\n用户消息平均字数: {sum(lens)/len(lens):.1f}")
        print(f"最长消息: {max(lens)} 字")
        print(f"最短消息: {min(lens)} 字")
        over20 = sum(1 for l in lens if l >= 20)
        over50 = sum(1 for l in lens if l >= 50)
        print(f">=20字: {over20}条 ({over20/len(lens)*100:.0f}%)")
        print(f">=50字: {over50}条 ({over50/len(lens)*100:.0f}%)")

    # 主动提问
    questions = [um for um in user_msgs if um["content"].strip().endswith(("？", "?"))]
    print(f"\n孩子主动提问: {len(questions)}条")


if __name__ == "__main__":
    main()
