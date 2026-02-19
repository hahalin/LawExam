#!/usr/bin/env python3
"""
Markdown to EPUB converter for LawExam project.

Usage:
    python convert_to_epub.py <md_file_path>

The EPUB file will be created in the same directory as the input file,
with the same name but .epub extension.
"""

import sys
import os
import re

from ebooklib import epub
import markdown


def extract_title(md_content: str, fallback_name: str) -> str:
    """Extract the first # heading from markdown content as the book title."""
    match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return fallback_name


def create_epub(md_path: str) -> None:
    """Convert a Markdown file to EPUB."""
    md_path = os.path.abspath(md_path)

    if not os.path.exists(md_path):
        print(f"錯誤：找不到檔案 {md_path}")
        sys.exit(1)

    epub_path = os.path.splitext(md_path)[0] + '.epub'

    if os.path.exists(epub_path):
        print(f"跳過：{epub_path} 已存在")
        sys.exit(0)

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
    print(f"完成：{epub_path}")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("用法：python convert_to_epub.py <markdown_file>")
        sys.exit(1)

    create_epub(sys.argv[1])
