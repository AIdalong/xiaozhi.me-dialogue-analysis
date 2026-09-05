#!/usr/bin/env python3
"""提取纯用户消息（孩子的话），带时间戳，按时间正序 → user_messages.txt
用法: python3 scripts/extract_user_msgs.py [data.json] [out.txt]
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA = os.path.join(BASE, "..", "raw", "all_messages.json")
DEFAULT_OUT = os.path.join(BASE, "..", "user_messages.txt")


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
    out_path = out_path or DEFAULT_OUT

    user_msgs = []
    for c in chats:
        for m in c["messages"]:
            if m["role"] == "user":
                user_msgs.append({
                    "time": m.get("created_at", ""),
                    "content": m.get("content", ""),
                })
    user_msgs.sort(key=lambda x: x["time"])

    out_lines = [f"[{um['time'][:19]}] {um['content']}" for um in user_msgs]

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))

    print(f"共 {len(user_msgs)} 条用户消息")
    print(f"已保存: {out_path}")
    print("前10条:")
    for l in out_lines[:10]:
        print(l)


if __name__ == "__main__":
    main()
