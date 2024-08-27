"""
BibLaTeX Processor

This script processes a BibLaTeX file, extracts information from each entry,
creates individual Markdown files for each entry, and a combined corpus file.

Dependencies: bibtexparser, bib_notes_parser
"""

import shutil
from typing import List, Dict
from pathlib import Path
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
import bib_notes_parser
import ast

def validate_biblatex_file(file_path: str) -> bool:
    try:
        with open(file_path, 'r', encoding='utf-8') as bibtex_file:
            parser = BibTexParser(common_strings=True)
            parser.customization = convert_to_unicode
            bib_database = bibtexparser.load(bibtex_file)
        
        if not bib_database.entries:
            raise ValueError("The BibLaTeX file contains no valid entries.")
        return True
    except (bibtexparser.bibdatabase.UndefinedString, Exception) as e:
        raise ValueError(f"Error validating BibLaTeX file: {str(e)}")

def setup_directories(output_directory: str) -> Dict[str, Path]:
    dirs = {name: Path(output_directory) / name for name in ['source', 'abstract', 'corpus']}
    for dir_path in dirs.values():
        if dir_path.exists():
            shutil.rmtree(dir_path)
        dir_path.mkdir(parents=True)
    return dirs

def extract_biblatex_info(entry: Dict[str, str], fields: List[str]) -> Dict[str, str]:
    info = {}
    author = entry.get('author', "No author available").split(' and ')[0]
    info['author_last_name'] = author.split('family=')[-1].split(',')[0].strip().replace(' ', '').replace('{', '').replace('}', '')
    info['year'] = entry.get('year') or entry.get('date', 'Unknown year').split('-')[0]

    for field in fields:
        if field in ['author_last_name', 'year']:
            continue
        elif field == 'keywords':
            info[field] = ', '.join(k.strip() for k in entry.get('keywords', "").split(',') if k.strip() != "/unread")
        elif field == 'note':
            note_content = entry.get('note', '')
            try:
                parsed_note = ast.literal_eval(note_content)
                info[field] = str(parsed_note) if isinstance(parsed_note, dict) else "{}"
            except:
                info[field] = "{}"
        else:
            info[field] = entry.get(field, f"No {field} available")
    
    return info

def process_entries(biblatex_file: str, output_directory: str, fields_to_extract: List[str]) -> None:
    validate_biblatex_file(biblatex_file)
    dirs = setup_directories(output_directory)
    shutil.copy2(biblatex_file, dirs['source'])

    with open(biblatex_file, 'r', encoding='utf-8') as bibtex_file:
        parser = BibTexParser(common_strings=True)
        parser.customization = convert_to_unicode
        entries = bibtexparser.load(bibtex_file).entries

    corpus_content = []
    for entry in entries:
        info = extract_biblatex_info(entry, fields_to_extract)
        header = f"## {info['author_last_name']}{info['year']}\n\n"

        field_content = []
        for field in fields_to_extract:
            if field not in ['author_last_name', 'year']:
                if field == 'note' and info['note'] != "{}":
                    try:
                        note_dict = ast.literal_eval(info['note'])
                        note_content = "\n".join([f"{key}: {value}" for key, value in note_dict.items() if value])
                        if note_content:
                            field_content.append(f"**Note**\n\n{note_content}\n")
                    except:
                        # If there's an error parsing the note, skip it
                        pass
                else:
                    field_value = info[field]
                    if field == 'ID':
                        field_value = f"@{field_value}"
                    field_content.append(f"**{field.capitalize()}**\n\n{field_value}\n")

        file_content = header + '\n'.join(field_content)
        corpus_content.append(file_content)
        
        with open(dirs['abstract'] / f"{info['author_last_name']}{info['year']}.md", 'w', encoding='utf-8') as file:
            file.write(file_content)

    try:
        with open(dirs['corpus'] / 'corpus.md', 'w', encoding='utf-8') as file:
            file.write('\n\n'.join(corpus_content))
        print(f"Successfully processed {len(entries)} entries from {Path(biblatex_file).name}.")
        print(f"Individual files created in {dirs['abstract']}")
        print(f"Corpus file created in {dirs['corpus']}")
    except Exception as e:
        print(f"Error creating corpus.md: {e}")

        
if __name__ == "__main__":
    input_file = 'bib/SLR_Selection_Papers.bib'
    fields_to_extract = ['author_last_name', 'year', 'title', 'ID', 'abstract', 'keywords', 'note']
    output_directory = './papers'
    process_entries(input_file, output_directory, fields_to_extract)