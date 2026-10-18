"""
憲法考古題主題熱力圖
統計 考古題/憲法/主題整理_*.md 各主題在各年度的出題次數
橫軸：年度  縱軸：主題
"""

import re
import os
from pathlib import Path
from collections import defaultdict

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# ── 資料收集 ──────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent / "考古題" / "憲法"

TOPIC_DISPLAY = {
    "基本國策與國家基本原則": "基本國策",
    "基本權總論與法治國原則": "基本權總論",
    "人格權隱私權與遷徙自由": "人格權隱私遷徙",
    "人身自由與生命權":       "人身自由生命權",
    "言論自由與宗教學術自由": "言論宗教自由",
    "財產權職業自由與結社自由": "財產職業結社",
    "平等權":                 "平等權",
    "訴訟權與受益權":         "訴訟受益權",
    "總統與行政院":           "總統行政院",
    "立法院":                 "立法院",
    "司法院與考試院":         "司法考試院",
    "監察院":                 "監察院",
    "地方自治":               "地方自治",
    "憲法訴訟":               "憲法訴訟",
}

# 年份正規表示式：匹配「（108年第3題）」或「（107年第14題，原第14題）」
YEAR_PATTERN = re.compile(r"（(\d{3})年第\d+題")

data = defaultdict(lambda: defaultdict(int))  # data[topic][year] = count

for md_file in sorted(BASE_DIR.glob("主題整理_*.md")):
    raw_topic = md_file.stem.replace("主題整理_", "")
    topic = TOPIC_DISPLAY.get(raw_topic, raw_topic)

    text = md_file.read_text(encoding="utf-8")
    for year_str in YEAR_PATTERN.findall(text):
        year = int(year_str)
        data[topic][year] += 1

# ── 建立矩陣 ──────────────────────────────────────────────
all_years = sorted({y for counts in data.values() for y in counts})
topics    = sorted(data.keys(), key=lambda t: sum(data[t].values()), reverse=True)

matrix = np.zeros((len(topics), len(all_years)), dtype=int)
for i, topic in enumerate(topics):
    for j, year in enumerate(all_years):
        matrix[i, j] = data[topic][year]

# ── 字型設定（Windows 上使用微軟正黑體）────────────────────
def find_chinese_font() -> str | None:
    candidates = [
        "Microsoft JhengHei",   # 微軟正黑體
        "Microsoft YaHei",      # 微軟雅黑
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

im = ax.imshow(matrix, cmap="BuPu", aspect="auto", vmin=0)

# 軸刻度
ax.set_xticks(range(len(all_years)))
#ax.set_xticklabels([f"{y}" for y in all_years], fontsize=13, rotation=30, ha="right")
ax.set_xticklabels([f"{y}" for y in all_years], fontsize=15, rotation=0, ha="right")
ax.set_yticks(range(len(topics)))
ax.set_yticklabels(topics, fontsize=16)

# 格子內顯示數字
for i in range(len(topics)):
    for j in range(len(all_years)):
        val = matrix[i, j]
        if val > 0:
            text_color = "white" if val >= matrix.max() * 0.55 else "#1a1a2e"
            ax.text(j, i, str(val), ha="center", va="center", fontsize=16, color=text_color, fontweight="bold")

# 色條
cbar = fig.colorbar(im, ax=ax, shrink=0.8)
#cbar.set_label("出題次數", fontsize=13)
cbar.ax.tick_params(labelsize=12)

ax.set_title("憲法考古題主題熱力圖（各年度出題次數）", fontsize=18, fontweight="bold", pad=18)
#ax.set_xlabel("年度", fontsize=15)
#ax.set_ylabel("主題", fontsize=15)

plt.tight_layout()

out_path = Path(__file__).parent.parent / "憲法考古題熱力圖.png"
plt.savefig(out_path, dpi=150, bbox_inches="tight")
plt.close()
print(f"✅ 熱力圖已儲存：{out_path}")
