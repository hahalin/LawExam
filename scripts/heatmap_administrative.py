"""
行政法考古題主題熱力圖
統計 考古題/行政法/主題整理_*.md 各主題在各年度的出題次數
橫軸：年度  縱軸：主題

注意：僅統計題目「標題行」（### N、YYY年第X題），
避免誤抓內文交叉引用。
"""

import re
from pathlib import Path
from collections import defaultdict

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# ── 資料收集 ──────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent / "考古題" / "行政法"

TOPIC_DISPLAY = {
    "訴願":               "訴願",
    "行政訴訟":           "行政訴訟",
    "行政處分":           "行政處分",
    "行政罰":             "行政罰",
    "行政組織與管轄":     "行政組織與管轄",
    "行政程序與資訊公開": "行政程序與資訊公開",
    "行政法源與行政命令": "行政法源與命令",
    "行政法基礎與公物法": "行政法基礎與公物法",
    "行政法原則與裁量":   "行政法原則與裁量",
    "行政契約":           "行政契約",
    "行政執行":           "行政執行",
    "地方自治":           "地方自治",
    "國家賠償與損失補償": "國賠與損失補償",
    "公務員法":           "公務員法",
}

# 標題行（### 或 ####）中含「NNN年 … 第N題」，容許數字/中文序號前綴與空格
# 例：#### 1【105年 第21題】 / ### 一、108年第17題 / ### 1、111 年 第 5 題
YEAR_PATTERN = re.compile(r"^#{2,4}.*?(\d{3})\s*年\s*第\s*\d+\s*題")

data = defaultdict(lambda: defaultdict(int))

for md_file in sorted(BASE_DIR.glob("主題整理_*.md")):
    raw_topic = md_file.stem.replace("主題整理_", "")
    topic = TOPIC_DISPLAY.get(raw_topic, raw_topic)

    for line in md_file.read_text(encoding="utf-8").splitlines():
        m = YEAR_PATTERN.match(line)
        if m:
            year = int(m.group(1))
            data[topic][year] += 1

if not data:
    raise SystemExit("⚠️  未抽到任何題目，請確認主題檔標題行格式與 YEAR_PATTERN 是否相符")

# 建立矩陣
all_years = sorted({y for counts in data.values() for y in counts})
topics    = sorted(data.keys(), key=lambda t: sum(data[t].values()), reverse=True)

matrix = np.zeros((len(topics), len(all_years)), dtype=int)
for i, topic in enumerate(topics):
    for j, year in enumerate(all_years):
        matrix[i, j] = data[topic][year]

# ── 字型設定 ──────────────────────────────────────────────
def find_chinese_font() -> str | None:
    candidates = [
        "Microsoft JhengHei",
        "Microsoft YaHei",
        "PingFang TC",
        "Noto Sans CJK TC",
        "SimHei",
    ]
    available = {f.name for f in fm.fontManager.ttflist}
    for name in candidates:
        if name in available:
            return name
    return None

font_name = find_chinese_font()
if font_name:
    plt.rcParams["font.family"] = font_name
else:
    print("⚠️  找不到中文字型，標籤可能顯示方塊，請安裝微軟正黑體")

plt.rcParams["axes.unicode_minus"] = False

# ── 繪圖 ──────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(max(14, len(all_years) * 1.2), max(9, len(topics) * 0.75)))

im = ax.imshow(matrix, cmap="OrRd", aspect="auto", vmin=0)

ax.set_xticks(range(len(all_years)))
ax.set_xticklabels([f"{y}" for y in all_years], fontsize=15, rotation=0, ha="right")
ax.set_yticks(range(len(topics)))
ax.set_yticklabels(topics, fontsize=16)

for i in range(len(topics)):
    for j in range(len(all_years)):
        val = matrix[i, j]
        if val > 0:
            text_color = "white" if val >= matrix.max() * 0.55 else "#1a1a2e"
            ax.text(j, i, str(val), ha="center", va="center", fontsize=16, color=text_color, fontweight="bold")

row_totals = matrix.sum(axis=1)
for i, total in enumerate(row_totals):
    ax.text(len(all_years) - 0.35, i, f"｜{total}", ha="left", va="center",
            fontsize=14, color="#7a0177", fontweight="bold")

cbar = fig.colorbar(im, ax=ax, shrink=0.8, pad=0.06)
cbar.ax.tick_params(labelsize=12)

total_q = int(matrix.sum())
ax.set_title(f"行政法考古題主題熱力圖（各年度出題次數，共 {total_q} 題）",
             fontsize=18, fontweight="bold", pad=18)

plt.tight_layout()

out_path = Path(__file__).parent.parent / "行政法考古題熱力圖.png"
plt.savefig(out_path, dpi=150, bbox_inches="tight")
plt.close()
print(f"✅ 熱力圖已儲存：{out_path}")
print(f"   年度範圍：{all_years[0]}～{all_years[-1]}　主題數：{len(topics)}　總題數：{total_q}")
