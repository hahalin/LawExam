````skill
---
name: markdown-to-epub
description: 將 Markdown 檔案轉換為 EPUB 電子書格式。適用於考古題、課程字幕等學習資料的離線閱讀。支援單檔與目錄批次轉換。
---

# Markdown 轉 EPUB 技能

## 功能說明

此技能用於將 Markdown 檔案轉換為 EPUB 電子書格式，方便在電子書閱讀器或手機上離線閱讀。支援單一檔案轉換與目錄批次轉換。

## Skill 資源

本 skill 資料夾包含：
- `SKILL.md` - 技能說明文件（本檔案）
- `convert_to_epub.py` - 轉換腳本（支援單檔與目錄批次模式）

共用資源：
- `../shared/python_env.md` - Python 環境設定說明

## 適用情境

- 將考古題 Markdown 檔案轉換為 EPUB 以便行動裝置閱讀
- 將課程字幕 Markdown 檔案轉換為電子書格式
- 將主題整理筆記轉換為方便攜帶的電子書
- **批次轉換某個目錄下所有 MD 檔案**（如：考古題底下各科目全部轉 EPUB）

## 指令格式

使用者會以下列格式指派任務：

### 單檔轉換
```
考古題/刑法/114110_1301.md 轉換為epub
```

### 批次轉換（目錄）
```
考古題底下各科目的md檔轉為epub
考古題/刑法 全部轉換為epub
```

### 解析指令

從指令中提取：

**單檔模式：**
1. **MD 檔案路徑**：「轉換為epub」前的路徑（如 `考古題/刑法/114110_1301.md`）
2. **輸出路徑**：同資料夾，副檔名改為 `.epub`

**批次模式：**
1. **目錄路徑**：要批次轉換的目錄（如 `考古題` 或 `考古題/刑法`）
2. 腳本會遞迴搜尋目錄下所有 `.md` 檔案並逐一轉換

### 跳過與更新規則（必須遵守）

- 若對應的 `.epub` 已存在，且 MD 檔案**未被修改**（MD 修改時間 ≤ EPUB 修改時間），則**跳過不處理**
- 若對應的 `.epub` 已存在，但 MD 檔案**已被更新**（MD 修改時間 > EPUB 修改時間），則**重新產生 EPUB 取代舊檔**

## Python 環境設定

### 環境資訊
- **環境類型**：Conda
- **環境名稱**：tf_gpu_env
- **Python 版本**：3.12.4

### 執行 Python 的指令（建議使用直接路徑）

由於 `conda run` 在 PowerShell 中輸出中文會亂碼或消失，**建議使用直接 Python 路徑**：

```powershell
C:/Users/User/anaconda3/envs/tf_gpu_env/python.exe
```

> ⚠️ **不建議使用** `conda run` 方式：`C:/Users/User/anaconda3/Scripts/conda.exe run -n tf_gpu_env --no-capture-output python`
> 原因：在 PowerShell 中執行時，中文輸出會變成亂碼，無法正確顯示轉換結果或捕獲輸出。

### 必要套件
- `ebooklib`：用於產生 EPUB 檔案
- `markdown`：用於將 Markdown 轉換為 HTML

### 安裝必要套件
```powershell
C:/Users/User/anaconda3/envs/tf_gpu_env/python.exe -m pip install ebooklib markdown -q
```

## 執行步驟

### 1. 解析使用者指令

判斷是單檔模式或批次模式：

**單檔模式：** 提取 MD 檔案路徑
- `md_path`：MD 檔案路徑（如 `考古題/刑法/114110_1301.md`）

**批次模式：** 提取目錄路徑
- `dir_path`：目錄路徑（如 `考古題` 或 `考古題/刑法`）

### 2. 執行轉換

使用本 skill 資料夾內的 `convert_to_epub.py` 腳本。

#### 單檔轉換

```powershell
C:/Users/User/anaconda3/envs/tf_gpu_env/python.exe .github/skills/markdown-to-epub/convert_to_epub.py "D:/repo/LawExam/考古題/刑法/114110_1301.md"
```

