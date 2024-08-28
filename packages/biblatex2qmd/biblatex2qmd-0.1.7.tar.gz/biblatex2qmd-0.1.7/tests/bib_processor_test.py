"""
Tests for BibLaTeX Processor

This module contains pytest-based tests for the BibLaTeX Processor script.
It tests the main functionalities of extracting information from BibLaTeX entries,
validating BibLaTeX files, and processing entries to create individual files and a corpus file.

To run these tests:
1. Ensure pytest is installed: pip install pytest
2. Run the command: pytest bib_processor_test.py

Make sure the bib_processor.py file is in the same directory as this test file.
"""

import pytest
from pathlib import Path
from lib.bib_processor import extract_biblatex_info, process_entries, validate_biblatex_file

@pytest.fixture(scope="function")
def unique_output_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("output")

@pytest.fixture
def mock_biblatex_entry():
    return {
        'author': 'Doe, John and Smith, Jane',
        'year': '2023',
        'title': 'A Study on BibLaTeX Processing',
        'ID': 'Doe2023',
        'abstract': 'This is a test abstract.',
        'keywords': 'biblatex, processing, test',
        'note': '{"importance": "high", "read": "yes"}'
    }

@pytest.fixture
def mock_biblatex_file(tmp_path):
    content = """@article{Doe2023,
        author = {Doe, John and Smith, Jane},
        year = {2023},
        title = {A Study on BibLaTeX Processing},
        abstract = {This is a test abstract.},
        keywords = {biblatex, processing, test},
        note = {{"importance": "high", "read": "yes"}}
    }"""
    file_path = tmp_path / "test.bib"
    file_path.write_text(content)
    return str(file_path)

def test_extract_biblatex_info(mock_biblatex_entry):
    fields_to_extract = ['author_last_name', 'year', 'title', 'ID', 'abstract', 'keywords', 'note']
    info = extract_biblatex_info(mock_biblatex_entry, fields_to_extract)
    assert info['author_last_name'] == 'Doe'
    assert info['year'] == '2023'
    assert info['title'] == 'A Study on BibLaTeX Processing'
    assert info['ID'] == 'Doe2023'
    assert info['abstract'] == 'This is a test abstract.'
    assert info['keywords'] == 'biblatex, processing, test'
    assert info['note'] == "{'importance': 'high', 'read': 'yes'}"

    # Add a test for entries without a note
    entry_without_note = mock_biblatex_entry.copy()
    del entry_without_note['note']
    info_without_note = extract_biblatex_info(entry_without_note, fields_to_extract)
    assert info_without_note['note'] == "{}"

def test_validate_biblatex_file(mock_biblatex_file, tmp_path):
    assert validate_biblatex_file(mock_biblatex_file) == True

    invalid_file = tmp_path / "invalid.bib"
    invalid_file.write_text("This is not a valid BibLaTeX file")
    with pytest.raises(ValueError):
        validate_biblatex_file(str(invalid_file))

    empty_file = tmp_path / "empty.bib"
    empty_file.write_text("")
    with pytest.raises(ValueError):
        validate_biblatex_file(str(empty_file))

def test_process_entries(mock_biblatex_file, unique_output_dir):
    fields_to_extract = ['author_last_name', 'year', 'title', 'ID', 'abstract', 'keywords', 'note']
    process_entries(mock_biblatex_file, str(unique_output_dir), fields_to_extract)
    
    # Check individual abstract file
    abstract_dir = unique_output_dir / "abstract"
    assert abstract_dir.is_dir()
    abstract_file = abstract_dir / "Doe2023.md"
    assert abstract_file.is_file()
    
    with open(abstract_file, 'r') as f:
        content = f.read()
        assert "Doe2023" in content
        assert "A Study on BibLaTeX Processing" in content
        assert "This is a test abstract." in content
        assert "biblatex, processing, test" in content
        assert "importance: high" in content
        assert "read: yes" in content

    # Check corpus file
    corpus_dir = unique_output_dir / "corpus"
    assert corpus_dir.is_dir()
    corpus_file = corpus_dir / "corpus.md"
    assert corpus_file.is_file()
    
    with open(corpus_file, 'r') as f:
        content = f.read()
        assert "Doe2023" in content
        assert "A Study on BibLaTeX Processing" in content

def test_process_entries_empty_file(unique_output_dir):
    empty_file = unique_output_dir / "empty.bib"
    empty_file.write_text("")
    fields_to_extract = ['author_last_name', 'year', 'title', 'ID', 'abstract', 'keywords', 'note']
    
    with pytest.raises(ValueError):
        process_entries(str(empty_file), str(unique_output_dir), fields_to_extract)

def test_process_entries_invalid_file(unique_output_dir):
    invalid_file = unique_output_dir / "invalid.bib"
    invalid_file.write_text("This is not a valid BibLaTeX file")
    fields_to_extract = ['author_last_name', 'year', 'title', 'ID', 'abstract', 'keywords', 'note']
    
    with pytest.raises(ValueError):
        process_entries(str(invalid_file), str(unique_output_dir), fields_to_extract)

if __name__ == "__main__":
    pytest.main([__file__])