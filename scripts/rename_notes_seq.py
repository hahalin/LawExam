#!/usr/bin/env python3
"""
把主題筆記檔名加上講課順序序號：
    民法NN-筆記-{主題}.md  →  民法NN-筆記-{序號}-{主題}.md
並把 repo 內所有 .md / .html 裡出現的舊檔名換成新檔名（ELI5 頁底部的對應檔名、審核表等）。

用法（在 repo 根目錄）：
    python3 scripts/rename_notes_seq.py           # 實際改名
    python3 scripts/rename_notes_seq.py --dry-run # 只列出會做什麼

可重複執行：已經改過的會跳過。
"""
import os, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
NOTES_DIR = ROOT / "課程字幕" / "民法"
DRY = "--dry-run" in sys.argv

# 依字幕時間順序排列；新的一堂課做完筆記後，把該堂加進來再跑一次即可。
ORDER = {
    "民法01": [
        "民法體系鳥瞰與法源",
        "請求權基礎思考流程",
        "法律解釋與§4§5數量記載",
        "權利能力與權利的概念",
        "胎兒§7與視為推定",
        "死亡宣告§8§9",
        "撤銷死亡宣告與家事法§163",
        "法律行為概念與各種能力",
    ],
    "民法02": [
        "監護宣告§14§15",
        "輔助宣告§15-1§15-2與監護宣告比較",
        "成年年齡修法與民總施行法§3-1",
        "§16§17不得拋棄與人格權§18不法性",
        "人格權損害賠償§184§195與不當得利",
        "姓名權§19體系定位",
        "生命權侵害與間接被害人§192§194",
        "身分權§195III與類推§18",
        "住所§20-§24",
        "法人成立消滅與社團財團",
        "法人權利能力§26慰撫金與目的限制§64",
        "法人董事§27代表權",
    ],
    "民法03": [   # 寫檔時已帶序號，列在這裡只是備查
        "無權代表§27III與§31",
        "代表與代理的區別",
        "法人侵權責任體系與§184肯定說",
        "§28要件與連帶§273",
        "社團總會決議方法§52§53§57與出席數爭議",
        "總會決議瑕疵§56撤銷與無效",
        "財團法人捐助撤回與§64宣告無效",
        "權利客體與物的四要件",
        "定著物四要件與魚池",
        "輕便軌道封頂電線桿",
        "構成部分一物一權與一樹二賣",
        "動產§67與動物寵物慰撫金",
    ],
    "民法12": [
        "消滅時效客體",            # 00:00
        "§767與消滅時效",          # 00:03
        "考試論述技巧",            # 00:11
        "釋字771與繼承回復請求權", # 00:22
        "浮覆地與大法庭裁定",      # 00:31
        "消滅時效期間",            # 00:49
        "§127短期時效",            # 01:08
        "消滅時效起算點",          # 01:24
        "消滅時效中斷",            # 01:46
    ],
}

def main():
    mapping = {}  # 舊檔名 → 新檔名
    for lesson, topics in ORDER.items():
        for i, t in enumerate(topics, 1):
            old = f"{lesson}-筆記-{t}.md"
            new = f"{lesson}-筆記-{i:02d}-{t}.md"
            mapping[old] = new

    # 1. 改名
    renamed = 0
    for old, new in mapping.items():
        src, dst = NOTES_DIR / old, NOTES_DIR / new
        if dst.exists():
            continue
        if not src.exists():
            print(f"[略過] 找不到 {old}")
            continue
        print(f"[改名] {old}\n    → {new}")
        if not DRY:
            src.rename(dst)
        renamed += 1

    # 2. 更新引用（全 repo 的 .md / .html，跳過 .git 與 .github）
    patched = 0
    for p in ROOT.rglob("*"):
        if p.suffix.lower() not in (".md", ".html"):
            continue
        if any(part in (".git", ".github", "node_modules") for part in p.parts):
            continue
        try:
            s = p.read_text(encoding="utf-8")
        except Exception:
            continue
        t = s
        for old, new in mapping.items():
            if old in t:
                t = t.replace(old, new)
        if t != s:
            print(f"[更新引用] {p.relative_to(ROOT)}")
            if not DRY:
                p.write_text(t, encoding="utf-8")
            patched += 1

    # 3. 套用待更新的 skill 檔（Claude 從雲端不能直接寫 .claude/，先放 scripts/_pending/）
    pending = ROOT / "scripts" / "_pending"
    if pending.is_dir():
        for f in sorted(pending.glob("*.SKILL.md")):
            skill = f.name[: -len(".SKILL.md")]
            dst = ROOT / ".claude" / "skills" / skill / "SKILL.md"
            print(f"[更新 skill] {dst.relative_to(ROOT)}  ← {f.relative_to(ROOT)}")
            if not DRY:
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
                f.unlink()
        if not DRY and not any(pending.iterdir()):
            pending.rmdir()

    print(f"\n完成：改名 {renamed} 個檔案，更新 {patched} 個檔案的引用{'（dry-run，未實際寫入）' if DRY else ''}。")

if __name__ == "__main__":
    main()
