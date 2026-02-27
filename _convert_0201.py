# -*- coding: utf-8 -*-
"""
綜合法學(二)(民法、民事訴訟法) 考古題轉換腳本
強制分科：1-50 → 民法, 51-80 → 民事訴訟法
"""
import sys, re, json
from pathlib import Path

# 重用 convert_exam.py 的函式
sys.path.insert(0, str(Path(__file__).parent / '.github' / 'skills' / 'exam-pdf-to-markdown'))
from convert_exam import extract_pdf, parse_questions, parse_answers, extract_exam_info, question_to_md

# 定義所有年度的 PDF 對
EXAM_PAIRS = [
    ('考古題/108120_0201_綜合法學(二)(民法.pdf', '考古題/108120_ANS0201_綜合法學(二)(民法.pdf', '108'),
    ('考古題/109120_0201_綜合法學(二)(民法.pdf', '考古題/109120_ANS0201_綜合法學(二)(民法.pdf', '109'),
    ('考古題/110120_0201_綜合法學(二)(民法.pdf', '考古題/110120_ANS0201_綜合法學(二)(民法.pdf', '110'),
    ('考古題/111120_0201_綜合法學(二)(民法.pdf', '考古題/111120_ANS0201_綜合法學(二)(民法.pdf', '111'),
    ('考古題/112120_0201_綜合法學(二)(民法.pdf', '考古題/112120_ANS0201_綜合法學(二)(民法.pdf', '112'),
    ('考古題/113110_0201_綜合法學(二)(民法.pdf', '考古題/113110_ANS0201_綜合法學(二)(民法.pdf', '113'),
    ('考古題/114110_0201_綜合法學(二)(民法.pdf', '考古題/114110_ANS0201_綜合法學(二)(民法.pdf', '114'),
]

# 強制分科規則
SPLIT_RULES = {
    '民法': range(1, 51),        # 第 1-50 題
    '民事訴訟法': range(51, 81),  # 第 51-80 題
}

EXAM_NAME = '綜合法學（民法、民事訴訟法）'
WORKSPACE = Path(__file__).parent / '考古題'


def generate_md(year, exam_code, subject, nums, questions, answers):
    """產生單一科目的 Markdown 檔案"""
    out_dir = WORKSPACE / subject
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f'{exam_code}.md'

    md = []
    md.append(f'# {year}年司法官律師考試 - {subject}（3301）')
    md.append('')
    md.append(f'> {year}年公務人員特種考試司法官考試（第一試）  ')
    md.append(f'> {year}年專門職業及技術人員高等考試律師考試（第一試）  ')
    md.append(f'> 科目：{EXAM_NAME}  ')
    md.append(f'> 本文件僅整理{subject}部分（第{nums[0]}-{nums[-1]}題）')
    md.append('')
    md.append('---')
    md.append('')

    for seq, qnum in enumerate(nums, start=1):
        if qnum not in questions:
            continue
        ans = answers.get(qnum, '?')
        md.extend(question_to_md(seq, qnum, questions[qnum], ans))

    out_path.write_text('\n'.join(md).rstrip() + '\n', encoding='utf-8')
    print(f'  [寫入] {out_path}')
    return str(out_path)


def process_exam(paper_path_str, ans_path_str, fallback_year):
    """處理一組考卷"""
    paper_path = Path(paper_path_str).resolve()
    ans_path = Path(ans_path_str).resolve()

    print(f'\n=== 處理 {paper_path.name} ===')

    paper_text = extract_pdf(paper_path)
    ans_text = extract_pdf(ans_path)
    questions = parse_questions(paper_text)
    answers = parse_answers(ans_text)
    year, exam_name = extract_exam_info(paper_text)

    if not year:
        year = fallback_year

    # 取得考卷代號（從檔名）
    stem = paper_path.stem.split('_')[0]
    exam_code = f'{stem}_3301'

    print(f'  年度={year}, 共 {len(questions)} 題, 答案 {len(answers)} 題')

    created = []
    for subject, qrange in SPLIT_RULES.items():
        nums = sorted([q for q in questions.keys() if q in qrange])
        if nums:
            f = generate_md(year, exam_code, subject, nums, questions, answers)
            created.append(f)

    return created


def main():
    all_created = []
    for paper, ans, year in EXAM_PAIRS:
        files = process_exam(paper, ans, year)
        all_created.extend(files)

    print(f'\n=== 完成！共產生 {len(all_created)} 個檔案 ===')
    for f in all_created:
        print(f'  {f}')


if __name__ == '__main__':
    main()
