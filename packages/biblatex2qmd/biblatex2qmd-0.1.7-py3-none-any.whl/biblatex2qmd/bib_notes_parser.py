"""
This script parses bibliographic entries from a BibTeX file, extracting
structured information from the notes field of each entry.
"""

import re
from typing import Dict, List, Union
from collections import Counter
from textwrap import shorten
import bibtexparser
from bibtexparser.bibdatabase import BibDatabase

TAG_NAMES = ['Summary', 'Framework', 'Theory', 'Findings', 'Methodology']


def contains_tags(note_text: str) -> bool:
    """
    Check if the note text contains any of the defined tags, case-insensitive.

    Args:
    note_text (str): The text of the note to check.

    Returns:
    bool: True if any tag is found, False otherwise.
    """
    lower_text = note_text.lower()
    return any(f'@{tag.lower()}:' in lower_text for tag in TAG_NAMES)


def parse_note(note_text: str) -> Dict[str, str]:
    """
    Parse a note text to extract structured information, case-insensitive.

    Args:
    note_text (str): The text of the note to parse.

    Returns:
    dict: A dictionary containing the parsed sections of the note, or an error message if nested or invalid tags are found.
    """
    result = {}
    lowercase_text = note_text.lower()
    
    # Find all start and end tags
    start_tags = re.findall(r'@(\w+):', lowercase_text)
    end_tags = re.findall(r'@end(\w+)', lowercase_text)

    # Check for nested tags
    open_tags = []
    for tag in re.finditer(r'@(\w+):|@end(\w+)', lowercase_text):
        if tag.group(1):  # Start tag
            open_tags.append(tag.group(1))
        else:  # End tag
            if not open_tags or open_tags[-1] != tag.group(2):
                return {"error": "Mismatched tags found. Each start tag must have a corresponding end tag."}
            open_tags.pop()
        if len(open_tags) > 1:
            return {"error": "Nested tags found. Nested tags are not allowed."}

    # Check for invalid tags
    invalid_tags = set(start_tags) - set(t.lower() for t in TAG_NAMES)
    if invalid_tags:
        return {"error": f"Invalid tag(s) found: {', '.join(invalid_tags)}. Only tags listed in TAG_NAMES are allowed."}

    # Parse content if no errors
    for tag in TAG_NAMES:
        pattern = rf'@{tag.lower()}:(.*?)@end{tag.lower()}'
        match = re.search(pattern, lowercase_text, re.DOTALL | re.IGNORECASE)
        if match:
            content = note_text[match.start(1):match.end(1)].strip()
            result[tag] = content.strip().strip('\\\n')

    return result


def process_entries(bib_database: Union[Dict, bibtexparser.bibdatabase.BibDatabase]) -> Dict[str, Dict[str, str]]:
    """
    Process each entry in the BibTeX database.

    Args:
    bib_database (Union[Dict, bibtexparser.bibdatabase.BibDatabase]): The BibTeX database.

    Returns:
    dict: A dictionary of parsed notes keyed by entry ID.
    """
    if isinstance(bib_database, bibtexparser.bibdatabase.BibDatabase):
        entries = bib_database.entries
    elif isinstance(bib_database, dict):
        entries = bib_database.get('entries', bib_database)
    else:
        raise TypeError("bib_database must be either a dict or a BibDatabase object")

    return {
        entry['ID']: parsed_note
        for entry in entries
        if 'note' in entry and contains_tags(entry['note'])
        and (parsed_note := parse_note(entry['note']))
    }


def print_statistics(bib_database: Union[Dict, List, BibDatabase], all_parsed_notes: Dict):
    """
    Print statistics about the processed entries.

    Args:
    bib_database (Union[Dict, List, BibDatabase]): The BibTeX database.
    all_parsed_notes (dict): The dictionary of parsed notes.
    """
    if isinstance(bib_database, BibDatabase):
        entries = bib_database.entries
    elif isinstance(bib_database, dict):
        entries = bib_database.get('entries', bib_database)
    elif isinstance(bib_database, list):
        entries = bib_database
    else:
        raise TypeError("bib_database must be either a dict, list, or BibDatabase object")

    counts = Counter({'total': len(entries), 'notes': sum('note' in entry for entry in entries), 'tagged': len(all_parsed_notes)})
    
    print(f"\nEntries, Notes, Notes with tags, Parsed notes: {counts['total']}, {counts['notes']}, {counts['tagged']}, {counts['tagged']}")
    if counts['total'] > 0:
        percentages = {k: v / counts['total'] * 100 for k, v in counts.items()}
        print(f"Percentages: {percentages['total']:.0f}%, {percentages['notes']:.0f}%, {percentages['tagged']:.0f}%, {percentages['tagged']:.0f}%")
    else:
        print("Percentages: N/A (no entries)")


def print_parsed_notes(all_parsed_notes: Dict[str, Dict[str, str]]):
    """
    Print the contents of parsed notes.

    Args:
    all_parsed_notes (dict): The dictionary of parsed notes.
    """
    print("\nContents of parsed notes:")
    for entry_id, parsed_note in all_parsed_notes.items():
        print(f"\nEntry ID: {entry_id}")
        for tag, content in parsed_note.items():
            print(f"  {tag}:")
            print(f"    {shorten(content, width=50, placeholder='...')}")

def main():
    """Main execution function."""
    with open('bib/SLR_Selection_Papers.bib') as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)

    all_parsed_notes = process_entries(bib_database)
    print_statistics(bib_database, all_parsed_notes)
    print_parsed_notes(all_parsed_notes)


if __name__ == "__main__":
    main()