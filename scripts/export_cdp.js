// 通过 CDP 从浏览器导出 window.__chunks（或 window.__allChatsJson）到本地文件
// 用法: node scripts/export_cdp.js <ws_url> [out_file]
//   ws_url: 浏览器页面的 DevTools WebSocket 地址
//           （在浏览器控制台运行 window.location 或从 chrome://inspect 获取）
//   默认读取 window.__chunks（分块），fallback 到 window.__allChatsJson（整体）
const WebSocket = require('ws');
const path = require('path');
const fs = require('fs');

const WS_URL = process.argv[2];
if (!WS_URL) {
  console.error('用法: node scripts/export_cdp.js <ws_url> [out_file]');
  console.error('  ws_url 形如: ws://127.0.0.1:18800/devtools/page/XXXX');
  process.exit(1);
}

const OUT_FILE = process.argv[3] || path.join(__dirname, '..', 'raw', 'all_messages.json');
fs.mkdirSync(path.dirname(OUT_FILE), { recursive: true });

const ws = new WebSocket(WS_URL);
let msgId = 0;
const pending = new Map();

function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = ++msgId;
    pending.set(id, { resolve, reject });
    ws.send(JSON.stringify({ id, method, params }));
  });
}

ws.on('message', (data) => {
  const msg = JSON.parse(data.toString());
  if (msg.id && pending.has(msg.id)) {
    const { resolve, reject } = pending.get(msg.id);
    pending.delete(msg.id);
    if (msg.error) reject(new Error(JSON.stringify(msg.error)));
    else resolve(msg.result);
  }
});

async function main() {
  await new Promise((res) => ws.on('open', res));
  console.log('CDP connected');

  // 检查分块是否存在
  const numRes = await send('Runtime.evaluate', {
    expression: 'window.__chunks ? window.__chunks.length : (window.__allChatsJson ? -1 : 0)',
    returnByValue: true
  });
  const numChunks = numRes.result.value;
  console.log('numChunks:', numChunks);

  let allJson;
  if (numChunks > 0) {
    // 分块模式：逐块取回拼接
    allJson = '';
    for (let i = 0; i < numChunks; i++) {
      const res = await send('Runtime.evaluate', {
        expression: `window.__chunks[${i}]`,
        returnByValue: true
      });
      const chunk = res.result.value;
      allJson += chunk;
      console.log(`chunk ${i + 1}/${numChunks} len=${chunk ? chunk.length : 0}`);
    }
  } else if (numChunks === -1) {
    // 整体 JSON 模式
    const res = await send('Runtime.evaluate', {
      expression: 'window.__allChatsJson',
      returnByValue: true
    });
    allJson = res.result.value;
    console.log(`allChatsJson len=${allJson ? allJson.length : 0}`);
  } else {
    console.error('浏览器中未找到 window.__chunks 或 window.__allChatsJson');
    console.error('请在页面控制台先抓取数据并存入 window 变量（见 references/data_format.md）');
    process.exit(1);
  }

  // 验证是合法 JSON
  const parsed = JSON.parse(allJson);
  console.log('Parsed OK, chats:', parsed.length);
  const msgCount = parsed.reduce((a, c) => a + (c.messages ? c.messages.length : 0), 0);
  console.log('Total messages:', msgCount);

  fs.writeFileSync(OUT_FILE, allJson, 'utf-8');
  console.log('Saved to', OUT_FILE);
  process.exit(0);
}

main().catch((e) => { console.error('ERROR:', e); process.exit(1); });
