# -*- coding: utf-8 -*-
r"""
考古題 PDF  Markdown 轉換腳本（自動分科版）

用法：
    python convert_exam.py <考卷PDF> <答案卷PDF>

自動偵測每題所屬科目，分別輸出至 考古題/{科目}/ 資料夾。
無法判斷的題目會以 JSON 輸出，交由 Agent 人工判斷。
"""
import sys, re, json
from pathlib import Path
import pdfplumber

#  科目關鍵字（支援正規表達式）
SUBJECT_KEYWORDS = {
    '憲法': [
        '憲法', '基本權', '違憲', '釋字', '大法官', '憲法法庭',
        '言論自由', '集會自由', '結社自由', '宗教自由', '人身自由',
        '財產權', '平等權', '比例原則', '法律保留', '憲法訴訟',
        '立法院', '行政院', '司法院', '考試院', '監察院', '總統',
        '五權', '增修條文', '人民之權利',
    ],
    '行政法': [
        '行政處分', '行政契約', '行政程序', '行政訴訟', '訴願', '行政罰',
        '行政執行', '行政機關', '國家賠償', '損失補償', '裁量',
        '判斷餘地', '不確定法律概念', '行政法院', '撤銷訴訟', '課予義務',
        '確認訴訟', '一般給付', '行政規則', '法規命令', '自治條例', '委辦規則',
    ],
    '刑法': [
        '故意', '過失', '未遂', '既遂', '共犯', '正犯', '教唆', '幫助犯',
        '阻卻違法', '正當防衛', '緊急避難', '罪刑法定', '累犯', '自首', '緩刑', '假釋',
        '竊盜', '搶奪', '強盜', '詐欺', '侵占', '背信', '殺人', '傷害',
        '毀損', '偽造文書', '妨害秩序', '遺棄', '賭博', '瀆職',
        '刑法第', '想像競合', '數罪併罰', '褫奪公權', '沒收', '構成要件',
        '錯誤論', '罪責', '責任能力', '刑法上', '義務衝突', '不能未遂',
        '吸收關係', '猥褻', '性交', '妨害秘密', '私行拘禁', '恐嚇',
        '刑法第\\d+條', '公務員.*賄',
    ],
    '刑事訴訟法': [
        '偵查', '公訴', '自訴', '告訴乃論', '羈押', '搜索票', '搜索', '扣押',
        '逮捕', '拘提', '傳喚', '通緝', '辯護人', '檢察官.*偵',
        '證據能力', '證明力', '自白', '傳聞', '交互詰問', '抗告',
        '再審', '非常上訴', '簡式審判', '協商程序',
        '國民法官', '國民參與審判', '刑事訴訟法第',
        '沒收程序', '證人.*具結', '詰問', '不起訴',
        '管轄.*追加起訴', '迴避.*審判', '被告.*在場權',
    ],
    '法律倫理': [
        '律師倫理', '法官倫理', '檢察官倫理', '倫理規範', '利益衝突', '保密義務',
        '忠誠義務', '懲戒', '律師法', '法官法',
        '律師.*委任', '律師.*代理', '事務所',
        '法官.*兼', '檢察一體',
        '道德.*法律.*倫理', '法律倫理', '律師.*報酬',
    ],
    '國際公法': [
        '國際法', '條約', '公約', '國家承認', '政府承認', '主權', '領土',
        '領海', '領空', '專屬經濟區', '大陸礁層', '外交', '領事',
        '引渡', '庇護', '國際組織', '聯合國', '安理會', '國際法院',
        '國際習慣法', '法之確信', '國家實踐', '條約法', '維也納公約',
    ],
    '國際私法': [
        '涉外', '準據法', '國際私法', '法律適用', '反致', '定性', '先決問題',
        '外國法', '屬人法', '屬地法', '本國法', '住所地法',
        '行為地法', '物之所在地', '當事人意思自主', '最密切關係', '國際管轄',
    ],
    '民法': [
        '契約', '債權', '債務', '物權', '所有權', '抵押權', '質權', '留置權',
        '占有', '繼承', '遺囑', '遺產', '婚姻', '離婚', '親權', '監護',
        '無權代理', '表見代理', '意思表示', '法律行為', '時效',
        '損害賠償', '不當得利', '無因管理', '侵權行為', '買賣', '租賃',
        '民法第',
    ],
    '民事訴訟法': [
        '民事訴訟', '訴之聲明', '訴訟標的', '當事人適格', '訴之利益',
        '言詞辯論', '舉證責任', '自認', '鑑定', '勘驗',
        '假扣押', '假處分', '強制執行', '第三人撤銷',
        '民事訴訟法第',
    ],
    '商事法': [
        '公司法', '股份', '董事', '監察人', '股東會', '票據', '支票', '本票',
        '匯票', '背書', '保險', '要保人', '被保險人', '保險金', '海商',
        '公司法第', '票據法第', '保險法第',
    ],
}

#  Unicode 私用區選項標記 
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


def normalize_block(block):
    for k, v in MARKER_MAP.items():
        block = block.replace(k, '\n' + v + ' ')
    return block


def clean_text(text):
    text = re.sub(r'\s+', ' ', ' '.join(text.splitlines())).strip()
    text = CH_SPACE.sub('', text)
    text = CH_PUNCT.sub(r'\1', text)
    return text


def classify_question(text):
    """回傳 (科目, 最高分, 次高分)"""
    scores = {}
    for subj, keywords in SUBJECT_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if re.search(kw, text):
                score += 1
        if score > 0:
            scores[subj] = score
    if not scores:
        return None, 0, 0
    ranked = sorted(scores.items(), key=lambda x: -x[1])
    best_subj, best_score = ranked[0]
    second_score = ranked[1][1] if len(ranked) > 1 else 0
    return best_subj, best_score, second_score


