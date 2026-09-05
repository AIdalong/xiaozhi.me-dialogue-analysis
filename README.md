# 🍇 Child AI Dialogue Analysis

> 分析儿童与 AI 语音助手的对话记录，评估孩子的语言发展、心理状态、兴趣主题与成长状态。**家长观察工具，不是医学诊断。**

一个开源的 OpenClaw/Claude skill：从 AI 助手控制台（如小智 xiaozhi.me「随身」智能体）提取孩子与 AI 的聊天记录，结合量化统计与人工阅读，输出一份客观、建设性的儿童成长观察报告。

本项目源于一次真实的亲子分析：一位爸爸想了解 5 岁儿子和 AI 语音助手的 6000+ 条对话里，藏着怎样的心理与成长状态。我们把整个过程沉淀成了这个可复用的 skill。

---

## ✨ 功能

- **数据抓取**：通过浏览器/CDP 从 AI 助手控制台批量提取对话记录
- **量化分析**：主题词频、情绪表情、语言长度、时间分布、行为模式（规则意识/社交/照顾/死亡游戏等）
- **定性分析框架**：基于儿童发展心理学的解读原则，区分「正常发展」「亮点」「需要留意」
- **结构化报告**：语言发展 / 心理发展 / 兴趣图谱 / 成长里程碑 / 给家长的建议
- **隐私友好**：报告自动脱敏建议，避免暴露真实身份

## 📦 安装

作为 OpenClaw skill 使用：

```bash
# 克隆到 workspace/skills/
git clone https://github.com/<your-org>/child-ai-dialogue-analysis.git \
  ~/.openclaw/workspace/skills/child-ai-dialogue-analysis
```

依赖：Python 3.8+（标准库即可，无需第三方包）、Node.js（仅 CDP 导出脚本需要，可选）。

## 🚀 快速开始

### 1. 获取数据

**方式 A：浏览器控制台抓取（如 xiaozhi.me）**

1. 用浏览器打开 `https://xiaozhi.me/console/agents` 并登录
2. 定位孩子实际使用的智能体（看活跃度、角色、设备绑定）
3. 在 DevTools Console 中执行脚本，把数据存到 `window.__allChats`（见 `references/data_format.md`）
4. 用 CDP 导出：

```bash
# 修改 export_cdp.js 里的 WS_URL 为你的页面 WebSocket 地址
node scripts/export_cdp.js   # → raw/all_messages.json
```

**方式 B：已有数据**

把数据按 `references/data_format.md` 的格式放入 `raw/all_messages.json`。

### 2. 分析

```bash
cd child-ai-dialogue-analysis

# 基础统计 + 提取文本
python3 scripts/analyze.py
python3 scripts/extract_user_msgs.py      # → user_messages.txt（孩子的原话）
python3 scripts/extract_transcript.py     # → transcript.txt（完整对话）

# 量化分析
python3 scripts/theme_stats.py
python3 scripts/behavior_stats.py
python3 scripts/time_analysis.py

# 生成报告框架
python3 scripts/report_generator.py
```

### 3. 阅读与撰写

1. **通读 `user_messages.txt`**（孩子的原话）——这是最关键的步骤
2. 参考 `references/child_psychology.md` 的框架进行定性判断
3. 基于 `templates/report_template.md` 撰写报告

## 📁 目录结构

```
child-ai-dialogue-analysis/
├── SKILL.md                 # skill 使用说明（OpenClaw 读取）
├── README.md
├── LICENSE                  # MIT
├── config/
│   └── themes.json          # 主题关键词配置（可自定义）
├── references/
│   ├── child_psychology.md  # 儿童发展心理学评估框架
│   ├── data_format.md       # 数据格式说明
│   └── interpretation.md    # 解读原则与警示信号
├── scripts/
│   ├── analyze.py
│   ├── extract_user_msgs.py
│   ├── extract_transcript.py
│   ├── theme_stats.py
│   ├── behavior_stats.py
│   ├── time_analysis.py
│   ├── report_generator.py
│   └── export_cdp.js
├── templates/
│   └── report_template.md
└── examples/
    └── sample_report.md     # 脱敏示例
```

## 🧠 核心解读原则

| 孩子的表现 | 发展阶段 | 家长建议 |
|---|---|---|
| "屎尿屁"脏话 | 3-6岁污言秽语期 | 正常，不干预 |
| 战斗幻想/"打死怪兽" | 象征性游戏 | 正常，区分幻想与现实 |
| 计较输赢、自己定规则 | 认知过渡期 | 引导规则游戏（棋类） |
| 幻想伙伴 | 情感联结需求 | 关注陪伴，多亲子互动 |
| 同音错字 | 语音发展后期 | 6岁后仍明显再咨询 |
| 生气后快速恢复 | 情绪弹性好 | 正向肯定 |

**需真正留意的信号**（需结合上下文）：持续严重负面情绪、反复害怕且影响生活、幻想与现实长期混淆、完全没有真实同伴、单日使用 AI 过长（建议 ≤1-2 小时且大人陪伴）。

## ⚠️ 重要声明

- **不是诊断工具**。本 skill 帮助家长观察与理解，不提供医学/心理学诊断。
- **尊重隐私**：只分析你拥有合法访问权的数据（自己的孩子/家人）。报告避免真实姓名、手机号、地址、学校。
- **理解 ASR 误差**：语音转写可能有错字，判断语言能力要结合上下文。
- **AI 的局限**：AI 助手无限迁就孩子，孩子需要真实社交反馈。请确保孩子有足够的真实同伴互动。

## 🛠️ 自定义

- 主题关键词：编辑 `config/themes.json`
- 报告结构：编辑 `templates/report_template.md`
- 解读框架：编辑 `references/child_psychology.md`

## 📄 License

[MIT](LICENSE)

## 🙏 致谢

由一次真实的亲子 AI 对话分析实践沉淀而来。感谢那个 5 岁小男孩和他充满想象力的世界——愿所有孩子都能被理解、被陪伴、被爱。🍇
