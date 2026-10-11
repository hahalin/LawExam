"""重產 README.md 的「課程字幕與筆記」段（各科、各課分節）。用法：python scripts/build_readme.py"""
import os,re,urllib.parse as up
PAGES='https://hahalin.github.io/LawExam/'
def q(p): return up.quote(p)
def eli5_sub(path):
    t=open(path,encoding='utf-8').read()
    m=re.search(r'<span class="sub">(.*?)</span>',t,re.S)
    return re.sub('<[^>]+>','',m.group(1)).strip() if m else ''
def subject(d,label,prefix):
    base=f'課程字幕/{d}'
    fs=os.listdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),base))
    nums=sorted({m.group(1) for f in fs for m in [re.match(re.escape(prefix)+r'(\d\d)\.md$',f)] if m})
    out=[f'### {label}\n']
    for n in nums:
        sub_md=f'{prefix}{n}.md'
        notes=sorted(f for f in fs if f.startswith(f'{prefix}{n}-筆記-') and f.endswith('.md'))
        eli=f'{prefix}{n}-ELI5.html'
        out.append(f'#### {label}{n}\n')
        if eli in fs:
            s=eli5_sub(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),base,eli))
            if s: out.append(f'> {s}\n')
        out.append(f'- 課程字幕：[{sub_md}]({q(f"{base}/{sub_md}")})')
        if eli in fs:
            out.append(f'- ELI5 網頁：[{eli}]({PAGES}{q(f"{base}/{eli}")})')
        if notes:
            out.append(f'- 分主題筆記（{len(notes)} 份）：')
            for f in notes:
                m=re.match(re.escape(prefix)+n+r'-筆記-(\d\d)-(.*)\.md$',f)
                out.append(f'  - [{m.group(1)}　{m.group(2)}]({q(f"{base}/{f}")})')
        else:
            out.append('- 分主題筆記：尚未製作')
        out.append('')
    return '\n'.join(out)
sec=['## 課程字幕與筆記\n',
     f'ELI5 網頁目錄：<{PAGES}>（GitHub Pages；「懂了」勾選只存在各裝置的瀏覽器）\n',
     subject('民法','民法','民法'),subject('強制執行法','強制執行法','')]
new='\n'.join(sec)
s=open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'README.md'),encoding='utf-8').read()
a=s.index('## 課程字幕與筆記'); b=s.index('## 考古題')
s=s[:a]+new+'\n---\n\n'+s[b:]
open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'README.md'),'w',encoding='utf-8').write(s)
