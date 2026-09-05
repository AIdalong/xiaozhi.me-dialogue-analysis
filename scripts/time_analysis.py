#!/usr/bin/env python3
"""时间分布与情绪趋势分析
用法: python3 scripts/time_analysis.py [data.json]
"""
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA = os.path.join(BASE, "..", "raw", "all_messages.json")
TZ_OFFSET = 8  # 北京时区偏移（UTC+8），可按需修改


def load_data(path=None):
    path = path or DEFAULT_DATA
    if not os.path.exists(path):
        sys.exit(f"未找到数据文件: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    data_path = sys.argv[1] if len(sys.argv) > 1 else None
    chats = load_data(data_path)

    print("=== 每天对话时长与消息量 ===")
    day_stats = defaultdict(lambda: {"msgs": 0, "duration_min": 0, "sessions": 0})
    for c in chats:
        msgs = c["messages"]
        if not msgs:
            continue
        t0 = msgs[0].get("created_at", "")
        t1 = msgs[-1].get("created_at", "")
        if t0 and t1:
            try:
                d0 = datetime.fromisoformat(t0.replace("Z", "+00:00"))
                d1 = datetime.fromisoformat(t1.replace("Z", "+00:00"))
                dur = (d1 - d0).total_seconds() / 60
                day = t0[:10]
                day_stats[day]["duration_min"] += dur
                day_stats[day]["sessions"] += 1
            except Exception:
                pass
        for m in msgs:
            if m["role"] == "user":
                day_stats[m["created_at"][:10]]["msgs"] += 1

    for day in sorted(day_stats.keys()):
        s = day_stats[day]
        print(f"{day}: {s['msgs']}条用户消息, {s['sessions']}段对话, "
              f"估算时长 {s['duration_min']:.0f}分钟 ({s['duration_min']/60:.1f}小时)")

    print("\n=== 时段分布（用户消息，本地时间）===")
    hour_counter = Counter()
    for c in chats:
        for m in c["messages"]:
            if m["role"] == "user" and m.get("created_at"):
                hour = (int(m["created_at"][11:13]) + TZ_OFFSET) % 24
                hour_counter[hour] += 1
    for h in range(24):
        if hour_counter[h] > 0:
            print(f"{h:02d}:00-{h:02d}:59 {hour_counter[h]}条")

    print("\n=== 每天平均消息长度（语言复杂度参考）===")
    day_len = defaultdict(list)
    for c in chats:
        for m in c["messages"]:
            if m["role"] == "user" and m.get("created_at") and m.get("content"):
                day_len[m["created_at"][:10]].append(len(m["content"]))
    for day in sorted(day_len.keys()):
        lens = day_len[day]
        median = sorted(lens)[len(lens) // 2]
        print(f"{day}: 平均 {sum(lens)/len(lens):.1f} 字, 中位数 {median} 字")

    print("\n=== 负面情绪消息样本（😡😔等）===")
    neg_emojis = set("😡😠😔😢😭😱😨😤💢")
    neg_msgs = []
    for c in chats:
        for m in c["messages"]:
            if m["role"] == "user" and any(e in m["content"] for e in neg_emojis):
                neg_msgs.append((m["created_at"], m["content"]))
    neg_msgs.sort()
    for t, content in neg_msgs[:30]:
        print(f"[{t[:16]}] {content}")


if __name__ == "__main__":
    main()
