import re
import os

files = ['accounts/views.py', 'cart/views.py', 'products/views.py', 'orders/views.py', 'dashboard/views.py']

for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()
    
    # Remove all docstrings (""" ... """)
    content = re.sub(r'""".*?"""', '', content, flags=re.DOTALL)
    # Remove all single-line comments (# ...)
    content = re.sub(r'#.*$', '', content, flags=re.MULTILINE)
    # Remove multiple blank lines
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    with open(f, 'w', encoding='utf-8') as fh:
        fh.write(content)
    print(f'Cleaned: {f}')