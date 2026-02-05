#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix Unicode characters in watch_balance.py"""

import sys

# Read the file
with open('hll_rcon_tool/custom_tools/watch_balance.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the broken characters with the correct block character
# â– is the broken representation, we want █ (U+2588)
content = content.replace('â– ', '█')
content = content.replace('â–', '█')

# Write back
with open('hll_rcon_tool/custom_tools/watch_balance.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed Unicode characters!")
