# -*- coding: utf-8 -*-
"""
綜合法學(二)公司 PDF → Markdown 批次轉換腳本
將考卷與答案卷合併為單一 Markdown 檔案，不做科目分類。
"""
import sys, re, json
from pathlib import Path
import pdfplumber

MARKER_MAP = {'\ue18c': '(A)', '\ue18d': '(B)', '\ue18e': '(C)', '\ue18f': '(D)'}
OPT_PAT = re.compile(r'\(A\)|\(B\)|\(C\)|\(D\)')
CH_SPACE = re.compile(r'(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])')
CH_PUNCT = re.compile(r'([，。、；：！？）」])\s+')


def extract_pdf(path):
    pages = []
    with pdfplumber.open(path) as pdf:
        for p in pdf.pages:
            pages.append(p.extract_text() or '')
    return '\n\n'.join(pages).replace('\r\n', '\n')


def clean_text(text):
    text = re.sub(r'\s+', ' ', ' '.join(text.splitlines())).strip()
    text = CH_SPACE.sub('', text)
    text = CH_PUNCT.sub(r'\1', text)
    return text


def fix_circled_numbers(text):
    """Fix broken font mapping: consecutive ①① → ①②, ①①① → ①②③, etc."""
    CIRCLED = '①②③④⑤⑥⑦⑧⑨⑩'
    def _replace(m):
        n = len(m.group(0))
        return CIRCLED[:n]
    return re.sub(r'①{2,}', _replace, text)


def normalize_block(block):
    for k, v in MARKER_MAP.items():
        block = block.replace(k, '\n' + v + ' ')
    block = fix_circled_numbers(block)
    return block


def parse_questions(paper_text):
    # Match question numbers at start of line, excluding false positives like "10 萬元", "107 年"
    pattern = re.compile(r'(?m)^(\d{1,3})\s')
    false_positive = re.compile(r'^(\d{1,3})\s*[萬億元年月日條項款%％]')
    matches = list(pattern.finditer(paper_text))
    # Filter: only keep valid question numbers (1-80, not followed by units/dates)
    filtered = []
    for m in matches:
        qnum = int(m.group(1))
        if qnum < 1 or qnum > 80:
            continue
        line = paper_text[m.start():m.start()+20]
        if false_positive.match(line):
            continue
        filtered.append(m)
    # Ensure sequential: remove duplicates keeping the first occurrence
    seen = set()
    unique = []
    for m in filtered:
        qnum = int(m.group(1))
        if qnum not in seen:
            seen.add(qnum)
            unique.append(m)
    questions = {}
    for i, m in enumerate(unique):
        qnum = int(m.group(1))
        start = m.start()
        end = unique[i + 1].start() if i + 1 < len(unique) else len(paper_text)
        questions[qnum] = paper_text[start:end].strip()
    return questions


def parse_answers(ans_text):
    answers = {}
    letters = []
    for line in ans_text.splitlines():
        line = line.strip()
        if line.startswith('答案'):
            letters.extend(re.findall(r'[A-D]', line))
    for idx, letter in enumerate(letters, start=1):
        answers[idx] = letter
    return answers


def extract_exam_info(paper_text):
    exam_name = ''
    year = ''
    exam_lines = []
    for line in paper_text.splitlines():
        m = re.search(r'科\s*目\s*[：:]\s*(.+)', line)
        if m:
            exam_name = re.sub(r'\s+', '', m.group(1))
        m2 = re.search(r'(\d{3})年', line)
        if m2 and not year:
            year = m2.group(1)
        # Capture exam description lines
        if re.search(r'(考試|第一試|律師考試)', line):
            exam_lines.append(line.strip())
    return year, exam_name, exam_lines


def question_to_md(qnum, block, answer):
    block = normalize_block(block)
    block = re.sub(r'代號：\d+\s*\n?頁次：.*?(\n|$)', '\n', block)

    first_opt = OPT_PAT.search(block)
    if first_opt:
        qtext = block[:first_opt.start()].strip()
        rest = block[first_opt.start():].strip()
    else:
        qtext = block.strip()
        rest = ''

    qtext = re.sub(r'^\d{1,3}\s+', '', qtext).strip()
    qtext = clean_text(qtext)

    options = {}
    if rest:
        opt_matches = list(OPT_PAT.finditer(rest))
        for i, m in enumerate(opt_matches):
            key = m.group(0).strip('()')
            s = m.end()
            e = opt_matches[i + 1].start() if i + 1 < len(opt_matches) else len(rest)
            options[key] = clean_text(rest[s:e])

    lines = [f'## 第{qnum}題', qtext, '']
    for k in 'ABCD':
        lines.append(f'({k}) {options.get(k, "")}  ')
    lines += ['', f'### 答案：({answer})', '', '---', '']
    return lines


def convert_one(paper_path, ans_path, out_dir):
    paper_text = extract_pdf(paper_path)
    ans_text = extract_pdf(ans_path)
    questions = parse_questions(paper_text)
    answers = parse_answers(ans_text)
    _, exam_name, exam_lines = extract_exam_info(paper_text)

    # Extract year from filename (first 3 digits, e.g. 107120 -> 107)
    year = paper_path.stem[:3]

    m = re.search(r'代號[：:]\s*(\d+)', paper_text)
    exam_code = m.group(1) if m else paper_path.stem.split('_')[1][:4]

    # Fix truncated exam name
    if exam_name and not exam_name.endswith('）'):
        exam_name = exam_name.rstrip('、') + '、法學英文）'

    m = re.search(r'代號[：:]\s*(\d+)', paper_text)
    exam_code = m.group(1) if m else paper_path.stem.split('_')[1][:4]

    print(f'  年度={year}, 代號={exam_code}, 科目={exam_name}')
    print(f'  共 {len(questions)} 題, 答案 {len(answers)} 題')

    # Build markdown
    md = []
    md.append(f'# {year}年司法官律師考試 - 綜合法學（{exam_code}）')
    md.append('')
    md.append(f'> 科目：{exam_name}  ')
    md.append('')
    md.append('---')
    md.append('')

    for qnum in sorted(questions.keys()):
        ans = answers.get(qnum, '?')
        md.extend(question_to_md(qnum, questions[qnum], ans))

    out_stem = paper_path.stem.split('_')[0] + '_' + exam_code
    out_path = out_dir / f'{out_stem}.md'
    out_path.write_text('\n'.join(md).rstrip() + '\n', encoding='utf-8')
    print(f'  => {out_path.name}')
    return out_path


def main():
    folder = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('考古題/綜合法學(2)公司').resolve()

    # Find all exam/answer pairs
    papers = sorted(folder.glob('*_0202_*.pdf'))
    pairs = []
    for p in papers:
        if '_ANS' in p.name or '_MOD' in p.name:
            continue
        ans_name = p.name.replace('_0202_', '_ANS0202_')
        ans_path = folder / ans_name
        if ans_path.exists():
            pairs.append((p, ans_path))
        else:
            print(f'[警告] 找不到答案卷: {ans_name}')

    print(f'找到 {len(pairs)} 組考卷/答案卷\n')

    for paper, ans in pairs:
        print(f'[處理] {paper.name}')
        try:
            convert_one(paper, ans, folder)
        except Exception as e:
            print(f'  [錯誤] {e}')
        print()


if __name__ == '__main__':
    main()
