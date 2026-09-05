#!/usr/bin/env python3
"""基础统计：对话数/消息数/时间范围/角色分布/按天统计/对话标题列表
用法: python3 scripts/analyze.py [data.json]
默认读取 raw/all_messages.json
"""
import json
import os
import sys
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA = os.path.join(BASE, "..", "raw", "all_messages.json")


def load_data(path=None):
    path = path or DEFAULT_DATA
    if not os.path.exists(path):
        sys.exit(f"未找到数据文件: {path}\n请先获取数据（见 references/data_format.md）")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    data_path = sys.argv[1] if len(sys.argv) > 1 else None
    chats = load_data(data_path)

    print("=== 总览 ===")
    print(f"对话数: {len(chats)}")
    total_msgs = sum(len(c["messages"]) for c in chats)
    print(f"消息总数: {total_msgs}")

    # 时间范围
    all_times = []
    for c in chats:
        for m in c["messages"]:
            if m.get("created_at"):
                all_times.append(m["created_at"])
    all_times.sort()
    if all_times:
        print(f"最早: {all_times[0]}")
        print(f"最晚: {all_times[-1]}")

    # 用户消息与AI消息
    user_msgs = [m for c in chats for m in c["messages"] if m["role"] == "user"]
    ai_msgs = [m for c in chats for m in c["messages"] if m["role"] == "assistant"]
    tool_msgs = [m for c in chats for m in c["messages"] if m["role"] == "tool"]
    print(f"\n用户消息(孩子): {len(user_msgs)}")
    print(f"AI消息: {len(ai_msgs)}")
    print(f"工具消息: {len(tool_msgs)}")

    # 按天统计
    day_counts = Counter()
    for m in user_msgs:
        day = m["created_at"][:10]
        day_counts[day] += 1
    print(f"\n=== 按天用户消息数 ===")
    for day, cnt in sorted(day_counts.items()):
        print(f"{day}: {cnt}")

    # 对话标题列表（按时间倒序）
    print(f"\n=== 对话标题（按时间倒序）===")
    sorted_chats = sorted(chats, key=lambda c: c["chat"].get("created_at", ""), reverse=True)
    for c in sorted_chats:
        chat = c["chat"]
        title = chat.get("chat_summary", {}).get("title", "无标题") if chat.get("chat_summary") else "无标题"
        created = chat.get("created_at", "")[:16]
        msgs = len(c["messages"])
        print(f"{created} | {msgs:4d}条 | {title}")


if __name__ == "__main__":
    main()
