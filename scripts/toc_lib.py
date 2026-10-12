"""掃描 課程字幕/ 各科資料夾，整理成「科目 → 課堂 → 字幕／ELI5／筆記」結構，給 build_index.py、build_readme.py 共用。
各科檔名不一致，規則：
  {前綴}{課}.md                      → 課程字幕（前綴＝資料夾名，可省略，如強制執行法 04.md、刑訴 伊谷01.md）
  {前綴}{課}-筆記-NN-主題.md         → 分主題筆記（有序號）
  {前綴}{課}-筆記-主題.md            → 分主題筆記（無序號，舊格式）
  {課}筆記.md、{課}筆記2.md           → 整堂筆記（舊格式，如刑法、行政法）
  {前綴}{課}-ELI5.html               → ELI5 網頁
其餘 html（字幕原始檔）、pdf、epub、readme.md 不列。"""
import os, re, urllib.parse as up
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = '課程字幕'
ORDER = ['民法', '強制執行法', '民事訴訟法', '刑法', '刑訴', '行政法', '保險法', '票據法', '民法-陳聰富']

def q(p): return up.quote(p)
def natkey(s): return [int(t) if t.isdigit() else t for t in re.split(r'(\d+)', s)]
def md_title(path, fallback):
    """取筆記第一個 # 大標題：去掉「民法14 筆記：」前綴、「——」後的摘要、粗體記號；沒有大標題就用 fallback。"""
    try:
        with open(path, encoding='utf-8') as fh:
            for line in fh:
                if line.startswith('# '):
                    t = line[2:].strip()
                    t = re.sub(r'^[^：:]{0,30}?筆記[：:]\s*', '', t)
                    t = t.split('——')[0].replace('**', '').strip()
                    t = re.sub(r'（[^（）]*講義[^（）]*）$', '', t).strip()
                    return t or fallback
                if line.strip() and not line.startswith('#'):
                    break
    except OSError:
        pass
    return fallback

def eli5_sub(path):
    t = open(path, encoding='utf-8').read()
    m = re.search(r'<span class="sub">(.*?)</span>', t, re.S)
    return re.sub('<[^>]+>', '', m.group(1)).strip() if m else ''

def scan_subject(d):
    base = f'{BASE}/{d}'
    fs = os.listdir(os.path.join(ROOT, base))
    strip = lambda f: f[len(d):] if f.startswith(d) else f
    L = {}
    def get(i): return L.setdefault(i, dict(n=i, sub=None, eli=None, notes=[]))
    for f in fs:
        g = strip(f)
        if f.endswith('-ELI5.html'):
            get(g[:-len('-ELI5.html')])['eli'] = f
            continue
        if not f.endswith('.md') or f.lower() == 'readme.md':
            continue
        m = re.match(r'^(.+?)-筆記-(?:(\d\d)-)?(.+)\.md$', g)
        if m:
            get(m.group(1))['notes'].append([m.group(2) or '', m.group(3), f]); continue
        m = re.match(r'^(.+?)筆記(\d*)\.md$', g)
        if m:
            get(m.group(1))['notes'].append(['', '整堂筆記' + (f'（{m.group(2)}）' if m.group(2) else ''), f]); continue
        get(g[:-3])['sub'] = f
    out = []
    for i in sorted(L, key=natkey):
        l = L[i]
        tab, _, rest = i.partition(' ')
        theme = eli5_sub(os.path.join(ROOT, base, l['eli'])) if l['eli'] else rest
        notes = sorted(l['notes'], key=lambda x: (0 if x[1].startswith('整堂筆記') else 1, x[0] == '', x[0], natkey(x[1])))
        out.append(dict(
            n=i, tab=tab, title=(d + tab) if not rest and not d.startswith(tab) else tab, theme=theme,
            sub=dict(name=l['sub'], path=f"{base}/{l['sub']}", url='note.html?f=' + q(f"{base}/{l['sub']}")) if l['sub'] else None,
            eli=q(f"{base}/{l['eli']}") if l['eli'] else None,
            notes=[dict(no=no, t=t if t.startswith('整堂筆記') else md_title(os.path.join(ROOT, base, f), t), fn=t,
                        path=f'{base}/{f}', url='note.html?f=' + q(f'{base}/{f}')) for no, t, f in notes]))
    return out

def scan():
    ds = [d for d in os.listdir(os.path.join(ROOT, BASE)) if os.path.isdir(os.path.join(ROOT, BASE, d)) and not d.startswith('_')]
    ds.sort(key=lambda d: (ORDER.index(d) if d in ORDER else 99, d))
    data = []
    for d in ds:
        ls = scan_subject(d)
        if ls: data.append(dict(id=d, label=d, lessons=ls))
    return data

if __name__ == '__main__':
    for s in scan():
        print(s['label'], len(s['lessons']), 'lessons', sum(len(l['notes']) for l in s['lessons']), 'notes',
              sum(1 for l in s['lessons'] if l['eli']), 'eli5', '| tabs:', ' '.join(l['tab'] for l in s['lessons'])[:90])
