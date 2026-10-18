// 志光 ai.highstudy.com.tw 課程字幕抓取（在 Claude in Chrome 的 javascript_tool 執行）
// 用法：先在課程清單頁（/zh/program/{id}）或播放頁（/playlist）貼上本檔全文定義 window.__grab，
//       之後每次只抓一講：JSON.stringify(await window.__grab('憲法', '115律師-憲法A(陸伯言)-', '04'))
// 結果：Chrome 下載 {科目}{NN}.html 到「下載」資料夾（只留時間與字幕，約 0.3～0.5MB），回傳句數與首末時間。
// 規則：只點影片項目、不點「-測驗」；抓到 0 句就不下載；一講一呼叫、間隔幾秒（連抓太快網站曾進維護頁）。
window.__grab = async function (subject, prefix, nn) {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const name = prefix + nn;
  const it = [...document.querySelectorAll('*')].find(e => e.children.length === 0 && e.textContent.trim() === name);
  if (!it) return {nn, err: 'item not found'};
  it.click();
  for (let i = 0; i < 10 && !document.title.endsWith(name); i++) await sleep(500);
  if (!document.title.endsWith(name)) return {nn, err: 'title ' + document.title};
  await sleep(1500);
  document.querySelectorAll('video').forEach(v => v.pause());
  const count = () => document.querySelectorAll('div.css-10s8ss9').length;
  let n = 0, prev = -1;
  for (let i = 0; i < 20; i++) {
    if (i % 5 === 0 && count() === 0) {
      const t = [...document.querySelectorAll('button,[role=tab]')].find(b => b.innerText.trim() === '字幕');
      t && t.click();
    }
    await sleep(1000); n = count(); if (n > 0 && n === prev) break; prev = n;
  }
  document.querySelectorAll('video').forEach(v => v.pause());
  if (!n) return {nn, err: 'no subtitles loaded'};
  const esc = s => s.replace(/[&<>]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;'}[c]));
  const boxes = [...document.querySelectorAll('div.css-10s8ss9')];
  const rows = boxes.map(b => {
    const p = b.querySelectorAll('p');
    return `<div class="css-10s8ss9"><p>${esc(p[0]?.innerText.trim() || '')}</p><p>${esc((p[1]?.innerText || '').replace(/\s+/g, ' ').trim())}</p></div>`;
  });
  const html = `<!doctype html>\n<html lang="zh-Hant"><head><meta charset="utf-8"><title>${subject}${nn}</title></head><body>\n<!-- ${name}；${location.href} -->\n` + rows.join('\n') + '\n</body></html>\n';
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([html], {type: 'text/html'}));
  a.download = subject + nn + '.html';
  document.body.appendChild(a); a.click(); a.remove();
  return {nn, cues: boxes.length, first: boxes[0]?.querySelector('p')?.innerText, last: boxes.at(-1)?.querySelector('p')?.innerText};
};
