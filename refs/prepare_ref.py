'''
维护文献清单
'''

from pathlib import Path

REF_FILE = Path("C:/coding/FLT/yanboc-thesis/includefile/reference.tex")

def remove_duplicate(ref_file: Path=REF_FILE):
    tex_lines = []
    with open(ref_file, 'r', encoding='utf-8') as file:
        for line in file:
            line_content = line.strip('\n')
            tex_lines.append(line_content)
    tex_lines = list(set(tex_lines))
    

def to_thesis_format(conf_format: str, thesis_format: str):
