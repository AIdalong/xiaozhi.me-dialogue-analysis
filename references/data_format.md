# 数据格式说明

本 skill 分析的核心数据文件是 `raw/all_messages.json`，结构如下。

## all_messages.json 顶层结构

```json
[
  {
    "chat": { ... 对话元信息 ... },
    "messages": [ ... 该对话的所有消息 ... ]
  },
  {
    "chat": { ... },
    "messages": [ ... ]
  }
]
```

一个数组，每个元素代表**一段对话**（session），包含对话元信息 `chat` 和消息列表 `messages`。

## chat 对象（对话元信息）

```json
{
  "id": 80104817,
  "chat_id": "53d59faf-7dd9-49b0-891d-9ced201661f6",
  "created_at": "2026-08-31T04:55:53.000Z",
  "chat_summary": {
    "title": "对话标题（AI 自动生成）"
  }
}
```

- `id` / `chat_id`：对话 ID
- `created_at`：对话创建时间（ISO 8601，UTC）
- `chat_summary.title`：对话标题（可选）

## message 对象（消息）

```json
{
  "id": 3220939701,
  "role": "user" | "assistant" | "tool",
  "content": "消息文本内容",
  "created_at": "2026-08-31T04:55:53.000Z"
}
```

- `role`：
  - `user`：孩子的发言（语音转写文本）
  - `assistant`：AI 助手的回复
  - `tool`：工具调用消息（分析时可跳过）
- `content`：文本内容。对于语音助手，是 ASR 语音识别结果
- `created_at`：消息时间（ISO 8601，UTC）

## 其他字段（可选）

不同平台的导出可能包含额外字段，如：
- `message_id` / `uuid`
- `role` 为 `tool` 时的 `tool_calls`、`tool_call_id`
- `media` / `audio_url`（语音文件 URL，通常无需分析）

分析脚本只依赖 `role`、`content`、`created_at` 三个字段，其他字段会忽略。

## 时区说明

- 时间字段通常为 **UTC**（如 `2026-08-31T04:55:53.000Z`）
- 脚本 `time_analysis.py` 会转换为北京时间（UTC+8）做时段分布
- 注意：对话里孩子说的"早上""晚上"可能指本地时间，看原始时间戳要留意时区

## 如何获取数据

### 方式 A：浏览器控制台抓取（如 xiaozhi.me）

1. 登录 AI 助手控制台（如 `https://xiaozhi.me/console/agents`）
2. 找到孩子实际使用的智能体
3. 打开 DevTools（F12），在 Console 中执行：

```js
// 以 xiaozhi.me 为例，实际接口以控制台为准
// 1. 获取对话列表
const token = localStorage.getItem('token');  // 或从请求头获取
const chatsRes = await fetch('/api/agents/{YOUR_AGENT_ID}/chats?page=1&pageSize=50', {
  headers: { 'Authorization': 'Bearer ' + token }
});
const chats = (await chatsRes.json()).data;

// 2. 拉取每个对话的消息
const allData = [];
for (const c of chats) {
  const msgsRes = await fetch(`/api/chats/messages?chatId=${c.id}&page=1&pageSize=50&includeTools=1&order=asc`, {
    headers: { 'Authorization': 'Bearer ' + token }
  });
  const msgs = (await msgsRes.json()).data?.list || [];
  allData.push({ chat: c, messages: msgs });
}

// 3. 存入 window 供 CDP 导出
window.__allChats = allData;
window.__allChatsJson = JSON.stringify(allData);
```

4. 用 `scripts/export_cdp.js` 通过 CDP 导出到本地

> ⚠️ 实际接口、分页方式、token 存储位置因平台而异，需要现场确认。chats 接口可能忽略分页、只返回最新 N 个对话。

### 方式 B：已有导出文件

如果你有平台导出的数据（可能是 CSV、JSON、txt），需要先转换为上述格式。常见转换：
- 有 `role/content/created_at` 字段的 JSON → 直接重组为上述结构
- 纯文本对话记录 → 需按说话人切分，生成 messages

## 数据完整性检查

- 检查 `analyze.py` 输出的对话数、消息数是否与平台显示一致
- 检查时间范围是否覆盖了你期望的全部历史
- 若 chats 接口只返回最新 50 个对话，确认是否有更早数据遗漏
