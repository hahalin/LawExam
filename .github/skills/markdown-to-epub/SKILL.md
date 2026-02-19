````skill
---
name: markdown-to-epub
description: 將 Markdown 檔案轉換為 EPUB 電子書格式。適用於考古題、課程字幕等學習資料的離線閱讀。使用指令格式：「{路徑} 轉換為epub」
---

# Markdown 轉 EPUB 技能

## 功能說明

此技能用於將 Markdown 檔案轉換為 EPUB 電子書格式，方便在電子書閱讀器或手機上離線閱讀。

## Skill 資源

本 skill 資料夾包含：
- `SKILL.md` - 技能說明文件（本檔案）
- `convert_to_epub.py` - 轉換腳本

共用資源：
- `../shared/python_env.md` - Python 環境設定說明

## 適用情境

- 將考古題 Markdown 檔案轉換為 EPUB 以便行動裝置閱讀
- 將課程字幕 Markdown 檔案轉換為電子書格式
- 將主題整理筆記轉換為方便攜帶的電子書

## 指令格式

使用者會以下列格式指派任務：

```
{MD檔案路徑} 轉換為epub
```

### 範例

```
考古題/刑法/114110_1301.md 轉換為epub
```

### 解析指令

從指令中提取：
1. **MD 檔案路徑**：「轉換為epub」前的路徑（如 `考古題/刑法/114110_1301.md`）
2. **輸出路徑**：同資料夾，副檔名改為 `.epub`（如 `考古題/刑法/114110_1301.epub`）

### 跳過與更新規則（必須遵守）

- 若對應的 `.epub` 已存在，且 MD 檔案**未被修改**（MD 修改時間 ≤ EPUB 修改時間），則**跳過不處理**
- 若對應的 `.epub` 已存在，但 MD 檔案**已被更新**（MD 修改時間 > EPUB 修改時間），則**重新產生 EPUB 取代舊檔**
- 例如：`考古題/刑法/114110_1301.md` 若已有 `考古題/刑法/114110_1301.epub`，且 MD 檔未修改，則跳過；若 MD 檔已更新，則重新產生 EPUB

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
- `ebooklib`：用於產生 EPUB 檔案
- `markdown`：用於將 Markdown 轉換為 HTML

### 安裝必要套件
```powershell
C:/Users/User/anaconda3/Scripts/conda.exe run -n tf_gpu_env --no-capture-output python -m pip install ebooklib markdown -q
```

## 執行步驟

### 1. 解析使用者指令

從指令中提取：
- `md_path`：MD 檔案路徑（如 `考古題/刑法/114110_1301.md`）
- `epub_path`：輸出路徑，同資料夾、同檔名、副檔名改為 `.epub`（如 `考古題/刑法/114110_1301.epub`）

### 2. 檢查是否需要轉換

- 若 `.epub` 不存在：直接執行轉換
- 若 `.epub` 已存在且 MD 檔未更新：告知使用者並跳過
- 若 `.epub` 已存在但 MD 檔已更新：重新產生 EPUB 取代舊檔

### 3. 執行轉換

使用本 skill 資料夾內的 `convert_to_epub.py` 腳本：

```powershell
C:/Users/User/anaconda3/Scripts/conda.exe run -n tf_gpu_env --no-capture-output python .github/skills/markdown-to-epub/convert_to_epub.py "{完整絕對路徑}"
```

**重要**：必須傳入**絕對路徑**，避免路徑解析錯誤。

### 範例

```powershell
C:/Users/User/anaconda3/Scripts/conda.exe run -n tf_gpu_env --no-capture-output python .github/skills/markdown-to-epub/convert_to_epub.py "D:/repo/LawExam/考古題/刑法/114110_1301.md"
```

### 4. 腳本位置

- **腳本路徑**：`.github/skills/markdown-to-epub/convert_to_epub.py`
- **必要套件**：`ebooklib`, `markdown`

### 5. 腳本運作邏輯

1. 檢查 EPUB 檔是否已存在：
   - 若已存在且 MD 檔未更新（MD 修改時間 ≤ EPUB 修改時間）→ 跳過
   - 若已存在但 MD 檔已更新（MD 修改時間 > EPUB 修改時間）→ 重新產生 EPUB 取代舊檔
   - 若不存在 → 繼續產生新 EPUB
2. 讀取 Markdown 檔案（UTF-8 編碼）
3. 從 Markdown 內容中提取第一個 `#` 標題作為書名；若無標題則使用檔名
3. 使用 `markdown` 套件將 Markdown 轉為 HTML
4. 使用 `ebooklib` 產生 EPUB 檔案，包含：
   - 書名（title）
   - 語言設定為 `zh-TW`
   - 單一章節包含完整 HTML 內容
   - 內建基本 CSS 樣式（適合中文閱讀）
5. 輸出 EPUB 檔案到同目錄

## 注意事項

1. **編碼**：確保 Markdown 檔案為 UTF-8 編碼，避免亂碼
2. **智慧更新**：若 MD 檔案在 EPUB 產生後被修改，會自動重新產生 EPUB 取代舊檔；若未修改則跳過
3. **路徑**：必須使用絕對路徑傳入腳本
4. **書名**：自動從 Markdown 第一個 `#` 標題取得，若無則用檔名
5. **中文支援**：EPUB 內建的 CSS 已針對中文閱讀優化行距與字體大小

## 常見問題與解決方案

### 問題：使用相對路徑執行腳本時失敗

**解決方案**：傳入絕對路徑。

❌ 錯誤用法：
```powershell
C:/Users/User/anaconda3/Scripts/conda.exe run -n tf_gpu_env --no-capture-output python .github/skills/markdown-to-epub/convert_to_epub.py 考古題/刑法/114110_1301.md
```

✅ 正確用法：
```powershell
C:/Users/User/anaconda3/Scripts/conda.exe run -n tf_gpu_env --no-capture-output python .github/skills/markdown-to-epub/convert_to_epub.py "D:/repo/LawExam/考古題/刑法/114110_1301.md"
```

````
