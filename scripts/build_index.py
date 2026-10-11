"""產生 repo 根目錄 index.html（GitHub Pages 首頁）：各科、各課分節，列出課程字幕 md、ELI5 網頁、分主題筆記 md。
用法：python scripts/build_index.py
md 檔連到 GitHub 頁面（才有 markdown 排版）；ELI5 用相對路徑在 Pages 上開。"""
import os, re, html, urllib.parse as up
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOB = 'https://github.com/hahalin/LawExam/blob/master/'
SUBJECTS = [('民法', '民法', '民法'), ('強制執行法', '強制執行法', '')]  # (資料夾, 顯示名, 檔名前綴)

def q(p): return up.quote(p)
def esc(s): return html.escape(s, quote=True)
def eli5_sub(path):
    t = open(path, encoding='utf-8').read()
    m = re.search(r'<span class="sub">(.*?)</span>', t, re.S)
    return re.sub('<[^>]+>', '', m.group(1)).strip() if m else ''

def lessons(d, prefix):
    base = f'課程字幕/{d}'
    fs = os.listdir(os.path.join(ROOT, base))
    nums = sorted({m.group(1) for f in fs for m in [re.match(re.escape(prefix) + r'(\d\d)\.md$', f)] if m})
    for n in nums:
        eli = f'{prefix}{n}-ELI5.html'
        notes = []
        for f in sorted(fs):
            m = re.match(re.escape(prefix) + n + r'-筆記-(\d\d)-(.*)\.md$', f)
            if m: notes.append((m.group(1), m.group(2), f'{base}/{f}'))
        yield dict(n=n, base=base, sub_md=f'{base}/{prefix}{n}.md', sub_name=f'{prefix}{n}.md',
                   eli=f'{base}/{eli}' if eli in fs else None,
                   theme=eli5_sub(os.path.join(ROOT, base, eli)) if eli in fs else '', notes=notes)

import json
data = []
for d, label, prefix in SUBJECTS:
    ls = []
    for l in lessons(d, prefix):
        ls.append(dict(n=l['n'], theme=l['theme'],
                       sub=dict(name=l['sub_name'], url=BLOB + q(l['sub_md'])),
                       eli=q(l['eli']) if l['eli'] else None,
                       notes=[dict(no=no, t=t, url=BLOB + q(p)) for no, t, p in l['notes']]))
    data.append(dict(id=d, label=label, lessons=ls))
DATA = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')

