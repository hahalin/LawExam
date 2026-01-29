# -*- coding: utf-8 -*-
r"""
考古題 PDF 轉 Markdown 腳本

用法：
    python convert_exam.py <paper_path> <ans_path> <subject>
    
範例：
    python convert_exam.py 考古題/113110_2301.pdf 考古題/113110_ANS2301.pdf 憲法
"""
import sys
from pathlib import Path
import re
import pdfplumber


# === 科目特徵關鍵字（用於自動判斷題目所屬科目）===
SUBJECT_FEATURES = {
    '憲法': [
        '憲法', '基本權', '違憲', '釋字', '大法官', '憲法法庭', '人民之權利',
        '言論自由', '集會自由', '結社自由', '宗教自由', '人身自由', '遷徙自由',
        '財產權', '平等權', '比例原則', '法律保留', '憲法訴訟', '立法院',
        '行政院', '司法院', '考試院', '監察院', '總統', '五權', '增修條文'
    ],
    '行政法': [
        '行政處分', '行政契約', '行政程序', '行政訴訟', '訴願', '行政罰',
        '行政執行', '行政機關', '公務員', '國家賠償', '損失補償', '裁量',
        '判斷餘地', '不確定法律概念', '行政法院', '撤銷訴訟', '課予義務',
        '確認訴訟', '一般給付', '行政規則', '法規命令', '自治條例', '委辦規則'
    ],
    '刑法': [
        '犯罪', '刑責', '構成要件', '故意', '過失', '未遂', '既遂', '共犯',
        '正犯', '教唆', '幫助', '阻卻違法', '正當防衛', '緊急避難', '罪刑',
        '法定刑', '處斷刑', '宣告刑', '累犯', '自首', '緩刑', '假釋',
        '竊盜', '搶奪', '強盜', '詐欺', '侵占', '背信', '殺人', '傷害'
    ],
    '刑事訴訟法': [
        '偵查', '起訴', '公訴', '自訴', '告訴', '羈押', '搜索', '扣押',
        '逮捕', '拘提', '傳喚', '通緝', '被告', '辯護人', '檢察官', '法官',
        '證據能力', '證明力', '自白', '傳聞', '交互詰問', '上訴', '抗告',
        '再審', '非常上訴', '準備程序', '審判程序', '簡易程序', '協商程序'
    ],
    '國際公法': [
        '國際法', '條約', '公約', '國家承認', '政府承認', '主權', '領土',
        '領海', '領空', '專屬經濟區', '大陸礁層', '外交', '領事', '國籍',
        '引渡', '庇護', '國際組織', '聯合國', '安理會', '國際法院',
        '國際習慣法', '法之確信', '國家實踐', '條約法', '維也納公約'
    ],
    '國際私法': [
        '涉外', '準據法', '國際私法', '法律適用', '反致', '定性', '先決問題',
        '公序良俗', '外國法', '屬人法', '屬地法', '本國法', '住所地法',
        '行為地法', '物之所在地', '當事人意思自主', '最密切關係', '國際管轄'
    ],
    '民法': [
        '契約', '債權', '債務', '物權', '所有權', '抵押權', '質權', '留置權',
        '占有', '繼承', '遺囑', '遺產', '婚姻', '離婚', '親權', '監護',
        '代理', '無權代理', '表見代理', '意思表示', '法律行為', '時效',
        '損害賠償', '不當得利', '無因管理', '侵權行為', '買賣', '租賃'
    ],
    '民事訴訟法': [
        '民事訴訟', '起訴', '訴之聲明', '訴訟標的', '當事人適格', '訴之利益',
        '管轄', '移送', '迴避', '訴訟代理', '言詞辯論', '準備程序', '證據',
        '舉證責任', '自認', '文書', '鑑定', '勘驗', '判決', '裁定', '上訴',
        '抗告', '再審', '第三人撤銷', '強制執行', '假扣押', '假處分'
    ],
    '法律倫理': [
        '律師', '法官倫理', '檢察官倫理', '律師倫理', '利益衝突', '保密義務',
        '忠誠義務', '迴避', '懲戒', '律師法', '法官法', '廉潔', '品位'
    ],
    '商事法': [
        '公司', '股份', '董事', '監察人', '股東會', '票據', '支票', '本票',
        '匯票', '背書', '保險', '要保人', '被保險人', '保險金', '海商'
    ],
}

