# -*- coding: utf-8 -*-
"""Convert 108 and 109 year 0101 PDFs (憲法/行政法/國公/國私) to Markdown."""
import sys, os
from pathlib import Path

os.chdir(r"D:\repo\LawExam")

import importlib.util
script = r".github\skills\exam-pdf-to-markdown\convert_exam.py"
spec = importlib.util.spec_from_file_location("convert_exam", script)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Subject mapping for 0101 papers (same as 2301)
# 憲法: Q1-20, 行政法: Q21-55, 國際公法: Q56-65, 國際私法: Q66-75
SUBJECT_RANGES = {
    '憲法': range(1, 21),
    '行政法': range(21, 56),
    '國際公法': range(56, 66),
    '國際私法': range(66, 76),
}

def convert_one(paper_pdf, ans_pdf, year_str, file_prefix):
    paper_path = os.path.abspath(paper_pdf)
    ans_path = os.path.abspath(ans_pdf)
    
    print(f"\n{'='*60}")
    print(f"Processing: {paper_pdf}")
    
    paper_text = mod.extract_pdf(paper_path)
    ans_text = mod.extract_pdf(ans_path)
    
    questions = mod.parse_questions(paper_text)
    answers = mod.parse_answers(ans_text)
    
    print(f"  Questions: {len(questions)}, Answers: {len(answers)}")
    
    # Classify by question number
    subject_map = {}
    for qnum in sorted(questions.keys()):
        for subj, rng in SUBJECT_RANGES.items():
            if qnum in rng:
                subject_map.setdefault(subj, []).append(qnum)
                break
    
    exam_code = "2301"  # Use standardized code for output
    exam_name = "綜合法學（憲法、行政法、國際公法、國際私法）"
    workspace = Path("考古題")
    
    for subject, q_nums in subject_map.items():
        q_nums_sorted = sorted(q_nums)
        out_dir = workspace / subject
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{file_prefix}_{exam_code}.md"
        
        md = []
        md.append(f'# {year_str}年司法官律師考試 - {subject}（{exam_code}）')
        md.append('')
        md.append(f'> {year_str}年公務人員特種考試司法官考試（第一試）  ')
        md.append(f'> {year_str}年專門職業及技術人員高等考試律師考試（第一試）  ')
        md.append(f'> 科目：{exam_name}  ')
        md.append(f'> 本文件僅整理{subject}部分（第{q_nums_sorted[0]}-{q_nums_sorted[-1]}題）')
        md.append('')
        md.append('---')
        md.append('')
        
        for seq, qnum in enumerate(q_nums_sorted, start=1):
            ans_letter = answers.get(qnum, '?')
            md.extend(mod.question_to_md(seq, qnum, questions[qnum], ans_letter))
        
        out_path.write_text('\n'.join(md).rstrip() + '\n', encoding='utf-8')
        print(f"  [寫入] {out_path} ({len(q_nums_sorted)} 題)")

# Convert 108年
convert_one(
    r"考古題\108120_0101_綜合法學(一)(憲法.pdf",
    r"考古題\108120_ANS0101_綜合法學(一)(憲法.pdf",
    "108", "108120"
)

# Convert 109年
convert_one(
    r"考古題\109120_0101_綜合法學(一)(憲法.pdf",
    r"考古題\109120_ANS0101_綜合法學(一)(憲法.pdf",
    "109", "109120"
)

print("\n\nDone!")
