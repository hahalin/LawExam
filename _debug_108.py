# -*- coding: utf-8 -*-
import pdfplumber

with pdfplumber.open('考古題/綜合法學(2)公司/108120_0202_綜合法學(二)(公司.pdf') as pdf:
    page = pdf.pages[0]
    chars = page.chars
    target_chars = [c for c in chars if c['text'] == '\u2460' or ord(c['text'][0]) > 0xE000]
    print(f'Found {len(target_chars)} target chars')
    for c in target_chars[:20]:
        print(f"  text=U+{ord(c['text']):04X} ({c['text']}) fontname={c['fontname']} x={c['x0']:.1f} y={c['top']:.1f}")
    print()
    fonts = set(c['fontname'] for c in chars)
    print('Fonts used:', fonts)
