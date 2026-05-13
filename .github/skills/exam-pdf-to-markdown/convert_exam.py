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
try:
    import fitz  # PyMuPDF；用於 pdfplumber 抽出亂碼時的 fallback
except ImportError:
    fitz = None

# Windows cp950 環境下，避免 print 含 PUA/罕用字時崩潰
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

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

#  Unicode 私用區選項標記（複選題用 A-E，故含 \ue190）
MARKER_MAP = {'\ue18c': '(A)', '\ue18d': '(B)', '\ue18e': '(C)', '\ue18f': '(D)', '\ue190': '(E)'}
OPT_PAT = re.compile(r'\(A\)|\(B\)|\(C\)|\(D\)|\(E\)')
CH_SPACE = re.compile(r'(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])')
CH_PUNCT = re.compile(r'([，。、；：！？）」])\s+')


def _fitz_extract_with_pua(path):
    """使用 PyMuPDF 的 rawdict 抽取，保留 PUA 字元（如 \\ue18c=(A) 等選項標記）。"""
    if fitz is None:
        return ''
    doc = fitz.open(str(path))
    pages = []
    for p in doc:
        rd = p.get_text("rawdict")
        out = []
        for block in rd.get('blocks', []):
            if 'lines' not in block:
                continue
            for line in block['lines']:
                line_chars = []
                for span in line.get('spans', []):
                    for ch in span.get('chars', []):
                        line_chars.append(ch.get('c', ''))
                out.append(''.join(line_chars))
        pages.append('\n'.join(out))
    doc.close()
    return '\n\n'.join(pages)


def extract_pdf(path):
    pages = []
    with pdfplumber.open(path) as pdf:
        for p in pdf.pages:
            pages.append(p.extract_text() or '')
    text = '\n\n'.join(pages).replace('\r\n', '\n')
    # 偵測抽取品質：CJK 字元比例。104-107 PDF 使用 CID 字型，
    # pdfplumber 會抽出大量亂碼；此時改用 PyMuPDF rawdict 重抽以保留正確字元與 PUA 標記。
    cjk = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    ratio = cjk / max(len(text), 1)
    if ratio < 0.15 and fitz is not None:
        print(f'[警告] pdfplumber 抽取 CJK 比例僅 {ratio:.1%}，改用 PyMuPDF 重抽: {path.name}')
        text = _fitz_extract_with_pua(path).replace('\r\n', '\n')
    return text


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
    # 題號必須單調遞增；過濾掉跨頁誤判的「假題號」（例如金額尾數「5 千元以下」）
    filtered = []
    last_qnum = 0
    for m in matches:
        qnum = int(m.group(1))
        # 合理的下一題號：> last_qnum 且不超過 last_qnum + 5（避免大幅跳號）
        if qnum > last_qnum and qnum <= last_qnum + 5 and qnum <= 200:
            filtered.append(m)
            last_qnum = qnum
    questions = {}
    for i, m in enumerate(filtered):
        qnum = int(m.group(1))
        start = m.start()
        end = filtered[i + 1].start() if i + 1 < len(filtered) else len(paper_text)
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


def parse_answers_by_coords(ans_path):
    """對考選部「答案表格 PDF」用座標配對：
    每列上方是「第N題」題號 spans，下方是對應答案字母 spans。
    可正確處理：題號跳序（如 MOD 把第13題排到第40題後）、複選答案（ABDE）、更正記號 #。
    回傳 {題號: 答案字串} 或 None（fallback 失敗）。
    """
    if fitz is None:
        return None
    try:
        doc = fitz.open(str(ans_path))
    except Exception:
        return None
    result = {}
    for page in doc:
        rd = page.get_text("dict")
        qspans = []  # (x, y, qnum)
        aspans = []  # (x, y, letter)
        for block in rd.get('blocks', []):
            for line in block.get('lines', []):
                for span in line.get('spans', []):
                    t = span['text'].strip()
                    bbox = span['bbox']
                    cy = (bbox[1] + bbox[3]) / 2
                    # 題號 span：「第N題」，可能多個合併
                    qmatches = list(re.finditer(r'第(\d+)題', t))
                    if qmatches:
                        n_q = len(qmatches)
                        w = bbox[2] - bbox[0]
                        for idx, m in enumerate(qmatches):
                            qnum = int(m.group(1))
                            x = bbox[0] + w * (idx + 0.5) / n_q
                            qspans.append((x, cy, qnum))
                    # 答案 span：純字母組合（含 #、ABCDE）
                    elif re.fullmatch(r'[A-E#]+', t):
                        cx = (bbox[0] + bbox[2]) / 2
                        aspans.append((cx, cy, t))
        # 依題號 y 群組
        if not qspans:
            continue
        ys = sorted(set(round(q[1] / 5) * 5 for q in qspans))
        for qrow in ys:
            row_qs = sorted([q for q in qspans if abs(q[1] - qrow) < 8], key=lambda x: x[0])
            row_as = sorted([a for a in aspans if 5 < a[1] - qrow < 30], key=lambda x: x[0])
            # 依 x 順序配對
            for i, (qx, _, qnum) in enumerate(row_qs):
                if i < len(row_as):
                    result[qnum] = row_as[i][2]
    doc.close()
    return result if result else None


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
    # 移除 PUA 私用區字元（PDF CID 字型可能殘留），避免 cp950 編碼錯誤
    exam_name = re.sub(r'[\ue000-\uf8ff]', '', exam_name)
    return year, exam_name


