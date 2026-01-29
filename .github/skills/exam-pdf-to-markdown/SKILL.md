---
name: exam-pdf-to-markdown
description: 將法律考試 PDF 試卷與答案卷轉換為結構化的 Markdown 檔案。使用指令格式：「{考卷路徑}是考卷 / {答案卷路徑}是答案卷 / 整理{科目}考古題檔」。支援自動識別題目科目。
---

# 考古題 PDF 轉 Markdown 技能

## 功能說明

此技能用於將法律考試的 PDF 試卷與答案卷轉換為結構化的 Markdown 檔案，方便後續學習與複習。

## Skill 資源

本 skill 資料夾包含：
- `SKILL.md` - 技能說明文件（本檔案）
- `convert_exam.py` - 轉換腳本
- `examples/` - 輸出範例
  - `sample_output.md` - Markdown 輸出範例

共用資源：
- `../shared/python_env.md` - Python 環境設定說明

## 適用情境

- 使用者提供考古題 PDF 檔案（試卷與答案卷）
- 需要整理特定科目的考古題（如刑法、民法、行政法等）
- 需要將題目與答案整合為易讀的 Markdown 格式

## 指令格式

使用者會以下列格式指派任務：

```
{考卷路徑}是考卷
{答案卷路徑}是答案卷
整理{科目}考古題檔
```

### 範例

```
考古題/113110_2301.pdf是考卷
考古題/113110_ANS2301.pdf是答案卷
整理憲法考古題檔
```

### 解析指令

從指令中提取以下資訊：
1. **考卷路徑**：第一行「是考卷」前的路徑
2. **答案卷路徑**：第二行「是答案卷」前的路徑
3. **科目名稱**：第三行「整理」與「考古題檔」之間的文字

### 自動判斷題號範圍

程式會根據**每道題目的內容特徵**自動判斷所屬科目：
- 分析題目中的法律術語和關鍵字
- 計算各科目的匹配分數，選擇分數最高者
- 自動建立科目→題號範圍的對應

例如：題目提到「行政處分」、「訴願」、「行政訴訟」→ 判斷為行政法

若自動偵測失敗，則使用以下預設值：

| 試卷代號 | 科目 | 預設題號範圍 | exam_name |
|----------|------|--------------|-----------|
| 1301 | 刑法 | 1-35 | 綜合法學（二）（刑法、刑事訴訟法、法律倫理） |
| 1301 | 刑事訴訟法 | 36-60 | 綜合法學（二）（刑法、刑事訴訟法、法律倫理） |
| 1301 | 法律倫理 | 61-75 | 綜合法學（二）（刑法、刑事訴訟法、法律倫理） |
| 2301 | 憲法 | 1-20 | 綜合法學（一）（憲法、行政法、國際公法、國際私法） |
| 2301 | 行政法 | 21-55 | 綜合法學（一）（憲法、行政法、國際公法、國際私法） |
| 2301 | 國際公法 | 56-65 | 綜合法學（一）（憲法、行政法、國際公法、國際私法） |
| 2301 | 國際私法 | 66-75 | 綜合法學（一）（憲法、行政法、國際公法、國際私法） |

### 輸出檔案路徑

輸出至 `考古題/{科目}/{考卷檔名}.md`，例如：
- 輸入：`考古題/113110_2301.pdf`，科目：`憲法`
- 輸出：`考古題/憲法/113110_2301.md`

## Python 環境設定

### 環境資訊
- **環境類型**：Conda
- **環境名稱**：tf_gpu_env
- **Python 版本**：3.12.4

### 執行 Python 的指令前綴
```powershell
C:/Users/User/anaconda3/Scripts/conda.exe run -n tf_gpu_env --no-capture-output python
```

### 安裝必要套件
```powershell
C:/Users/User/anaconda3/Scripts/conda.exe run -n tf_gpu_env --no-capture-output python -m pip install pdfplumber -q
```

## 執行步驟

### 1. 解析使用者指令