# === 預設的科目配置（作為備用）===
DEFAULT_SUBJECT_CONFIG = {
    '1301': {
        '刑法': (range(1, 36), '綜合法學（二）（刑法、刑事訴訟法、法律倫理）'),
        '刑事訴訟法': (range(36, 61), '綜合法學（二）（刑法、刑事訴訟法、法律倫理）'),
        '法律倫理': (range(61, 76), '綜合法學（二）（刑法、刑事訴訟法、法律倫理）'),
    },
    '2301': {
        '憲法': (range(1, 21), '綜合法學（一）（憲法、行政法、國際公法、國際私法）'),
        '行政法': (range(21, 56), '綜合法學（一）（憲法、行政法、國際公法、國際私法）'),
        '國際公法': (range(56, 66), '綜合法學（一）（憲法、行政法、國際公法、國際私法）'),
        '國際私法': (range(66, 76), '綜合法學（一）（憲法、行政法、國際公法、國際私法）'),
    },
}

# === exam_name 對照表 ===
EXAM_NAMES = {
    '1301': '綜合法學（二）（刑法、刑事訴訟法、法律倫理）',
    '2301': '綜合法學（一）（憲法、行政法、國際公法、國際私法）',
}

# === PDF 中使用 Unicode 私用區字元表示選項標記 ===
MARKER_MAP = {'\ue18c': '(A)', '\ue18d': '(B)', '\ue18e': '(C)', '\ue18f': '(D)'}


def extract_pages(path: Path) -> list[str]:
    """提取 PDF 所有頁面的文字"""
    texts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ''
            texts.append(text)
    return texts


def detect_question_subject(text: str) -> str | None:
    """根據題目內容判斷所屬科目"""
    scores = {}
    for subj, keywords in SUBJECT_FEATURES.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[subj] = score
    
    if scores:
        return max(scores, key=scores.get)
    return None


def detect_subject_ranges(text: str) -> dict[str, tuple[int, int]]:
    """從 PDF 內容自動偵測各科目的題號範圍"""
    pattern = re.compile(r'(?m)^(\d{1,2})\s')
    matches = list(pattern.finditer(text))
    
    question_subjects = {}
    for i, m in enumerate(matches):
        qnum = int(m.group(1))
        start = m.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        question_text = text[start:end]
        
        subj = detect_question_subject(question_text)
        if subj:
            question_subjects[qnum] = subj
    
    subject_ranges = {}
    for qnum, subj in question_subjects.items():
        if subj not in subject_ranges:
            subject_ranges[subj] = [qnum, qnum]
        else:
            subject_ranges[subj][0] = min(subject_ranges[subj][0], qnum)
            subject_ranges[subj][1] = max(subject_ranges[subj][1], qnum)
    
    return {subj: (r[0], r[1]) for subj, r in subject_ranges.items()}


def normalize_block(block: str) -> str:
    """標準化題目區塊（處理選項標記）"""
    for k, v in MARKER_MAP.items():
        block = block.replace(k, '\n' + v + ' ')
    return block


def clean_text(text: str) -> str:
    """清理文字（移除多餘空格）"""
    ch_space = re.compile(r'(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])')
    ch_punct = re.compile(r'([，。、；：！？])\s+')
    
    text = re.sub(r'\s+', ' ', ' '.join(text.splitlines())).strip()
    text = ch_space.sub('', text)
    text = ch_punct.sub(r'\1', text)
    return text


