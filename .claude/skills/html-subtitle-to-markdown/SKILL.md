---
name: html-subtitle-to-markdown
description: 將補習班課程網頁複製下來的字幕 HTML 轉成 Markdown 字幕檔。觸發方式：「{路徑}.html 轉換為字幕檔」、「轉第 16 堂字幕」，或使用者說已把某堂課的 HTML 存進 課程字幕/ 資料夾。
---

# 字幕 HTML 轉 Markdown

## 流程

1. 使用者把網頁字幕區塊存成 `課程字幕/{科目}/{科目}{編號}.html`（例：`課程字幕/民法/民法16.html`）。
   - 一堂課 HTML 約 1～2 MB，**不要**貼進對話，一律存檔。
2. 執行腳本（在專案根目錄）：
   ```bash
   python3 .claude/skills/html-subtitle-to-markdown/convert_subtitle.py "課程字幕/民法/民法16.html"
   ```
   - 傳**專案根目錄起算的相對路徑或絕對路徑**皆可；腳本會自行處理。
3. 輸出 `課程字幕/民法/民法16.md`，格式：
   ```markdown
   # 課程名稱：民法民法16

   HH:MM:SS - HH:MM:SS  
   字幕內容
   ```
4. 回報行數，並確認開頭／結尾幾句是否像完整一堂課（網頁有時只載入部分字幕）。

## 跳過規則（必須遵守）

- 對應的 `.md` 已存在 → **不處理、不覆蓋**，告知使用者。

## 腳本認得的 HTML 結構

```html
<div class="css-10s8ss9">
  <p>00:00:00 - 00:01:23</p>
  <p>字幕內容</p>
</div>
```
備用：連續的 `<p>時間</p><p>內容</p>`。若兩種都抓不到（補習班改版），讀 HTML 前 200 行找新的 class 名稱，修改腳本的選擇器，不要手動轉。

## 環境

- Claude 的執行環境是 Linux，用 `python3`；需要 `beautifulsoup4`（已安裝；缺少時 `pip install beautifulsoup4`）。

## 轉完之後

接著用 `subtitle-note-organizer` 做筆記。字幕檔 7000～8000 行，整理時分批讀（每批約 500～800 行）。
