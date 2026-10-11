"""重產 README.md 的「課程字幕與筆記」段（各科、各課分節）。用法：python scripts/build_readme.py；掃描規則見 scripts/toc_lib.py。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from toc_lib import ROOT, scan, q
from urllib.parse import unquote
PAGES = 'https://hahalin.github.io/LawExam/'
out = ['## 課程字幕與筆記\n', f'網站（左科目、上課堂活頁，筆記與 ELI5 都在站內開）：<{PAGES}>\n']
for s in scan():
    out.append(f"### {s['label']}\n")
    for l in s['lessons']:
        out.append(f"#### {l['title']}\n")
        if l['theme']: out.append(f"> {l['theme']}\n")
        if l['sub']: out.append(f"- 課程字幕：[{l['sub']['name']}]({q(l['sub']['path'])})")
        if l['eli']: out.append(f"- ELI5 網頁：[{os.path.basename(unquote(l['eli']))}]({PAGES}{l['eli']})")
        if l['notes']:
            out.append(f"- 筆記（{len(l['notes'])} 份）：")
            for n in l['notes']:
                out.append(f"  - [{(n['no'] + '　') if n['no'] else ''}{n['t']}]({q(n['path'])})")
        else:
            out.append('- 筆記：尚未製作')
        out.append('')
new = '\n'.join(out)
p = os.path.join(ROOT, 'README.md')
s = open(p, encoding='utf-8').read()
a = s.index('## 課程字幕與筆記'); b = s.index('## 考古題')
open(p, 'w', encoding='utf-8').write(s[:a] + new + '\n---\n\n' + s[b:])
print('README sections:', new.count('\n#### '))
