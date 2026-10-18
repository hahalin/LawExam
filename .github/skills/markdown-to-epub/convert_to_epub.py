#!/usr/bin/env python3
"""
Markdown to EPUB converter for LawExam project.

Usage:
    Single file:
        python convert_to_epub.py <md_file_path>

    Batch (directory):
        python convert_to_epub.py <directory_path>
        Recursively converts all .md files in the directory.

The EPUB file will be created in the same directory as the input file,
with the same name but .epub extension.

Exit codes (single file mode):
    0 - Success (converted or skipped)
    1 - Error
"""

import sys
import os
import re
import glob

from ebooklib import epub
import markdown


def extract_title(md_content: str, fallback_name: str) -> str:
    """Extract the first # heading from markdown content as the book title."""
    match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return fallback_name


def convert_single(md_path: str) -> str:
    """Convert a single Markdown file to EPUB.

    Returns:
        'created' - New EPUB created
        'updated' - Existing EPUB replaced (MD was newer)
        'skipped' - EPUB already up-to-date
        'error'   - Conversion failed
    """
    md_path = os.path.abspath(md_path)

    if not os.path.exists(md_path):
        print(f"錯誤：找不到檔案 {md_path}")
        return 'error'

    epub_path = os.path.splitext(md_path)[0] + '.epub'
    is_update = False

    if os.path.exists(epub_path):
        md_mtime = os.path.getmtime(md_path)
        epub_mtime = os.path.getmtime(epub_path)
        if md_mtime <= epub_mtime:
            return 'skipped'
        is_update = True

    try:
        _generate_epub(md_path, epub_path)
    except Exception as e:
        print(f"錯誤：轉換失敗 {md_path} - {e}")
        return 'error'

    return 'updated' if is_update else 'created'


def _generate_epub(md_path: str, epub_path: str) -> None:
    """Generate EPUB file from Markdown."""
    # Read markdown content
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Extract title
    file_basename = os.path.splitext(os.path.basename(md_path))[0]
    title = extract_title(md_content, file_basename)

    # Convert markdown to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'codehilite', 'toc'],
        output_format='html5'
    )

    # Create EPUB book
    book = epub.EpubBook()

    # Set metadata
    book.set_identifier(f'lawexam-{file_basename}')
    book.set_title(title)
    book.set_language('zh-TW')
    book.add_author('LawExam')

    # CSS style optimized for Chinese reading
    css_content = '''
body {
    font-family: "Noto Sans CJK TC", "Microsoft JhengHei", "PingFang TC", sans-serif;
    line-height: 1.8;
    font-size: 1em;
    color: #333;
    padding: 0 1em;
}

h1 {
    font-size: 1.5em;
    border-bottom: 2px solid #333;
    padding-bottom: 0.3em;
    margin-top: 1em;
}

h2 {
    font-size: 1.2em;
    margin-top: 1.5em;
    border-bottom: 1px solid #ccc;
    padding-bottom: 0.2em;
}

h3 {
    font-size: 1.1em;
    margin-top: 1em;
}

blockquote {
    border-left: 3px solid #666;
    padding-left: 1em;
    margin-left: 0;
    color: #555;
    font-size: 0.95em;
}

hr {
    border: none;
    border-top: 1px solid #ccc;
    margin: 1.5em 0;
}

p {
    margin: 0.5em 0;
    text-align: justify;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}

th, td {
    border: 1px solid #ccc;
    padding: 0.5em;
    text-align: left;
}

th {
    background-color: #f5f5f5;
    font-weight: bold;
}

code {
    background-color: #f5f5f5;
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-size: 0.9em;
}

pre {
    background-color: #f5f5f5;
    padding: 1em;
    border-radius: 5px;
    overflow-x: auto;
}

pre code {
    background-color: transparent;
    padding: 0;
}
'''

    style = epub.EpubItem(
        uid='style',
        file_name='style/default.css',
        media_type='text/css',
        content=css_content.encode('utf-8')
    )
    book.add_item(style)

    # Create chapter
    chapter = epub.EpubHtml(
        title=title,
        file_name='content.xhtml',
        lang='zh-TW'
    )
    chapter.content = f'<html><head><meta charset="utf-8"/></head><body>{html_content}</body></html>'
    chapter.add_item(style)
    book.add_item(chapter)

    # Table of contents and spine
    book.toc = [chapter]
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ['nav', chapter]

    # Write EPUB
    epub.write_epub(epub_path, book, {})


def convert_batch(dir_path: str) -> None:
    """Recursively convert all .md files in a directory to EPUB."""
    dir_path = os.path.abspath(dir_path)

    if not os.path.isdir(dir_path):
        print(f"錯誤：找不到目錄 {dir_path}")
        sys.exit(1)

    md_files = sorted(glob.glob(os.path.join(dir_path, '**', '*.md'), recursive=True))
    total = len(md_files)

    if total == 0:
        print(f"目錄中無 .md 檔案：{dir_path}")
        sys.exit(0)

    stats = {'created': 0, 'updated': 0, 'skipped': 0, 'error': 0}

    for i, md_file in enumerate(md_files, 1):
        result = convert_single(md_file)
        stats[result] += 1
        if i % 20 == 0:
            print(f"進度: {i}/{total}")

    print(f"\n=== 轉換完成 ===")
    print(f"總計: {total} 個 MD 檔案")
    print(f"新建: {stats['created']}")
    print(f"更新: {stats['updated']}")
    print(f"跳過: {stats['skipped']}")
    print(f"失敗: {stats['error']}")

    if stats['error'] > 0:
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("用法：python convert_to_epub.py <markdown_file_or_directory>")
        sys.exit(1)

    target = sys.argv[1]

    if os.path.isdir(target):
        convert_batch(target)
    else:
        result = convert_single(target)
        if result == 'created':
            epub_path = os.path.splitext(os.path.abspath(target))[0] + '.epub'
            print(f"完成：{epub_path}")
        elif result == 'updated':
            epub_path = os.path.splitext(os.path.abspath(target))[0] + '.epub'
            print(f"更新：{epub_path}")
        elif result == 'skipped':
            epub_path = os.path.splitext(os.path.abspath(target))[0] + '.epub'
            print(f"跳過：{epub_path} 已存在且為最新")
        else:
            sys.exit(1)