page = r"""<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>司律課程筆記</title>
<style>
:root{--bg:#f7f7f4;--side:#efefea;--fg:#1f2328;--mu:#646a71;--card:#fff;--line:#e2e2dc;--acc:#2f6f8f;--acc-bg:#e3eef3;--tab:#e9e9e4}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#15171a;--side:#1a1d20;--fg:#e6e6e3;--mu:#9a9fa5;--card:#1f2225;--line:#32363a;--acc:#7fb6d1;--acc-bg:#1d3440;--tab:#25292d}}
:root[data-theme="dark"]{--bg:#15171a;--side:#1a1d20;--fg:#e6e6e3;--mu:#9a9fa5;--card:#1f2225;--line:#32363a;--acc:#7fb6d1;--acc-bg:#1d3440;--tab:#25292d}
*{box-sizing:border-box}
html,body{height:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.65 system-ui,"Noto Sans TC","PingFang TC",sans-serif;display:flex}
aside{width:200px;flex:none;background:var(--side);border-right:1px solid var(--line);padding:20px 12px;position:sticky;top:0;height:100vh;overflow-y:auto}
aside h1{font-size:1.05rem;margin:0 8px 16px}
aside button{display:flex;justify-content:space-between;align-items:center;width:100%;text-align:left;border:0;background:none;color:var(--fg);font:inherit;padding:8px 10px;border-radius:8px;cursor:pointer;margin-bottom:2px}
aside button small{color:var(--mu);font-size:.8rem}
aside button:hover{background:var(--tab)}
aside button[aria-selected="true"]{background:var(--acc-bg);color:var(--acc);font-weight:600}
aside button[aria-selected="true"] small{color:var(--acc)}
.foot{color:var(--mu);font-size:.78rem;margin:20px 8px 0;line-height:1.5}
.main{flex:1;min-width:0;display:flex;flex-direction:column}
.tabs{flex:none;position:sticky;top:0;z-index:3;background:var(--bg);border-bottom:1px solid var(--line);padding:14px 24px 0;display:flex;gap:4px;overflow-x:auto;scrollbar-width:thin}
.tabs button{flex:none;border:1px solid var(--line);border-bottom:0;background:var(--tab);color:var(--mu);font:inherit;font-size:.92rem;font-variant-numeric:tabular-nums;padding:6px 14px;border-radius:8px 8px 0 0;cursor:pointer;position:relative;top:1px}
.tabs button:hover{color:var(--fg)}
.tabs button.has{color:var(--fg)}
.tabs button[aria-selected="true"]{background:var(--card);color:var(--acc);font-weight:600;border-color:var(--line);border-bottom:1px solid var(--card)}
.panel{padding:24px;max-width:880px}
.sheet{background:var(--card);border:1px solid var(--line);border-radius:0 10px 10px 10px;padding:20px 22px}
.sheet h2{margin:0;font-size:1.3rem}
.theme{margin:4px 0 14px;color:var(--mu)}
.pills{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:6px}
.pill{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:4px 14px;font-size:.92rem;text-decoration:none;color:var(--fg)}
.pill:hover{border-color:var(--acc);color:var(--acc)}
.pill.eli{background:var(--acc-bg);border-color:transparent;color:var(--acc);font-weight:600}
.pill.off{color:var(--mu);border-style:dashed}
h3{font-size:.92rem;color:var(--mu);font-weight:600;margin:18px 0 6px}
ol{list-style:none;margin:0;padding:0}
ol li{border-top:1px solid var(--line)} ol li:first-child{border-top:0}
ol a{display:flex;gap:12px;padding:8px 2px;color:var(--fg);text-decoration:none;font-size:.95rem;line-height:1.55;overflow-wrap:anywhere}
ol a b{color:var(--acc);font-variant-numeric:tabular-nums;flex:none}
ol a:hover{color:var(--acc)}
.none{color:var(--mu);margin:14px 0 0}
@media (max-width:720px){
  body{flex-direction:column}
  aside{width:auto;height:auto;position:static;border-right:0;border-bottom:1px solid var(--line);padding:12px 16px;display:flex;gap:6px;align-items:center;overflow-x:auto}
  aside h1{display:none} .foot{display:none}
  #subjects{display:flex;gap:6px}
  aside button{width:auto;flex:none;margin:0;gap:8px}
  .tabs{padding:10px 16px 0}
  .panel{padding:16px}
  .sheet{padding:16px}
}
</style></head><body>
<aside><h1>司律課程筆記</h1><div id="subjects" role="tablist" aria-label="科目"></div>
<p class="foot">字幕、筆記連到 GitHub 檢視；ELI5 在本站開。「懂了」勾選只存在各裝置的瀏覽器。</p></aside>
<div class="main"><nav class="tabs" id="tabs" role="tablist" aria-label="課堂"></nav>
<div class="panel"><div class="sheet" id="sheet" role="tabpanel"></div></div></div>
<script>
const DATA = __DATA__;
const $ = id => document.getElementById(id);
const esc = s => s.replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
let cur = {s: 0, l: 0};
function defaultLesson(si){ const ls = DATA[si].lessons; for (let i = ls.length - 1; i >= 0; i--) if (ls[i].notes.length) return i; return 0; }
function renderSubjects(){
  $('subjects').innerHTML = DATA.map((s, i) =>
    `<button role="tab" aria-selected="${i===cur.s}" data-i="${i}">${esc(s.label)}<small>${s.lessons.length} 講</small></button>`).join('');
}
function renderTabs(){
  const ls = DATA[cur.s].lessons;
  $('tabs').innerHTML = ls.map((l, i) =>
    `<button role="tab" class="${l.notes.length ? 'has' : ''}" aria-selected="${i===cur.l}" data-i="${i}" title="${esc(l.theme || '')}">${l.n}</button>`).join('');
  const b = $('tabs').querySelector('[aria-selected="true"]'); if (b) b.scrollIntoView({block:'nearest', inline:'nearest'});
}
function renderSheet(){
  const s = DATA[cur.s], l = s.lessons[cur.l];
  const pills = [`<a class="pill" href="${l.sub.url}">📄 課程字幕 ${esc(l.sub.name)}</a>`,
    l.eli ? `<a class="pill eli" href="${l.eli}">🌐 ELI5 網頁</a>` : `<span class="pill off">ELI5 尚未製作</span>`];
  const notes = l.notes.length
    ? `<h3>分主題筆記 ${l.notes.length} 份</h3><ol>${l.notes.map(n => `<li><a href="${n.url}"><b>${n.no}</b>${esc(n.t)}</a></li>`).join('')}</ol>`
    : `<p class="none">分主題筆記尚未製作</p>`;
  $('sheet').innerHTML = `<h2>${esc(s.label)}${l.n}</h2>${l.theme ? `<p class="theme">${esc(l.theme)}</p>` : ''}<div class="pills">${pills.join('')}</div>${notes}`;
}
function go(si, li, push){
  cur = {s: si, l: li ?? defaultLesson(si)};
  renderSubjects(); renderTabs(); renderSheet();
  const h = '#' + encodeURIComponent(DATA[cur.s].id) + '/' + DATA[cur.s].lessons[cur.l].n;
  if (push !== false && location.hash !== h) history.replaceState(null, '', h);
  try { localStorage.setItem('toc-last', h); } catch(e) {}
}
function fromHash(h){
  const m = decodeURIComponent(h || '').match(/^#([^/]+)\/(\d\d)$/); if (!m) return false;
  const si = DATA.findIndex(s => s.id === m[1]); if (si < 0) return false;
  const li = DATA[si].lessons.findIndex(l => l.n === m[2]);
  go(si, li < 0 ? null : li, false); return true;
}
$('subjects').addEventListener('click', e => { const b = e.target.closest('button'); if (b) go(+b.dataset.i, null); });
$('tabs').addEventListener('click', e => { const b = e.target.closest('button'); if (b) go(cur.s, +b.dataset.i); });
window.addEventListener('hashchange', () => fromHash(location.hash));
let last = null; try { last = localStorage.getItem('toc-last'); } catch(e) {}
if (!fromHash(location.hash) && !fromHash(last)) go(0, null);
</script>
</body></html>
""".replace('__DATA__', DATA)
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(page)
print('index.html', sum(len(s['lessons']) for s in data), 'lessons')