def convert_exam(paper_path: Path, ans_path: Path, subject: str) -> Path:
    """將 PDF 考古題轉換為 Markdown"""
    
    # 提取路徑資訊
    year = paper_path.stem.split('_')[0][:3]
    exam_code = paper_path.stem.split('_')[1]
    output_path = paper_path.parent / subject / f'{paper_path.stem}.md'
    
    # 提取 PDF 內容
    paper_pages = extract_pages(paper_path)
    ans_pages = extract_pages(ans_path)
    
    paper_text = '\n\n'.join(paper_pages).replace('\r\n', '\n')
    ans_text = '\n\n'.join(ans_pages)
    
    # 偵測題號範圍
    detected_ranges = detect_subject_ranges(paper_text)
    
    if subject in detected_ranges:
        start_q, end_q = detected_ranges[subject]
        selected = range(start_q, end_q + 1)
        print(f'[自動偵測] {subject}: 第{start_q}-{end_q}題')
    elif exam_code in DEFAULT_SUBJECT_CONFIG and subject in DEFAULT_SUBJECT_CONFIG[exam_code]:
        selected, _ = DEFAULT_SUBJECT_CONFIG[exam_code][subject]
        print(f'[使用預設] {subject}: 第{selected.start}-{selected.stop-1}題')
    else:
        raise ValueError(f'無法判斷 {subject} 的題號範圍，請手動指定')
    
    exam_name = EXAM_NAMES.get(exam_code, f'綜合法學（{exam_code}）')
    
    # 解析題目
    pattern = re.compile(r'(?m)^(\d{1,2})\s')
    matches = list(pattern.finditer(paper_text))
    questions = {}
    for i, m in enumerate(matches):
        qnum = int(m.group(1))
        start = m.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(paper_text)
        block = paper_text[start:end].strip()
        questions[qnum] = block
    
    # 解析答案
    answers = {}
    letters = []
    for line in ans_text.splitlines():
        line = line.strip()
        if line.startswith('答案'):
            letters.extend(re.findall(r'[ABCD]', line))
    for idx, letter in enumerate(letters, start=1):
        answers[idx] = letter
    
    # 產生 Markdown
    opt_pattern = re.compile(r'\(A\)|\(B\)|\(C\)|\(D\)')
    md_lines = []
    md_lines.append(f'# {year}年司法官律師考試 - {subject}（{exam_code}）')
    md_lines.append('')
    md_lines.append('> 113年公務人員特種考試司法官考試（第一試）  ')
    md_lines.append('> 113年專門職業及技術人員高等考試律師考試（第一試）  ')
    md_lines.append(f'> 科目：{exam_name}  ')
    md_lines.append(f'> 本文件僅整理{subject}部分（第{selected.start}-{selected.stop-1}題）')
    md_lines.append('')
    md_lines.append('---')
    md_lines.append('')
    
    for qnum in selected:
        block = questions.get(qnum, '')
        if not block:
            md_lines.append(f'## 第{qnum}題')
            md_lines.append('（原始題目擷取失敗）')
            md_lines.append('')
            md_lines.append(f'### 答案：({answers.get(qnum, "")})')
            md_lines.append('')
            md_lines.append('---')
            md_lines.append('')
            continue
        
        block = normalize_block(block)
        block = re.sub(r'代號：\d+\s*\n?頁次：.*?(\n|$)', '\n', block)
        
        first_opt = opt_pattern.search(block)
        if first_opt:
            qtext = block[:first_opt.start()].strip()
            rest = block[first_opt.start():].strip()
        else:
            qtext = block.strip()
            rest = ''
        
        qtext = re.sub(r'^\d{1,2}\s+', '', qtext).strip()
        qtext = clean_text(qtext)
        
        options = {}
        if rest:
            opt_matches = list(opt_pattern.finditer(rest))
            for i, m in enumerate(opt_matches):
                key = m.group(0).strip('()')
                start = m.end()
                end = opt_matches[i+1].start() if i+1 < len(opt_matches) else len(rest)
                text = rest[start:end].strip()
                text = clean_text(text)
                options[key] = text
        
        md_lines.append(f'## 第{qnum}題')
        md_lines.append(qtext)
        md_lines.append('')
        
        for key in ['A', 'B', 'C', 'D']:
            if key in options:
                md_lines.append(f'({key}) {options[key]}  ')
            else:
                md_lines.append(f'({key})')
        
        md_lines.append('')
        md_lines.append(f'### 答案：({answers.get(qnum, "")})')
        md_lines.append('')
        md_lines.append('---')
        md_lines.append('')
    
    md = '\n'.join(md_lines).rstrip() + '\n'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md, encoding='utf-8')
    
    return output_path


def main():
    if len(sys.argv) != 4:
        print('用法：python convert_exam.py <paper_path> <ans_path> <subject>')
        print('範例：python convert_exam.py 考古題/113110_2301.pdf 考古題/113110_ANS2301.pdf 憲法')
        sys.exit(1)
    
    paper_path = Path(sys.argv[1])
    ans_path = Path(sys.argv[2])
    subject = sys.argv[3]
    
    # 處理相對路徑
    if not paper_path.is_absolute():
        paper_path = Path.cwd() / paper_path
    if not ans_path.is_absolute():
        ans_path = Path.cwd() / ans_path
    
    # 檢查檔案是否存在
    if not paper_path.exists():
        print(f'檔案不存在：{paper_path}')
        sys.exit(1)
    if not ans_path.exists():
        print(f'檔案不存在：{ans_path}')
        sys.exit(1)
    
    output_path = convert_exam(paper_path, ans_path, subject)
    print(f'已產生：{output_path}')


if __name__ == '__main__':
    main()
