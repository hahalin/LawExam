---
name: html-subtitle-to-markdown
description: 從補習班課程網頁抓字幕並轉成 Markdown 字幕檔，再接著整理筆記。觸發：「抓{科目}第N堂字幕」「從第N堂開始逐課抓」、給課程網址，或使用者說已把某堂課的 HTML 存進 課程字幕/ 資料夾。
---

# 字幕：抓取 → 轉 md → 接筆記

一堂課走三步：① 用 Chrome 抓該堂字幕 ② 跳下一堂 ③ 字幕轉筆記。多堂時一堂一堂循序做（前一堂寫回才開下一堂）。

## 需要的東西

- 電腦上的 Chrome 開著、Claude 擴充功能已連線、補習班網站已登入。
- Claude 可存取 `D:\repo\LawExam` 與「下載」資料夾（`~/Downloads`）。「下載」沒接上時，請 Frank 在 Claude 桌面 app 按「Add folder」加入。

## ① 抓字幕（金榜函授 easylearn2.aivod.com.tw，2026/11/17 起）

1. Claude in Chrome 開新分頁到課程頁（例：江赫公司法 `https://easylearn2.aivod.com.tw/courses/2/115E608744CIL`）。右側清單是各堂（`公司法B 江赫 第09堂`），切課不換網址。
2. `javascript_tool` 貼上 `scripts/grab_subtitles_aivod.js` 全文，定義 `window.__lessons`、`window.__grab`。
3. `JSON.stringify(window.__lessons())` 看堂數與各堂進度。
4. 一堂一呼叫：`JSON.stringify(await window.__grab(9, '公司法-江赫'))`。它會點該堂、開「字幕小幫手」分頁、等字幕清單穩定、暫停影片，下載 `公司法-江赫09.html`。
5. 回傳的句數（一堂約 3500 句）與最後時間要對得上該堂分鐘數；`err` 就重抓那一堂。

新站字幕結構：`.subtitle-list > .subtitle-item > .time-code`（`0:00:29`，只有起始時間）＋`.text`。腳本輸出沿用舊格式 `<div class="css-10s8ss9"><p>HH:MM:SS - HH:MM:SS</p><p>字幕</p></div>`，結束時間取下一句起始時間，所以 `convert_subtitle.py` 不用改。網站再改版時，先在頁面查新的 class 名稱，改腳本的選擇器。

注意：
- 點進某堂，影片會從上次看到的位置開始，腳本每 0.5 秒暫停一次，觀看進度不變（09 實測 58% → 58%）。開課程頁時清單上的進度偶爾暫時顯示 0%，重新整理或切課後會恢復，不是被改掉。
- 只想驗證切課、不下載：`__grab(10, '公司法-江赫', {dl: false})`。
- 字幕內容不經過對話傳（一堂約 7 萬字），一律走下載檔。
- 舊站（志光 ai.highstudy.com.tw）用 `scripts/grab_subtitles.js`，做法見 git 歷史。

## ② 跳下一堂

下一堂＝下一次呼叫 `__grab(N+1, …)`，中間隔幾秒，不要一次呼叫連抓多堂。Chrome 第二個下載起可能被擋：請 Frank 點網址列右邊的下載圖示，選「一律允許 easylearn2.aivod.com.tw 自動下載多個檔案」；被擋期間排隊的檔可能變成「(1)」「(2)」重複檔，以檔案大小與檔內註解的課名挑對的。

## 轉 md 並寫回

1. `device_stage_files` 從「下載」取 `{科目}{NN}.html`，確認檔內註解的課名對得上（`grep "第NN堂"`）。
2. 在雲端放成 `{科目資料夾}/{檔名}.html`，跑 `python3 convert_subtitle.py {科目資料夾}/{檔名}.html`（md 第一行會是「課程名稱：{資料夾}{檔名}」）。
3. 回報句數；看開頭、結尾幾句像完整一堂。
4. `device_commit_files` 把 html 與 md 都寫進 `課程字幕/{科目資料夾}/`（html 在 .gitignore，只留本機）。
5. 「下載」裡的殘檔 Claude 刪不掉，提醒 Frank 自行清。

對應的 `.md` 已存在 → 不處理、不覆蓋，告知 Frank。

## 資料夾與檔名

| 課程 | 資料夾 | 檔名 |
|---|---|---|
| 公司法（江赫，金榜函授） | `課程字幕/公司法-江赫/` | `09.html`、`09.md`、`09-筆記-01-主題.md`、`09-ELI5.html`；筆記大標題 `# 公司法江赫09 筆記：主題`，ELI5 data-lesson＝`公司法江赫09` |
| 公司法（董謙） | `課程字幕/公司法/` | `公司法NN…`（既有，不動） |

下載檔名用 `__grab` 第二個參數＋兩位數堂號（`公司法-江赫09.html`），寫回 repo 時改成上表的檔名。網站目錄會顯示「公司法-江赫」科目、「公司法-江赫09」課堂。

## ③ 轉筆記

寫回後接 `subtitle-note-organizer`：壓縮字幕（去時間戳、每 25 句留一個時間標記）分批讀 → 列主題清單直接開寫 → 主題筆記一次一份（寫完、寫回、回報一行）→ ELI5 → 跑 `python3 scripts/build_readme.py`。

## 環境

- 雲端是 Linux，用 `python3`；需要 `beautifulsoup4`（缺少時 `pip install beautifulsoup4 --break-system-packages`）。
- 雲端連線不能寫 `.claude/`：改這份 SKILL.md 時放 `scripts/_pending/html-subtitle-to-markdown.SKILL.md`，Frank 手動搬。
