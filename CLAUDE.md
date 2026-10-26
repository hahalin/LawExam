# LawExam — 2027（116 年）司律考試準備

使用者：Frank。目標：通過一試與二試（律師錄取分數）。

## 溝通
- 一律繁體中文、台灣用語、台灣法律術語。
- 一次給一個可執行的下一步，不列長清單；收尾用「下一步是 X」，不用問句。
- 已定案的事直接做並回報結果，不回頭確認。真正要他決定的點才問，一次一個。
- 講事情就講事情，不評價他這個人。
- 解說新概念：先給一組可以自己動手算／代入的具體數字或情境，再講規則。

## 資料夾
```
課程字幕/{科目}/{科目}{編號}.html   ← 使用者從補習班網頁存下來的字幕 HTML（1~2MB，不貼對話）
課程字幕/{科目}/{科目}{編號}.md     ← 轉出的字幕檔（7000~8000 行）
課程字幕/{科目}/{科目}{編號}-筆記-{序號}-{主題}.md   ← 主題筆記，一主題一檔；序號兩位數、依講課順序
課程字幕/{科目}/{科目}{編號}-ELI5.html        ← ELI5，一堂一檔（HTML），卡片與主題筆記一對一
課程字幕/_eli5/style.css, app.js           ← ELI5 共用樣式與腳本，外觀改這裡
考古題/{科目}/                      ← 考古題 md 與主題整理
條號地圖/{科目}/                    ← 條號地圖
```
民法字幕 01~41（41 網站名「41完」統一為 `民法41`）與補充課 `民法物權補充1/2`、`民法債權補充1/2` 已轉出；民法01～37、39 筆記＋ELI5 完成（2026/10/25），民法38 只完成筆記-01～06（字幕到 01:31），民法40 只完成筆記-01～06（字幕到 00:59），兩講都缺後段筆記與 ELI5（製作時兩度遭內容過濾中斷，需分小段補）；民法41 筆記 01～12＋ELI5 完成（2026/10/26，講到動產質權與營業質，財產法課程結束）；四堂補充課尚未整理。民法二試總複習（財產法）01～03 筆記＋ELI5 完成，檔名 `二試NN.md`、`二試NN-筆記-NN-主題.md`、`二試NN-ELI5.html`（不加「民法」前綴；網站與 README 顯示為「民法二試NN」；ELI5 data-lesson＝民法二試NN；二試筆記以「🎯 二試爭點提示」取代一試表）。強制執行法04、05 筆記＋ELI5 已完成。**強制執行法科目檔名不加科目前綴**（Frank 10/11 決定）：`NN.html`、`NN.md`、`NN-筆記-01-主題.md`、`NN-ELI5.html`（ELI5 內 data-lesson、標題仍寫「強制執行法NN」）；民法維持 `民法NN-…`。憲法（陸伯言，17 講）字幕 01～17 已轉出（檔名 `憲法NN…`），憲法01～17 筆記＋ELI5 全部完成。公司法（董謙，20 講）字幕 01～20 已轉出（檔名 `公司法NN…`，網站「20完」統一為 `公司法20`），公司法01～20 筆記＋ELI5 全部完成（2026/10/25）。檔名含前綴控制在 65 個中文字以內（雲端寫檔有 255 bytes 限制）。
筆記檔名序號：**建檔時就直接帶序號**（列完主題清單即定序，01 起兩位數），ELI5 卡片底部寫同一個檔名。`scripts/rename_notes_seq.py` 只是補救舊檔用，正常流程不跑。

## Skills（.claude/skills/）
| 要做的事 | skill |
|---|---|
| 字幕 HTML → md | `html-subtitle-to-markdown` |
| 字幕 md → 主題筆記 + ELI5 頁 | `subtitle-note-organizer` |
| 某主題的條號地圖 | `condition-map` |
| 考古題依主題整理 | `topic-note-organizer` |
| 考古題 PDF → md | `exam-pdf-to-markdown` |

`.github/` 下是舊的 Copilot 版本，保留不動、不要再編輯；以 `.claude/` 為準。
epub / pdf 轉換目前不需要，不要主動提。

