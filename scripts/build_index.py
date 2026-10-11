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

nav, body = [], []
for d, label, prefix in SUBJECTS:
    sid = f's-{q(d)}'
    ls = list(lessons(d, prefix))
    nav.append(f'<a href="#{sid}">{esc(label)}</a>')
    chips = ''.join(f'<a href="#{sid}-{l["n"]}">{l["n"]}</a>' for l in ls)
    cards = []
    for l in ls:
        rows = [f'<a class="pill" href="{BLOB}{q(l["sub_md"])}">📄 課程字幕 {esc(l["sub_name"])}</a>']
        rows.append(f'<a class="pill eli" href="{q(l["eli"])}">🌐 ELI5 網頁</a>' if l['eli'] else '<span class="pill off">ELI5 尚未製作</span>')
        theme = f'<p class="theme">{esc(l["theme"])}</p>' if l['theme'] else ''
        if l['notes']:
            items = ''.join(f'<li><a href="{BLOB}{q(p)}"><b>{no}</b>{esc(t)}</a></li>' for no, t, p in l['notes'])
            notes = f'<h4>分主題筆記 {len(l["notes"])} 份</h4><ol>{items}</ol>'
        else:
            notes = '<p class="none">分主題筆記尚未製作</p>'
        cards.append(f'<section class="lesson" id="{sid}-{l["n"]}"><h3>{esc(label)}{l["n"]}</h3>{theme}'
                     f'<div class="pills">{"".join(rows)}</div>{notes}</section>')
    body.append(f'<section class="subject" id="{sid}"><h2>{esc(label)}</h2><nav class="chips">{chips}</nav>{"".join(cards)}</section>')

page = f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>司律課程筆記</title>
<style>
:root{{--bg:#f7f7f4;--fg:#1f2328;--mu:#646a71;--card:#fff;--line:#e2e2dc;--acc:#2f6f8f;--acc-bg:#e8f1f5;--chip:#efefea}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#15171a;--fg:#e6e6e3;--mu:#9a9fa5;--card:#1d2023;--line:#32363a;--acc:#7fb6d1;--acc-bg:#1d3440;--chip:#262a2e}}}}
:root[data-theme="dark"]{{--bg:#15171a;--fg:#e6e6e3;--mu:#9a9fa5;--card:#1d2023;--line:#32363a;--acc:#7fb6d1;--acc-bg:#1d3440;--chip:#262a2e}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.65 system-ui,"Noto Sans TC","PingFang TC",sans-serif}}
header{{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line)}}
header .in{{max-width:820px;margin:0 auto;padding:12px 16px;display:flex;gap:16px;align-items:baseline;flex-wrap:wrap}}
header h1{{font-size:1.15rem;margin:0}} header nav a{{color:var(--acc);text-decoration:none;margin-right:14px;font-weight:600}}
main{{max-width:820px;margin:0 auto;padding:8px 16px 64px}}
.note{{color:var(--mu);font-size:.88rem;margin:14px 0 0}}
h2{{font-size:1.35rem;margin:36px 0 10px;scroll-margin-top:64px}}
.chips{{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:14px}}
.chips a{{background:var(--chip);color:var(--fg);text-decoration:none;border-radius:6px;padding:2px 10px;font-size:.9rem;font-variant-numeric:tabular-nums}}
.chips a:hover{{background:var(--acc-bg);color:var(--acc)}}
.lesson{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:12px 0;scroll-margin-top:64px}}
.lesson h3{{margin:0;font-size:1.1rem}}
.theme{{margin:2px 0 10px;color:var(--mu);font-size:.92rem}}
.pills{{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0 4px}}
.pill{{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:3px 12px;font-size:.9rem;text-decoration:none;color:var(--fg)}}
.pill:hover{{border-color:var(--acc);color:var(--acc)}} .pill.eli{{background:var(--acc-bg);border-color:transparent;color:var(--acc);font-weight:600}}
.pill.off{{color:var(--mu);border-style:dashed}}
h4{{font-size:.9rem;color:var(--mu);font-weight:600;margin:12px 0 4px}}
ol{{list-style:none;margin:0;padding:0}} ol li{{border-top:1px solid var(--line)}} ol li:first-child{{border-top:0}}
ol a{{display:flex;gap:10px;padding:6px 2px;color:var(--fg);text-decoration:none;font-size:.92rem;line-height:1.5;overflow-wrap:anywhere}}
ol a b{{color:var(--acc);font-variant-numeric:tabular-nums;flex:none}} ol a:hover{{color:var(--acc)}}
.none{{color:var(--mu);font-size:.9rem;margin:10px 0 0}}
</style></head><body>
<header><div class="in"><h1>司律課程筆記</h1><nav>{"".join(nav)}</nav></div></header>
<main>
<p class="note">課程字幕、分主題筆記連到 GitHub 檢視；ELI5 在本站開。「懂了」勾選只存在各裝置的瀏覽器。</p>
{"".join(body)}
</main></body></html>
'''
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(page)
print('index.html', sum(1 for _ in re.finditer('class="lesson"', page)), 'lessons')
