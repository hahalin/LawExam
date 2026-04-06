# -*- coding: utf-8 -*-
"""Check what chars the EUDC fonts produce for circled numbers in 108"""
import pdfplumber

with pdfplumber.open('考古題/綜合法學(2)公司/108120_0202_綜合法學(二)(公司.pdf') as pdf:
    page = pdf.pages[0]
    chars = page.chars
    
    # Find all EUDC font chars
    eudc_chars = [c for c in chars if 'EUDC' in c['fontname']]
    print(f'Found {len(eudc_chars)} EUDC chars on page 1')
    for c in eudc_chars[:30]:
        print(f"  U+{ord(c['text']):04X} fontname={c['fontname']} x={c['x0']:.1f} y={c['top']:.1f}")
    
    print()
    
    # Now find the area around line 14 (the options for Q1)
    # Q1 options should be around y=250-280 based on page layout
    # Let's find all chars between the ① area
    q1_chars = [c for c in chars if 245 < c['top'] < 265]
    print('=== Q1 options area chars ===')
    for c in q1_chars:
        print(f"  U+{ord(c['text']):04X} ({c['text']}) font={c['fontname']} x={c['x0']:.1f} y={c['top']:.1f}")
