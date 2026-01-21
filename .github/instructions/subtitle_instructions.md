# 字幕整理指引

## 目標
本指引旨在協助將 HTML 檔案中的字幕內容提取並轉換為 Markdown 格式，方便用於教學準備，特別是針對司律一試的考試準備。

## 步驟
1. **準備 HTML 檔案**：
   - 將 HTML 檔案放置於對應的科目資料夾中，例如：`刑法/`、`憲法/`。
2. ** 使用get-conent 以utf-8 編碼讀取html檔。

3. **檢查 HTML 檔案內容**：
   - 確認 HTML 檔案中是否包含課程名稱。
   - 如果有課程名稱，提取並記錄下來。

4. **執行自動化腳本**：
   - 使用 `generate_subtitles.py` 腳本來處理 HTML 檔案。
   - 腳本會自動提取 `<p>` 標籤中的字幕內容，移除不必要的 HTML 標籤（如 `<strong>`），並生成對應的 Markdown 檔案。

5. **檢查輸出結果**：
   - 確認生成的 Markdown 檔案是否正確。
   - 在 Markdown 檔案開頭填寫課程名稱。

6. **應用於教學準備**：
   - 使用整理好的字幕內容進行教學準備，特別是針對今年的司律一試。

## 注意事項
- 確保 HTML 檔案的編碼為 UTF-8，避免出現亂碼。
- 如果 HTML 檔案過大，請分段處理，避免工具或編輯器卡頓。
- 如果課程名稱無法自動提取，請手動檢查並填寫。

## 腳本使用方式
1. 確保 Python 環境已安裝。
2. 將 `generate_subtitles.py` 放置於專案根目錄。
3. **找出可用的 Python 路徑（Windows）**：
   - 先用 PowerShell 執行：`Get-Command python`。
   - 若 `python` 失敗或版本不符，改用完整路徑，例如：`D:/Users/使用者/anaconda3/python.exe`。
   - 在 VS Code 工作區內，優先使用已設定的 Python 環境路徑執行。
4. 執行以下指令（擇一）：
   - 使用 `python`：
     ```
     python generate_subtitles.py
     ```
   - 使用完整路徑：
     ```
     D:/Users/使用者/anaconda3/python.exe generate_subtitles.py
     ```
5. 腳本會自動處理所有科目資料夾中的 HTML 檔案，並生成對應的 Markdown 檔案。

# 使用說明：字幕轉換自動化

## 功能
此功能會自動將指定資料夾中的 HTML 檔案轉換為 Markdown 格式的字幕檔案，並儲存到相同的資料夾中。

## 使用方式
1. 確保 `generate_subtitles.py` 腳本已正確配置，並放置於專案根目錄。
2. 在 VS Code 中，開啟命令面板（快捷鍵：`Ctrl+Shift+P`）。
3. 輸入 `@subtitle` 指令，並執行。
4. 腳本會自動處理所有 HTML 檔案，並跳過已存在對應 Markdown 檔案的 HTML。

### 跳過規則（必須遵守）
- 只要對應的 `.md` 已存在，就**不處理**該 `.html`。
- 例如：`刑法/05.html` 若已有 `刑法/05.md`，必須跳過，不可覆蓋。

## 注意事項
- 確保 HTML 檔案的格式正確，包含時間標籤和字幕內容。
- 腳本會自動跳過已存在的 Markdown 檔案，避免覆蓋。
- 如果需要重新生成 Markdown 檔案，請先刪除對應的 `.md` 檔案。