def parse_questions(paper_text):
    pattern = re.compile(r'(?m)^(\d{1,3})\s')
    matches = list(pattern.finditer(paper_text))
    questions = {}
    for i, m in enumerate(matches):
        qnum = int(m.group(1))
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(paper_text)
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
    for line in paper_text.splitlines():
        m = re.search(r'科\s*目\s*[：:]\s*(.+)', line)
        if m:
            exam_name = re.sub(r'\s+', '', m.group(1))
        m2 = re.search(r'(\d{3})年', line)
        if m2 and not year:
            year = m2.group(1)
    return year, exam_name


def question_to_md(seq, qnum, block, answer):
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

    lines = [f'## 第{seq}題（原第{qnum}題）', qtext, '']
    for k in 'ABCD':
        lines.append(f'({k}) {options.get(k, "")}  ')
    lines += ['', f'### 答案：({answer})', '', '---', '']
    return lines


def main():
    if len(sys.argv) < 3:
        print('用法: python convert_exam.py <考卷PDF> <答案卷PDF>')
        sys.exit(1)

    paper_path = Path(sys.argv[1]).resolve()
    ans_path = Path(sys.argv[2]).resolve()
    workspace = Path(sys.argv[3]).resolve() if len(sys.argv) > 3 else paper_path.parent
    if workspace.name != '考古題':
        workspace = workspace / '考古題' if (workspace / '考古題').exists() else workspace

    print(f'[讀取] 考卷: {paper_path}')
    print(f'[讀取] 答案: {ans_path}')

    paper_text = extract_pdf(paper_path)
    ans_text = extract_pdf(ans_path)
    questions = parse_questions(paper_text)
    answers = parse_answers(ans_text)
    year, exam_name = extract_exam_info(paper_text)

    m = re.search(r'代號[：:]\s*(\d+)', paper_text)
    exam_code = m.group(1) if m else paper_path.stem.split('_')[1][:4]

    print(f'[資訊] 年度={year}, 代號={exam_code}, 科目={exam_name}')
    print(f'[資訊] 共 {len(questions)} 題, 答案 {len(answers)} 題')
    print()

    #  第一層：Python 關鍵字逐題分科 
    classified = {}   # qnum -> subject
    unclassified = [] # qnum list

    for qnum in sorted(questions.keys()):
        text = questions[qnum]
        subj, best, second = classify_question(text)
        if subj is None or best <= 1 or (second > 0 and best - second <= 0):
            unclassified.append(qnum)
        else:
            classified[qnum] = subj

    #  連續性修正：未分類題目若前後同科則歸入 
    all_qnums = sorted(questions.keys())
    still_unclassified = []
    for qnum in unclassified:
        idx = all_qnums.index(qnum)
        prev_subj = classified.get(all_qnums[idx - 1]) if idx > 0 else None
        next_subj = classified.get(all_qnums[idx + 1]) if idx < len(all_qnums) - 1 else None
        if prev_subj and prev_subj == next_subj:
            classified[qnum] = prev_subj
        else:
            still_unclassified.append(qnum)

    # 再跑一次連續性修正
    round2_unclassified = []
    for qnum in still_unclassified:
        idx = all_qnums.index(qnum)
        prev_subj = classified.get(all_qnums[idx - 1]) if idx > 0 else None
        next_subj = classified.get(all_qnums[idx + 1]) if idx < len(all_qnums) - 1 else None
        if prev_subj and prev_subj == next_subj:
            classified[qnum] = prev_subj
        elif prev_subj:
            classified[qnum] = prev_subj
        elif next_subj:
            classified[qnum] = next_subj
        else:
            round2_unclassified.append(qnum)
    still_unclassified = round2_unclassified

    #  彙整各科目題號 
    subject_questions = {}
    for qnum, subj in classified.items():
        subject_questions.setdefault(subj, []).append(qnum)

    print('=== 科目分類結果 ===')
    for subj in sorted(subject_questions.keys(), key=lambda s: min(subject_questions[s])):
        nums = sorted(subject_questions[subj])
        print(f'  {subj}: 第{nums[0]}-{nums[-1]}題 (共{len(nums)}題)')
    if still_unclassified:
        print(f'\n   無法分類: {still_unclassified}')
    print()

    #  產生 Markdown 檔案 
    output_stem = paper_path.stem.split('_')[0] + '_' + exam_code
    created_files = []

    for subj, nums in subject_questions.items():
        nums = sorted(nums)
        out_dir = workspace / subj
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f'{output_stem}.md'

        md = []
        md.append(f'# {year}年司法官律師考試 - {subj}（{exam_code}）')
        md.append('')
        md.append(f'> {year}年公務人員特種考試司法官考試（第一試）  ')
        md.append(f'> {year}年專門職業及技術人員高等考試律師考試（第一試）  ')
        md.append(f'> 科目：{exam_name}  ')
        md.append(f'> 本文件僅整理{subj}部分（第{nums[0]}-{nums[-1]}題）')
        md.append('')
        md.append('---')
        md.append('')

        for seq, qnum in enumerate(nums, start=1):
            ans = answers.get(qnum, '?')
            md.extend(question_to_md(seq, qnum, questions[qnum], ans))

        out_path.write_text('\n'.join(md).rstrip() + '\n', encoding='utf-8')
        created_files.append(str(out_path))
        print(f'[寫入] {out_path}')

    #  JSON 摘要 
    summary = {
        'year': year,
        'exam_code': exam_code,
        'exam_name': exam_name,
        'created_files': created_files,
        'subjects': {s: sorted(n) for s, n in subject_questions.items()},
        'unclassified': still_unclassified,
        'unclassified_texts': {str(q): questions[q][:300] for q in still_unclassified},
    }
    print('\n=== JSON ===')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
