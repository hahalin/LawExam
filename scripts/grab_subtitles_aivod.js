// 金榜函授 easylearn2.aivod.com.tw 課程字幕抓取（在 Claude in Chrome 的 javascript_tool 執行）
// 用法：在課程頁（/courses/2/{課程代碼}）貼上本檔全文，定義 window.__lessons 與 window.__grab。
//   JSON.stringify(window.__lessons())                 → 列出每堂：編號、名稱、分鐘、進度
//   JSON.stringify(await window.__grab(9, '公司法-江赫')) → 切到第 09 堂、等字幕載完、下載「公司法-江赫09.html」
//   跳下一課＝下一次呼叫 __grab(10, …)；一堂一呼叫，中間隔幾秒。
// 輸出 html 沿用舊站結構 <div class="css-10s8ss9"><p>HH:MM:SS - HH:MM:SS</p><p>字幕</p></div>，
// convert_subtitle.py 不用改。新站每句只有起始時間：結束時間取下一句的起始時間，最後一句起訖相同。
// 切課不改網址；點下去影片會從上次看到的位置開始播，腳本每 0.5 秒暫停一次。
window.__lessons = function () {
  return [...document.querySelectorAll('li.unit-item')].map(li => {
    const title = li.querySelector('.unit-title')?.textContent.trim() || '';
    return {
      n: +(title.match(/第(\d+)堂/) || [])[1] || null,
      title,
      min: +((li.querySelector('.unit-meta')?.textContent || '').match(/(\d+)\s*分鐘/) || [])[1] || null,
      progress: (li.querySelector('.unit-progress')?.textContent || '').replace(/\s/g, ''),
    };
  });
};

window.__grab = async function (n, subject, opt = {}) {  // opt.dl === false：只切課、驗證字幕，不下載
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const nn = String(n).padStart(2, '0');
  const pause = () => document.querySelectorAll('video').forEach(v => v.pause());
  const li = [...document.querySelectorAll('li.unit-item')]
    .find(e => +((e.querySelector('.unit-title')?.textContent || '').match(/第(\d+)堂/) || [])[1] === n);
  if (!li) return {nn, err: 'lesson not found'};
  const title = li.querySelector('.unit-title').textContent.trim();
  const min = +((li.querySelector('.unit-meta')?.textContent || '').match(/(\d+)\s*分鐘/) || [])[1] || null;
  const playingNo = () => {
    const el = [...document.querySelectorAll('*')].find(e => e.children.length === 0 && /正在播放/.test(e.textContent));
    return +((el?.parentElement?.innerText || '').match(/第(\d+)堂/) || [])[1] || null;
  };
  const items = () => document.querySelectorAll('.subtitle-list .subtitle-item');
  const sig = () => { const it = items(); return it.length + '|' + (it[0]?.innerText || '') + '|' + (it[it.length - 1]?.innerText || ''); };
  const openTab = () => {
    const t = [...document.querySelectorAll('button.p-tab,[role=tab]')].find(b => b.innerText.trim() === '字幕小幫手');
    if (t && !t.classList.contains('p-tab-active')) t.click();
  };
  openTab();
  const before = sig();
  const already = playingNo() === n && items().length > 0;
  if (!already) li.click();
  let prev = '', stable = 0;
  for (let i = 0; i < 60 && stable < 3; i++) {
    await sleep(500); pause();
    if (i % 6 === 5 && items().length === 0) openTab();
    if (playingNo() !== n) continue;
    const s = sig();
    if (!already && s === before) continue;
    stable = (s === prev && items().length > 0) ? stable + 1 : 0;
    prev = s;
  }
  pause();
  if (playingNo() !== n) return {nn, err: 'not switched, playing ' + playingNo()};
  if (stable < 3) return {nn, err: 'subtitles not stable', count: items().length};
  const hms = t => { const p = t.trim().split(':').map(x => x.padStart(2, '0')); while (p.length < 3) p.unshift('00'); return p.join(':'); };
  const esc = s => s.replace(/[&<>]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;'}[c]));
  const cues = [...items()].map(it => ({
    t: hms(it.querySelector('.time-code')?.textContent || '0:00:00'),
    x: (it.querySelector('.text')?.textContent || '').replace(/\s+/g, ' ').trim(),
  })).filter(c => c.x);
  if (!cues.length) return {nn, err: 'no subtitles'};
  const info = {nn, title, min, cues: cues.length, first: cues[0].t, last: cues.at(-1).t};
  if (opt.dl === false) return info;
  const rows = cues.map((c, i) => `<div class="css-10s8ss9"><p>${c.t} - ${(cues[i + 1] || c).t}</p><p>${esc(c.x)}</p></div>`);
  const html = `<!doctype html>\n<html lang="zh-Hant"><head><meta charset="utf-8"><title>${subject}${nn}</title></head><body>\n` +
    `<!-- ${title}；${min} 分鐘；${location.href}；結束時間＝下一句起始時間 -->\n` + rows.join('\n') + '\n</body></html>\n';
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([html], {type: 'text/html'}));
  a.download = subject + nn + '.html';
  document.body.appendChild(a); a.click(); a.remove();
  return {...info, file: a.download};
};