def question_to_md(seq, qnum, block, answer, cross_note=None):
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
    if cross_note:
        lines.insert(1, f'> ⚠️ {cross_note}')
        lines.insert(2, '')
    # 動態決定要輸出 ABCD 或 ABCDE：若 options 含 E（複選題），則輸出五個
    keys = 'ABCDE' if 'E' in options else 'ABCD'
    for k in keys:
        lines.append(f'({k}) {options.get(k, "")}  ')
    lines += ['', f'### 答案：({answer})', '', '---', '']
    return lines


def main():

    # 先解析參數，確保 paper_path, ans_path 已定義
    if len(sys.argv) < 3:
        print('用法: python convert_exam.py <考卷PDF> <答案卷PDF> [<輸出md路徑>] [--single]')
        sys.exit(1)

    paper_path = Path(sys.argv[1]).resolve()
    ans_path = Path(sys.argv[2]).resolve()
    single_mode = False
    output_path = None
    for arg in sys.argv[3:]:
        if arg == '--single':
            single_mode = True
        elif arg.endswith('.md'):
            output_path = Path(arg).resolve()

    print(f'[讀取] 考卷: {paper_path}')
    print(f'[讀取] 答案: {ans_path}')

    paper_text = extract_pdf(paper_path)
    ans_text = extract_pdf(ans_path)
    questions = parse_questions(paper_text)
    # 答案優先用座標法（可正確處理 MOD 重排、複選、CID 字型 PDF），失敗再退回文字法
    answers = parse_answers_by_coords(ans_path)
    if answers and len(answers) >= len(questions):
        print(f'[資訊] 答案以座標法解析：{len(answers)} 題')
    else:
        answers = parse_answers(ans_text)
    year, exam_name = extract_exam_info(paper_text)

    # 一律從檔名取得年度（PDF 內容可能含舊法條年份參照，不可靠）
    year = paper_path.stem.split('_')[0][:3]

    m = re.search(r'代號[：:]	*(\d+)', paper_text)
    exam_code = m.group(1) if m else paper_path.stem.split('_')[1][:4]

    print(f'[資訊] 年度={year}, 代號={exam_code}, 科目={exam_name}')
    print(f'[資訊] 共 {len(questions)} 題, 答案 {len(answers)} 題')
    print()

    if single_mode:
        # 單檔模式：所有題目合併為一個 md 檔
        if not output_path:
            output_path = paper_path.parent / f'{paper_path.stem.split("_")[0]}_{exam_code}.md'
        md = []
        md.append(f'# {year}年司法官律師考試 - 綜合法學（{exam_code}）')
        md.append('')
        md.append(f'> {year}年公務人員特種考試司法官考試（第一試）  ')
        md.append(f'> {year}年專門職業及技術人員高等考試律師考試（第一試）  ')
        md.append(f'> 科目：{exam_name}  ')
        md.append('')
        md.append('---')
        md.append('')
        for seq, qnum in enumerate(sorted(questions.keys()), start=1):
            ans = answers.get(qnum, '?')
            md.extend(question_to_md(seq, qnum, questions[qnum], ans))
        output_path.write_text('\n'.join(md).rstrip() + '\n', encoding='utf-8')
        print(f'[寫入] {output_path}')
        summary = {
            'year': year,
            'exam_code': exam_code,
            'exam_name': exam_name,
            'created_files': [str(output_path)],
            'subjects': {},
            'unclassified': [],
            'unclassified_texts': {},
        }
        print('\n=== JSON ===')
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return

    # --- 多科目分科邏輯 ---

    # 從檔名取得前綴（如 '104110'）
    file_prefix = paper_path.stem.split('_')[0]

    # 一律從檔名取得年度（PDF 內容可能含舊法條年份參照，不可靠）
    year = file_prefix[:3]

    # 工作目錄（考古題/科目/ 的上層）
    workspace = paper_path.parent.parent.parent  # PDF→科目資料夾→考古題→LawExam

    # 預設題號範圍（依代號）
    DEFAULT_RANGES = {
        '1301': [('刑法', 1, 35), ('刑事訴訟法', 36, 60), ('法律倫理', 61, 75)],
        '2301': [('憲法', 1, 20), ('行政法', 21, 55), ('國際公法', 56, 65), ('國際私法', 66, 75)],
        '3301': [('民法', 1, 50), ('民事訴訟法', 51, 80)],
    }

    # 年份特定邊界覆蓋（104-106年舊制憲法僅14題；範圍重疊表示跨科題，兩邊都收錄）
    BOUNDARY_OVERRIDES = {
        # 104年：舊制，憲法14題，行政法41題
        ('2301', '104'): [('憲法', 1, 14), ('行政法', 15, 55), ('國際公法', 56, 65), ('國際私法', 66, 75)],
        # 105年：舊制，Q14「法律保留原則」為跨科題（憲法§23 / 行政法段階理論），兩科都收錄
        ('2301', '105'): [('憲法', 1, 14), ('行政法', 14, 55), ('國際公法', 56, 65), ('國際私法', 66, 75)],
        # 106年：舊制，憲法14題，行政法41題
        ('2301', '106'): [('憲法', 1, 14), ('行政法', 15, 55), ('國際公法', 56, 65), ('國際私法', 66, 75)],
        # 107年以後：維持預設 Q1-20=憲法（不需要特殊處理）
    }

    EXAM_FULL_NAMES = {
        '1301': '綜合法學（一）（刑法、刑事訴訟法、法律倫理）',
        '2301': '綜合法學（一）（憲法、行政法、國際公法、國際私法）',
        '3301': '綜合法學（二）（民法、民事訴訟法）',
    }

    exam_full_name = EXAM_FULL_NAMES.get(exam_code, exam_name)
    # 優先使用年份特定覆蓋，否則使用預設範圍
    ranges = BOUNDARY_OVERRIDES.get((exam_code, year), DEFAULT_RANGES.get(exam_code))

    # 建立 qnum→[科目] 對應表（支援重疊範圍：跨科題同時屬多科）
    subj_map = {}
    if ranges:
        for subj, start, end in ranges:
            for qnum in range(start, end + 1):
                subj_map.setdefault(qnum, []).append(subj)

    cross_subject_qnums = {qnum for qnum, subjs in subj_map.items() if len(subjs) > 1}

    # 依題號分組
    subject_groups = {}  # subject -> [qnum, ...]
    unclassified = []

    all_qnums = sorted(questions.keys())

    if subj_map and exam_code in ('2301', '3301'):
        # 2301/3301 直接使用預設分界（關鍵字分類對這兩組可靠性低）
        # 支援跨科題：一題可同時加入多科
        for qnum in all_qnums:
            subjs = subj_map.get(qnum, [])
            if subjs:
                for subj in subjs:
                    subject_groups.setdefault(subj, []).append(qnum)
            else:
                unclassified.append(qnum)
    else:
        # 1301 或未知代號：以關鍵字分類為主，預設範圍為備援
        for qnum in all_qnums:
            subj, best_score, second_score = classify_question(questions[qnum])
            need_fallback = (
                subj is None or
                best_score <= 2 or
                (best_score - second_score) <= 1
            )
            if need_fallback:
                fallback_subjs = subj_map.get(qnum, [])
                subj = fallback_subjs[0] if fallback_subjs else None
            if subj:
                subject_groups.setdefault(subj, []).append(qnum)
            else:
                unclassified.append(qnum)

        # 連續性修正：孤立題目合併至前後主流科目
        if unclassified and subject_groups:
            last_known = None
            for qnum in sorted(all_qnums):
                if qnum in unclassified:
                    if last_known:
                        subject_groups[last_known].append(qnum)
                        unclassified.remove(qnum)
                else:
                    for s, qs in subject_groups.items():
                        if qnum in qs:
                            last_known = s
                            break

    # 輸出各科目 Markdown
    created_files = []
    summary_subjects = {}

    for subj, qnums in subject_groups.items():
        qnums_sorted = sorted(qnums)
        first_q, last_q = qnums_sorted[0], qnums_sorted[-1]

        out_dir = workspace / '考古題' / subj
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f'{file_prefix}_{exam_code}.md'

        md = []
        md.append(f'# {year}年司法官律師考試 - {subj}（{exam_code}）')
        md.append('')
        md.append(f'> {exam_full_name}  ')
        md.append(f'> 科目：{subj}  ')
        md.append(f'> 本文件僅整理{subj}部分（第{first_q}-{last_q}題）  ')
        md.append('')
        md.append('---')
        md.append('')
        for seq, qnum in enumerate(qnums_sorted, start=1):
            ans = answers.get(qnum, '?')
            other_subjs = [s for s in subj_map.get(qnum, []) if s != subj]
            cross_note = f'本題同時收錄於{"、".join(other_subjs)}（跨科題）' if other_subjs else None
            md.extend(question_to_md(seq, qnum, questions[qnum], ans, cross_note=cross_note))

        out_path.write_text('\n'.join(md).rstrip() + '\n', encoding='utf-8')
        print(f'[寫入] {out_path}  （{len(qnums_sorted)} 題，第{first_q}-{last_q}題）')
        created_files.append(str(out_path))
        summary_subjects[subj] = {
            'count': len(qnums_sorted),
            'range': f'{first_q}-{last_q}',
            'questions': qnums_sorted,
        }

    if unclassified:
        print(f'[警告] 未分類題目: {unclassified}')

    summary = {
        'year': year,
        'exam_code': exam_code,
        'exam_name': exam_full_name,
        'file_prefix': file_prefix,
        'created_files': created_files,
        'subjects': summary_subjects,
        'unclassified': unclassified,
    }
    print('\n=== JSON ===')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