從指令中提取：
- `paper_path`：考卷 PDF 路徑
- `ans_path`：答案卷 PDF 路徑
- `subject`：科目名稱

### 2. 根據科目判斷參數

根據檔名中的代號（如 `2301`）和科目名稱，查表得到：
- `selected`：題號範圍
- `exam_name`：科目全名
- `exam_code`：試卷代號

### 3. 執行轉換

使用本 skill 資料夾內的 `convert_exam.py` 腳本：

```powershell
C:/Users/User/anaconda3/Scripts/conda.exe run -n tf_gpu_env --no-capture-output python .github/skills/exam-pdf-to-markdown/convert_exam.py 考古題/113110_2301.pdf 考古題/113110_ANS2301.pdf 憲法
```

腳本會自動：
- 偵測題目所屬科目的題號範圍
- 提取題目與答案
- 產生結構化的 Markdown 檔案

### 4. 完整解析程式碼（備用）

若需要手動執行，可使用 `mcp_pylance_mcp_s_pylanceRunCodeSnippet` 工具執行以下程式碼：

```python
from pathlib import Path
import re

# === 設定區（從使用者指令提取）===
# 從指令「整理{科目}考古題檔」提取
subject = '憲法'

# 從指令「{路徑}是考卷」和「{路徑}是答案卷」提取，轉為絕對路徑
paper_path = Path(r'D:\repo\LawExam\考古題\113110_2301.pdf')
ans_path = Path(r'D:\repo\LawExam\考古題\113110_ANS2301.pdf')

# 輸出路徑：考古題/{科目}/{考卷檔名}.md
output_path = Path(rf'D:\repo\LawExam\考古題\{subject}\{paper_path.stem}.md')

# 從檔名提取年度（前3碼）和代號（後4碼）
# 例如 113110_2301.pdf → year='113', exam_code='2301'
year = paper_path.stem.split('_')[0][:3]
exam_code = paper_path.stem.split('_')[1]

# === PDF 提取 ===
import pdfplumber

def extract_pages(path):
    texts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ''
            texts.append(text)
    return texts

paper_pages = extract_pages(paper_path)
ans_pages = extract_pages(ans_path)

paper_text = '\n\n'.join(paper_pages).replace('\r\n', '\n')
ans_text = '\n\n'.join(ans_pages)

# === 從 PDF 自動偵測科目題號範圍 ===
def detect_question_subject(text):
    """根據題目內容判斷所屬科目"""
    # 各科目的特徵關鍵字（根據題目內容判斷）
    subject_features = {
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
    
    # 計算每個科目的匹配分數
    scores = {}
    for subj, keywords in subject_features.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[subj] = score
    
    # 返回分數最高的科目
    if scores:
        return max(scores, key=scores.get)
    return None

def detect_subject_ranges(text):
    """從 PDF 內容自動偵測各科目的題號範圍"""
    # 解析每道題目
    pattern = re.compile(r'(?m)^(\d{1,2})\s')
    matches = list(pattern.finditer(text))
    
    # 判斷每道題目所屬科目
    question_subjects = {}
    for i, m in enumerate(matches):
        qnum = int(m.group(1))
        start = m.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        question_text = text[start:end]
        
        subj = detect_question_subject(question_text)
        if subj:
            question_subjects[qnum] = subj
    
    # 建立科目範圍（找出每個科目的最小和最大題號）
    subject_ranges = {}
    for qnum, subj in question_subjects.items():
        if subj not in subject_ranges:
            subject_ranges[subj] = [qnum, qnum]
        else:
            subject_ranges[subj][0] = min(subject_ranges[subj][0], qnum)
            subject_ranges[subj][1] = max(subject_ranges[subj][1], qnum)
    
    return {subj: (r[0], r[1]) for subj, r in subject_ranges.items()}

# 嘗試自動偵測，若失敗則使用預設值
detected_ranges = detect_subject_ranges(paper_text)

# 預設的科目配置（作為備用）
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

# exam_name 對照表
EXAM_NAMES = {
    '1301': '綜合法學（二）（刑法、刑事訴訟法、法律倫理）',
    '2301': '綜合法學（一）（憲法、行政法、國際公法、國際私法）',
}

# 決定使用自動偵測還是預設值
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

# === 解析題目 ===
pattern = re.compile(r'(?m)^(\d{1,2})\s')
matches = list(pattern.finditer(paper_text))
questions = {}
for i, m in enumerate(matches):
    qnum = int(m.group(1))
    start = m.start()
    end = matches[i+1].start() if i+1 < len(matches) else len(paper_text)
    block = paper_text[start:end].strip()
    questions[qnum] = block

# === 解析答案 ===
answers = {}
letters = []
for line in ans_text.splitlines():
    line = line.strip()
    if line.startswith('答案'):
        letters.extend(re.findall(r'[ABCD]', line))
for idx, letter in enumerate(letters, start=1):
    answers[idx] = letter

# === 文字清理函數 ===
# PDF 中使用 Unicode 私用區字元表示選項標記
marker_map = {'\ue18c': '(A)', '\ue18d': '(B)', '\ue18e': '(C)', '\ue18f': '(D)'}
opt_pattern = re.compile(r'\(A\)|\(B\)|\(C\)|\(D\)')
ch_space = re.compile(r'(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])')
ch_punct = re.compile(r'([，。、；：！？])\s+')

def normalize_block(block):
    for k, v in marker_map.items():
        block = block.replace(k, '\n' + v + ' ')
    return block

def clean_text(text):
    text = re.sub(r'\s+', ' ', ' '.join(text.splitlines())).strip()
    text = ch_space.sub('', text)
    text = ch_punct.sub(r'\1', text)
    return text

# === 產生 Markdown ===
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

    for key in ['A','B','C','D']:
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
print(f'written: {output_path}')
```

