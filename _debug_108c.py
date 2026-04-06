# -*- coding: utf-8 -*-
"""Check the actual chars at the Q1 options line (y~296)"""
import pdfplumber

with pdfplumber.open('考古題/綜合法學(2)公司/108120_0202_綜合法學(二)(公司.pdf') as pdf:
    page = pdf.pages[0]
    chars = page.chars
    
    # Options line is at y=296.4 based on EUDC positions
    q1_opts = [c for c in chars if 290 < c['top'] < 310]
    print('=== Q1 options line (y~296) ===')
    for c in q1_opts:
        print(f"  U+{ord(c['text']):04X} ({c['text']}) font={c['fontname']} x={c['x0']:.1f} y={c['top']:.1f}")
