#!/usr/bin/env python3
"""行为模式统计：规则意识/社交/情绪/照顾/死亡游戏/提问能力等
用法: python3 scripts/behavior_stats.py [data.json]
"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA = os.path.join(BASE, "..", "raw", "all_messages.json")


def load_data(path=None):
    path = path or DEFAULT_DATA
    if not os.path.exists(path):
        sys.exit(f"未找到数据文件: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    data_path = sys.argv[1] if len(sys.argv) > 1 else None
    chats = load_data(data_path)

    user_msgs = []
    for c in chats:
        for m in c["messages"]:
            if m["role"] == "user":
                user_msgs.append({"time": m["created_at"], "content": m["content"]})
    user_msgs.sort(key=lambda x: x["time"])
    all_text = "\n".join(um["content"] for um in user_msgs)

    def count(words):
        return sum(all_text.count(w) for w in words)

    print("=== 行为模式统计 ===")
    print(f"规则/输赢相关词: {count(['犯规', '规则', '不行', '不对', '你输了', '我赢了', '你错了', '作弊'])}次")
    print(f"社交情感表达: {count(['好朋友', '朋友', '我喜欢', '我爱你', '亲亲', '抱抱', '一起玩', '陪我', '永远'])}次")
    print(f"对AI负面表达: {count(['你傻', '你脑子', '神经病', '滚蛋', '揍死', '打死你', '拜拜', '不跟你玩', '讨厌'])}次")
    print(f"家庭相关词: {count(['妈妈', '爸爸', '奶奶', '爷爷', '妹妹', '哥哥', '我们家', '我家', '上学', '幼儿园'])}次")
    print(f"照顾/帮助行为词: {count(['照顾', '救', '帮', '喂', '保护', '包扎', '创可贴', '关心', '别怕', '没事的'])}次")

    nums = re.findall(r'\d+', all_text)
    print(f"数字出现: {len(nums)}次")

    ono = ["嘣", "砰", "轰", "嗖", "滋", "咻", "咚", "咔嚓", "咕噜", "滴滴", "嗡嗡"]
    print(f"拟声词: {count(ono)}次")

    questions = [um for um in user_msgs if um["content"].strip().endswith(("？", "?"))]
    print(f"孩子主动提问: {len(questions)}条")

    print("\n高频游戏术语:")
    for w in ["狗屎", "炸弹", "变身", "分身", "隐身", "合体", "闪电", "火焰",
              "冲击", "大战", "怪兽", "坏蛋", "钥匙", "捉迷藏", "迷宫", "比赛",
              "超神", "巨神", "超人", "超级"]:
        print(f"  {w}: {all_text.count(w)}次")

    print("\n自称/身份:")
    for w in ["哥哥", "大王", "超人", "战神", "队长", "我赢", "第一名", "高手"]:
        print(f"  {w}: {all_text.count(w)}次")

    death_msgs = [um["content"] for um in user_msgs
                  if any(w in um["content"] for w in ["打死", "杀死", "死了", "弄死", "打扁", "炸死"])]
    print(f"\n包含死亡/消灭表达的消息: {len(death_msgs)}条")
    if death_msgs:
        print("样例:")
        for d in death_msgs[:5]:
            print(f"  - {d[:60]}")


if __name__ == "__main__":
    main()
