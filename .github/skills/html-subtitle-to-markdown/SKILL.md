---
name: html-subtitle-to-markdown
description: 將包含字幕的 HTML 檔案轉換為 Markdown 格式。適用於線上課程字幕的提取與整理，特別是法律考試準備課程。使用指令格式：「{路徑} 轉換為字幕檔」
---

# 字幕 HTML 轉 Markdown 技能

## 功能說明

此技能用於將包含字幕的 HTML 檔案轉換為結構化的 Markdown 檔案，方便後續學習與複習。

## Skill 資源

本 skill 資料夾包含：
- `SKILL.md` - 技能說明文件（本檔案）
- `convert_subtitle.py` - 轉換腳本
- `examples/` - 輸出範例
  - `sample_output.md` - Markdown 輸出範例

共用資源：
- `../shared/python_env.md` - Python 環境設定說明

## 適用情境

- 線上課程字幕的提取與整理
- 法律考試準備課程的字幕檔案處理
- 將 HTML 格式的字幕轉換為易讀的 Markdown 格式

## 指令格式

使用者會以下列格式指派任務：

```
{HTML檔案路徑} 轉換為字幕檔
```

### 範例

```
刑法/06.html 轉換為字幕檔
```

### 解析指令

從指令中提取：
1. **HTML 檔案路徑**：「轉換為字幕檔」前的路徑（如 `刑法/06.html`）
2. **輸出路徑**：同資料夾，副檔名改為 `.md`（如 `刑法/06.md`）

### 跳過規則（必須遵守）

- 只要對應的 `.md` 已存在，就**不處理**，並告知使用者
- 例如：`刑法/06.html` 若已有 `刑法/06.md`，必須跳過，不可覆蓋

## Python 環境設定

### 環境資訊
- **環境類型**：Conda
- **環境名稱**：tf_gpu_env
- **Python 版本**：3.12.4

### 執行 Python 的指令前綴
```powershell
C:/Users/User/anaconda3/Scripts/conda.exe run -n tf_gpu_env --no-capture-output python
```

### 必要套件
- `beautifulsoup4`：用於解析 HTML

### 安裝必要套件
```powershell
C:/Users/User/anaconda3/Scripts/conda.exe run -n tf_gpu_env --no-capture-output python -m pip install beautifulsoup4 -q
```

## 執行步驟

### 1. 解析使用者指令

從指令中提取：
- `html_path`：HTML 檔案路徑（如 `課程字幕/刑法/06.html`）
- `md_path`：輸出路徑，同資料夾、同檔名、副檔名改為 `.md`（如 `課程字幕/刑法/06.md`）

### 2. 檢查是否已存在

若 `.md` 檔案已存在，告知使用者並跳過，不可覆蓋。

### 3. 執行轉換

使用本 skill 資料夾內的 `convert_subtitle.py` 腳本：

```powershell
C:/Users/User/anaconda3/Scripts/conda.exe run -n tf_gpu_env --no-capture-output python .github/skills/html-subtitle-to-markdown/convert_subtitle.py 刑法/06.html
```

腳本會自動：
- 檢查 `.md` 是否已存在（存在則跳過）
- 將相對路徑轉為絕對路徑
- 提取字幕並產生 Markdown 檔案

### 4. 腳本位置

- **腳本路徑**：`.github/skills/html-subtitle-to-markdown/convert_subtitle.py`
- **必要套件**：`beautifulsoup4`

### 5. 腳本運作邏輯

腳本預期的 HTML 結構：

```html
<div class="css-10s8ss9">
  <p>00:00:00 - 00:01:23</p>
  <p>字幕內容</p>
</div>
```

或備用格式（連續的 `<p>` 標籤）：

```html
<p>00:00:00 - 00:01:23</p>
<p>字幕內容</p>
```

## Markdown 輸出格式

```markdown
# 課程名稱：{科目}{編號}

HH:MM:SS - HH:MM:SS  
字幕內容第一段

HH:MM:SS - HH:MM:SS  
字幕內容第二段
```

## 注意事項

1. **編碼**：確保 HTML 檔案為 UTF-8 編碼，避免亂碼
2. **不覆蓋**：已存在的 `.md` 檔案不會被覆蓋
3. **HTML 結構**：需要特定的 HTML 結構才能正確提取字幕
4. **課程名稱**：自動從資料夾名稱和檔案名稱組合生成

## 常見問題與解決方案

### 問題：使用相對路徑執行腳本時失敗（exit code 1，無輸出）

**原因**：腳本中的路徑處理邏輯是以腳本所在位置為基準，而非工作目錄。當傳入相對路徑如 `刑法/08.html` 時，腳本會嘗試從 `.github/skills/html-subtitle-to-markdown/刑法/08.html` 尋找檔案，導致找不到檔案而失敗。

**解決方案**：傳入絕對路徑而非相對路徑。

❌ 錯誤用法：
```powershell
C:/Users/User/anaconda3/Scripts/conda.exe run -n tf_gpu_env --no-capture-output python .github/skills/html-subtitle-to-markdown/convert_subtitle.py 課程字幕/刑法/08.html
```

✅ 正確用法：
```powershell
C:/Users/User/anaconda3/Scripts/conda.exe run -n tf_gpu_env --no-capture-output python .github/skills/html-subtitle-to-markdown/convert_subtitle.py "D:/repo/LawExam/課程字幕/刑法/08.html"
```

**執行步驟中的指令也應使用絕對路徑**：
```powershell
C:/Users/User/anaconda3/Scripts/conda.exe run -n tf_gpu_env --no-capture-output python .github/skills/html-subtitle-to-markdown/convert_subtitle.py "{完整絕對路徑}"
```

## 批次處理

若需要批次處理所有 HTML 檔案，可使用專案根目錄的 `generate_subtitles.py` 腳本：

```powershell
C:/Users/User/anaconda3/Scripts/conda.exe run -n tf_gpu_env --no-capture-output python generate_subtitles.py
```

此腳本會自動處理所有子資料夾中的 HTML 檔案，並跳過已存在的 `.md` 檔案。

## 輸出範例

- [刑法/01.md](../../../課程字幕/刑法/01.md)
- [憲法/01.md](../../../課程字幕/憲法/01.md)
- [行政法/01.md](../../../課程字幕/行政法/01.md)
