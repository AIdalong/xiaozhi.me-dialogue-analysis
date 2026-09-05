#!/usr/bin/env python3
"""提取用户消息全文，按对话组织（含 AI 回复摘要）→ transcript.txt
用法: python3 scripts/extract_transcript.py [data.json] [out.txt]
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA = os.path.join(BASE, "..", "raw", "all_messages.json")
DEFAULT_OUT = os.path.join(BASE, "..", "transcript.txt")


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

    sorted_chats = sorted(chats, key=lambda c: c["chat"].get("created_at", ""), reverse=True)

    out_lines = []
    for c in sorted_chats:
        chat = c["chat"]
        title = chat.get("chat_summary", {}).get("title", "无标题") if chat.get("chat_summary") else "无标题"
        created = chat.get("created_at", "")[:16]
        out_lines.append(f"\n{'='*60}")
        out_lines.append(f"【对话】{title} | {created} | {len(c['messages'])}条")
        out_lines.append(f"{'='*60}")
        for m in c["messages"]:
            t = m.get("created_at", "")[11:19]
            role = m["role"]
            content = m.get("content", "")
            if role == "user":
                out_lines.append(f"\n[孩子 {t}] {content}")
            elif role == "assistant":
                out_lines.append(f"[AI {t}] {content[:80]}{'...' if len(content) > 80 else ''}")
            # tool 消息跳过

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))

    print(f"已保存 {out_path}，共 {len(out_lines)} 行")


if __name__ == "__main__":
    main()