#### 批次轉換（傳入目錄路徑）

```powershell
C:/Users/User/anaconda3/envs/tf_gpu_env/python.exe .github/skills/markdown-to-epub/convert_to_epub.py "D:/repo/LawExam/考古題"
```

腳本會遞迴搜尋目錄下所有 `.md` 檔案，逐一轉換並顯示統計結果：
- 新建數量（新 EPUB）
- 更新數量（MD 已更新，重新產生 EPUB）
- 跳過數量（EPUB 已存在且為最新）
- 失敗數量

**重要**：必須傳入**絕對路徑**，避免路徑解析錯誤。

### 3. 腳本位置與套件

- **腳本路徑**：`.github/skills/markdown-to-epub/convert_to_epub.py`
- **必要套件**：`ebooklib`, `markdown`

### 4. 腳本運作邏輯

#### 單檔模式
1. 檢查 EPUB 檔是否已存在：
   - 若已存在且 MD 檔未更新 → 跳過
   - 若已存在但 MD 檔已更新 → 重新產生 EPUB 取代舊檔
   - 若不存在 → 產生新 EPUB
2. 讀取 Markdown 檔案（UTF-8 編碼）
3. 從 Markdown 內容中提取第一個 `#` 標題作為書名；若無標題則使用檔名
4. 使用 `markdown` 套件將 Markdown 轉為 HTML
5. 使用 `ebooklib` 產生 EPUB 檔案
6. 輸出 EPUB 檔案到同目錄

#### 批次模式
1. 遞迴搜尋目錄下所有 `.md` 檔案
2. 逐一執行單檔模式邏輯（含跳過與更新規則）
3. 每 20 個檔案回報進度
4. 結束時輸出統計摘要（新建/更新/跳過/失敗數量）

### 5. Exit Codes

- `0`：成功（轉換完成或全部跳過）
- `1`：有錯誤發生

## 注意事項

1. **編碼**：確保 Markdown 檔案為 UTF-8 編碼，避免亂碼
2. **智慧更新**：若 MD 檔案在 EPUB 產生後被修改，會自動重新產生 EPUB 取代舊檔；若未修改則跳過
3. **路徑**：必須使用絕對路徑傳入腳本
4. **書名**：自動從 Markdown 第一個 `#` 標題取得，若無則用檔名
5. **中文支援**：EPUB 內建的 CSS 已針對中文閱讀優化行距與字體大小
6. **Python 路徑**：使用直接 Python 路徑（`C:/Users/User/anaconda3/envs/tf_gpu_env/python.exe`）而非 `conda run`，避免中文輸出亂碼

## 常見問題與解決方案

### 問題：使用相對路徑執行腳本時失敗

**解決方案**：傳入絕對路徑。

❌ 錯誤用法：
```powershell
C:/Users/User/anaconda3/envs/tf_gpu_env/python.exe .github/skills/markdown-to-epub/convert_to_epub.py 考古題/刑法/114110_1301.md
```

✅ 正確用法：
```powershell
C:/Users/User/anaconda3/envs/tf_gpu_env/python.exe .github/skills/markdown-to-epub/convert_to_epub.py "D:/repo/LawExam/考古題/刑法/114110_1301.md"
```

### 問題：使用 conda run 時中文輸出亂碼或消失

**原因**：`conda run` 在 Windows PowerShell 中的輸出編碼與 UTF-8 不相容，導致中文字元變成亂碼或被吞掉。

**解決方案**：改用直接 Python 路徑執行。

❌ 不建議：
```powershell
C:/Users/User/anaconda3/Scripts/conda.exe run -n tf_gpu_env --no-capture-output python .github/skills/markdown-to-epub/convert_to_epub.py "D:/repo/LawExam/考古題/刑法/114110_1301.md"
```

✅ 建議：
```powershell
C:/Users/User/anaconda3/envs/tf_gpu_env/python.exe .github/skills/markdown-to-epub/convert_to_epub.py "D:/repo/LawExam/考古題/刑法/114110_1301.md"
```

````
