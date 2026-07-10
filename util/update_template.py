#!/bin/env python
import os
import glob

# Paths are relative to this script
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
HEADER_TEMPLATE = os.path.join(BASE_DIR, "_header.html")
FOOTER_TEMPLATE = os.path.join(BASE_DIR, "_footer.html")
FILES = [
    os.path.join(BASE_DIR, "..", "index.html"),
    os.path.join(BASE_DIR, "..", "pages", "*.html")
]

def update_template():
    with open(HEADER_TEMPLATE, 'r', encoding='utf-8') as f:
        header_template = f.read()
    with open(FOOTER_TEMPLATE, 'r', encoding='utf-8') as f:
        footer_template = f.read()

    target_files = []
    for pattern in FILES:
        target_files.extend(glob.glob(pattern))

    for filepath in target_files:
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
                header_template +
                "\n</header>" + 
                parts[2] +
                "<footer>\n" + 
                footer_template +
                "\n</footer>" + 
                parts[4] 
            )
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(modified_content)
        except Exception as e:
            print(f"ERROR in {filepath}: {e}")
        print("OK")

if __name__ == "__main__":
    update_template()
