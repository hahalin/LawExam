# -*- coding: utf-8 -*-
r"""
字幕 HTML 轉 Markdown 腳本

用法：
    python convert_subtitle.py <html_path>
    
範例：
    python convert_subtitle.py 刑法/06.html
    python convert_subtitle.py D:/repo/LawExam/刑法/06.html
"""
import sys
from pathlib import Path
from bs4 import BeautifulSoup
import re

def convert_subtitle(html_path: Path) -> bool:
    """將 HTML 字幕檔轉換為 Markdown"""
    md_path = html_path.with_suffix('.md')
    
    # 檢查是否已存在
    if md_path.exists():
        print(f'已存在，跳過：{md_path}')
        return False
    
    # 時間格式
    TIME_PATTERN = re.compile(r"^\d{2}:\d{2}:\d{2} - \d{2}:\d{2}:\d{2}$")
    
    # 讀取 HTML
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    # 課程名稱：資料夾名稱 + 檔案名稱
    folder_name = html_path.parent.name
    file_stem = html_path.stem
    course_name = f"{folder_name}{file_stem}"
    
    # 提取字幕
    subtitles = []
    
    # 方法1：從 div.css-10s8ss9 提取
    for div in soup.find_all('div', class_='css-10s8ss9'):
        ps = div.find_all('p')
        if not ps:
            continue
        time_tag = None
        text_tag = None
        for p in ps:
            text = p.get_text(strip=True)
            if not text:
                continue
            if TIME_PATTERN.match(text):
                time_tag = p
            elif text_tag is None:
                text_tag = p
        if time_tag and text_tag:
            time_text = time_tag.get_text(strip=True)
            subtitle_text = text_tag.get_text(strip=True)
            subtitles.append(f"{time_text}  \n{subtitle_text}\n")
    
    # 方法2（備用）：從連續 p 標籤提取
    if not subtitles:
        ps = soup.find_all('p')
        i = 0
        while i < len(ps):
            time_text = ps[i].get_text(strip=True)
            if TIME_PATTERN.match(time_text):
                j = i + 1
                while j < len(ps):
                    subtitle_text = ps[j].get_text(strip=True)
                    if subtitle_text and not TIME_PATTERN.match(subtitle_text):
                        subtitles.append(f"{time_text}  \n{subtitle_text}\n")
                        i = j
                        break
                    j += 1
            i += 1
    
    if not subtitles:
        print(f'無法提取字幕：{html_path}')
        return False
    
    # 產生 Markdown
    md_content = f"# 課程名稱：{course_name}\n\n"
    md_content += "\n".join(subtitles)
    
    # 寫入檔案
    md_path.write_text(md_content, encoding='utf-8')
    print(f'已轉換：{html_path} → {md_path}')
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python convert_subtitle.py <html_path>")
        print("範例：python convert_subtitle.py 刑法/06.html")
        sys.exit(1)
    
    html_arg = sys.argv[1]
    html_path = Path(html_arg)
    
    # 相對路徑以目前工作目錄（專案根目錄）為基準
    html_path = html_path.resolve()
    
    if not html_path.exists():
        print(f'檔案不存在：{html_path}')
        sys.exit(1)
    
    convert_subtitle(html_path)
