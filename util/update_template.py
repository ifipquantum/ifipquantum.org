#!/usr/bin/env python3

# update_template.py - a simple Python script for plain HTML templates
#
# Copyright (c) 2026 Aleks Kissinger
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import glob
import re

# Paths are relative to the parent directory of this script
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HEADER_TEMPLATE = os.path.join(BASE_DIR, "templates", "_header.html")
FOOTER_TEMPLATE = os.path.join(BASE_DIR, "templates", "_footer.html")

# Each entry consists of a 'pattern' matching files to process, and additional
# strings which can be substituted for placeholders in the template, e.g. the
# any occurrence of '{{ROOT}}' in the template gets substituted for 'ROOT'
FILES = [
    { 'pattern': os.path.join(BASE_DIR, "index.html"), 'ROOT': '' },
    { 'pattern': os.path.join(BASE_DIR, "pages", "*.html"), 'ROOT': '../' },
]

def update_template():
    with open(HEADER_TEMPLATE, 'r', encoding='utf-8') as f:
        header_template = f.read()
    with open(FOOTER_TEMPLATE, 'r', encoding='utf-8') as f:
        footer_template = f.read()

    for desc in FILES:
        # substitute placeholders in template
        def rep(m):
            return desc[m.group(1)]
        header = re.sub(r'{{([^}]+)}}', rep, header_template)
        footer = re.sub(r'{{([^}]+)}}', rep, footer_template)

        # replace contents of <header> and <footer> with template
        for filepath in glob.glob(desc['pattern']):
            print(f"\nProcessing file: {filepath}")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                
                parts = [original_content]
                parts += parts.pop().split("<header>")
                if len(parts) != 2:
                    raise Exception("<header> tag not found")
                parts += parts.pop().split("</header>")
                if len(parts) != 3:
                    raise Exception("</header> tag not found")
                parts += parts.pop().split("<footer>")
                if len(parts) != 4:
                    raise Exception("<footer> tag not found")
                parts += parts.pop().split("</footer>")
                if len(parts) != 5:
                    raise Exception("</footer> tag not found")

                # Inject content
                modified_content = (
                    parts[0] +
                    "<header>\n" + 
                    header +
                    "\n</header>" + 
                    parts[2] +
                    "<footer>\n" + 
                    footer +
                    "\n</footer>" + 
                    parts[4] 
                )
            except Exception as e:
                print(f"SKIPPED {filepath}: {e}")

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            print("OK")

if __name__ == "__main__":
    update_template()
