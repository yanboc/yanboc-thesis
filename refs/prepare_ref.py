'''
维护文献清单
'''

import os
import bibtexparser as bp
from semanticscholar import SemanticScholar
from semanticscholar.Paper import Paper
from pathlib import Path

SOURCE_BIB_FILE = Path("E:/hutou/projects/yanboc-thesis/refs/ref.bib")

def deduplicate_ref(bib_file: Path):
    with open(bib_file, mode='r', encoding='utf-8', newline='') as f:
        bib_text = f.read()
    bib_database = bp.loads(bib_text)
    existing_bib_ids = set()
    for entry in bib_database.entries:
        if entry["ID"] in existing_bib_ids:
            bib_database.entries.remove(entry)
            print(f"Removed {entry['ID']} from {bib_file}")
        else:
            print(f"Added {entry['ID']} to {bib_file}")
            existing_bib_ids.add(entry["ID"])
    
    with bib_file.open(mode='w', encoding='utf-8', newline='') as f:
        bp.dump(bib_database, f)

if __name__ == "__main__":
    deduplicate_ref(SOURCE_BIB_FILE)