### 4. 使用方式

收到使用者指令後：

1. **解析指令**：從指令中提取 `paper_path`、`ans_path`、`subject`
2. **轉換路徑**：將相對路徑轉為絕對路徑（加上 `D:\repo\LawExam\` 前綴）
3. **修改設定區**：只需修改以下三行：
   ```python
   subject = '憲法'  # 從「整理{科目}考古題檔」提取
   paper_path = Path(r'D:\repo\LawExam\考古題\113110_2301.pdf')  # 從「{路徑}是考卷」提取
   ans_path = Path(r'D:\repo\LawExam\考古題\113110_ANS2301.pdf')  # 從「{路徑}是答案卷」提取
   ```
4. **執行程式碼**：其餘參數（`output_path`、`selected`、`exam_name` 等）會自動計算

### 5. Markdown 結構範本

```markdown
# {年度}年司法官律師考試 - {科目}（{代號}）

> {考試名稱}
> 科目：{科目全名}
> 本文件僅整理{科目}部分（第X-Y題）

---

## 第1題
{題目內容}

(A) {選項A}  
(B) {選項B}  
(C) {選項C}  
(D) {選項D}

### 答案：(X)

---
```

### 6. 格式化要求

1. **選項格式**：每個選項必須獨立成行，行末加上兩個空格以強制換行
2. **題目分隔**：每題之間使用 `---` 分隔線
3. **答案標示**：每題下方標示正確答案
4. **文字清理**：移除中文字間的多餘空格，合併跨行文字

## 輸出範例

- [考古題/刑法/113110_1301.md](../../../考古題/刑法/113110_1301.md)
- [考古題/行政法/113110_2301.md](../../../考古題/行政法/113110_2301.md)

## 注意事項

1. PDF 內容可能因排版問題導致文字斷行不正確，程式會自動清理
2. 選項文字可能跨行，程式會合併為完整句子
3. 答案卷格式可能因年度不同而有差異，需適當調整解析邏輯
4. 若 PDF 無法正確提取文字（如掃描檔），此技能將無法處理
5. 特殊字元（如圈碼選項標記）會自動轉換為標準 (A)(B)(C)(D) 格式
