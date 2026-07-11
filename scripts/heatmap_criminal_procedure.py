"""
刑事訴訟法考古題主題熱力圖
統計 考古題/刑事訴訟法/主題整理_*.md 各主題在各年度的出題次數
橫軸：年度  縱軸：主題

注意：僅統計題目「標題行」（### N、YYY年第X題），
避免誤抓內文交叉引用（例如「與108年第11題同一考點」）。
"""

import re
from pathlib import Path
from collections import defaultdict

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# ── 資料收集 ──────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent / "考古題" / "刑事訴訟法"

# 主題顯示名稱（可視需要縮短）
TOPIC_DISPLAY = {
    "告訴與管轄":       "告訴與管轄",
    "偵查":             "偵查",
    "搜索與扣押":       "搜索與扣押",
    "羈押與具保":       "羈押與具保",
    "證據法則":         "證據法則",
    "辯護權與被告權利": "辯護權與被告權利",
    "審判程序":         "審判程序",
    "簡易程序與協商程序": "簡易協商程序",
    "自訴程序":         "自訴程序",
    "上訴與救濟":       "上訴與救濟",
    "沒收程序":         "沒收程序",
    "國民法官":         "國民法官",
}

# 標題行格式：「### 1、109年第3題（原第38題）」或「### 8、113年第35題」
YEAR_PATTERN = re.compile(r"^###\s+\d+、(\d{3})年第\d+題")

data = defaultdict(lambda: defaultdict(int))  # data[topic][year] = count

for md_file in sorted(BASE_DIR.glob("主題整理_*.md")):
    raw_topic = md_file.stem.replace("主題整理_", "")
    topic = TOPIC_DISPLAY.get(raw_topic, raw_topic)

    for line in md_file.read_text(encoding="utf-8").splitlines():
        m = YEAR_PATTERN.match(line)
        if m:
            year = int(m.group(1))
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

im = ax.imshow(matrix, cmap="OrRd", aspect="auto", vmin=0)

# 軸刻度
ax.set_xticks(range(len(all_years)))
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

# 各主題總計（右側）
row_totals = matrix.sum(axis=1)
for i, total in enumerate(row_totals):
    ax.text(len(all_years) - 0.35, i, f"｜{total}", ha="left", va="center",
            fontsize=14, color="#7a0177", fontweight="bold")

# 色條
cbar = fig.colorbar(im, ax=ax, shrink=0.8, pad=0.06)
cbar.ax.tick_params(labelsize=12)

total_q = int(matrix.sum())
ax.set_title(f"刑事訴訟法考古題主題熱力圖（各年度出題次數，共 {total_q} 題）",
             fontsize=18, fontweight="bold", pad=18)

plt.tight_layout()

out_path = Path(__file__).parent.parent / "刑事訴訟法考古題熱力圖.png"
plt.savefig(out_path, dpi=150, bbox_inches="tight")
plt.close()
print(f"✅ 熱力圖已儲存：{out_path}")
print(f"   年度範圍：{all_years[0]}～{all_years[-1]}　主題數：{len(topics)}　總題數：{total_q}")