## 一堂課的標準流程
0. 字幕 HTML 可由 Claude 用 Chrome 直接到志光網站抓（跳過測驗、一講一個下載檔），做法與踩過的坑見 `html-subtitle-to-markdown` skill「取得字幕 HTML」段、腳本 `scripts/grab_subtitles.js`。
1. 使用者說「民法16 html 已存」→ 跑轉換腳本，回報行數。
2. 分批讀字幕（每批 500~800 行），列主題清單後直接開寫，不等回覆。
3. 逐一寫主題筆記，每份完成回報一行。
4. 寫 ELI5 頁（HTML），用無頭瀏覽器截圖檢查流程框、時間軸沒有重疊。ELI5 句子白話，但法律概念用正式用語（除去侵害、效力未定、情節重大…），標題不用要轉一下才懂的比喻——Frank 要藉此適應二試讀寫的法律用語。
5. 回報檔案清單。下一步固定是「下一堂」或「補 13~15 的筆記」。
6. **一次多堂時，一堂一堂循序做**（Frank 10/23：不求快）：前一堂筆記＋ELI5 完成、檢查、寫回後，才開下一堂；不要多堂平行分派同時做。

## 字幕缺漏補錄（錄音辨識）
志光影片是 BlendVision DASH＋Widevine/PlayReady 加密：不下載、不解密；Windows 即時輔助字幕也收不到這段聲音（2026/10/19 實測）。可行做法是錄電腦播出的聲音：
1. 先看字幕檔判斷：時間戳連續但內容斷句，或一條字幕撐很久字卻很少 → 才需要錄。字幕時間戳可能比影片實際時間晚到約 1 分鐘，播放起點往前多抓。
2. 請 Frank 雙擊 `scripts\record_clip.bat`（Claude 只有檔案總管點選權，不能自己執行）。它錄 110 秒 WASAPI loopback → `_rec\clip.wav`，狀態寫在 `_rec\status.txt`（INSTALLING → RECORDING → DONE）。
3. 看到 RECORDING 後，用 Claude in Chrome 在課程頁（`ai.highstudy.com.tw` playlist，點「115律師-民法A(袁翟)-NN」）以 JS 設 `video.currentTime`、取消靜音、`play()`。loopback 只在有聲音時寫入，wav 起點＝開始播放的位置。
4. stage `clip.wav` 到雲端，ffmpeg 轉 16k 單聲道，用 sherpa-onnx `paraformer-zh-small-2024-03-09`（GitHub releases 下載；Hugging Face 被擋）分 8 秒辨識，轉繁體、改明顯錯字。
5. 補進字幕 md 缺口處，開頭標「【以下為錄音辨識補錄，原字幕缺漏；錯字已人工校正】」；筆記來源註記改成「已以錄音辨識補入」。commit、push 後請 Frank 刪 `_rec\`（已在 .gitignore）。

## 硬規則
- 任何既有 `.md` 不覆蓋；要更新就在原檔上改。
- 法條原文不確定就標「→ 建議查閱最新六法原文」，不捏造。
- 寫給別人看的文件，每一行都要跟主張有關；無關的佐證不放。

## 環境
- 執行環境是 Linux（透過 Claude 掛載 D:\repo\LawExam），用 `python3`，已有 beautifulsoup4。
- mermaid 圖請依 `.github/instructions/mermaid.instructions.md`。

## 網站（GitHub Pages：https://hahalin.github.io/LawExam/）
- `index.html`（左科目、上課堂活頁）與 `toc.json` 由 `python scripts/build_index.py` 產生（掃描 `課程字幕/` 全部科目，規則在 `scripts/toc_lib.py`；新科目資料夾自動出現，排序在 ORDER）；README「課程字幕與筆記」段由 `python scripts/build_readme.py` 產生。**每做完一堂（或改了筆記檔名）兩支都要重跑**。
- 字幕與分主題筆記一律維持 md，網站用 `note.html?f=路徑` 即時排版（marked.js），不另做筆記 html。
- 目錄與上一份／下一份顯示的筆記標題取自筆記第一行 `#` 大標題（去掉「民法NN 筆記：」前綴、「——」後摘要、結尾的（講義…）），檔名只當滑鼠提示；要改目錄上的名字就改大標題。
- `.github/workflows/pages.yml`：每次 push 到 master 自動重產 `index.html`、`toc.json` 並發佈 Pages（Settings → Pages → Source 須選 GitHub Actions）；不 commit 回 repo。README 仍需手動跑 `build_readme.py`。
- repo 根目錄 `.nojekyll` 不可刪（否則 `_eli5/` 不會發佈）。
- PDF 與字幕原始 html（ELI5 除外）在 `.gitignore`：只留本機，不進 git、不上網站。2026/10/18 已清掉舊歷史，從單一 commit 重新開始。
