import pytest
from lib.bib_notes_parser import parse_note, contains_tags, process_entries , print_parsed_notes, print_statistics

# lib/tests/bib_notes_parser_test.py

def test_parse_note():
    print("Testing parse_note function")
    assert parse_note is not None

def test_parse_note():
    input_text = """
    @Summary:
    This is a summary text.
    @EndSummary

    @Framework:
    This is a framework description.
    @EndFramework

    @Theory:
    This is the theory section.
    @EndTheory

    @Findings:
    These are the findings.
    @EndFindings

    @Methodology:
    This is the methodology.
    @EndMethodology
    """

    expected_output = {
        'Summary': 'This is a summary text.',
        'Framework': 'This is a framework description.',
        'Theory': 'This is the theory section.',
        'Findings': 'These are the findings.',
        'Methodology': 'This is the methodology.'
    }
    
    assert parse_note(input_text) == expected_output

def test_contains_tags():
    input_text = "@Summary:\nThis is a summary.\n@EndSummary\n@Methodology:\nThis is the methodology.\n@EndMethodology"
    assert contains_tags(input_text) is True

def test_contains_tags_false():
    input_text = "This is a note without tags"
    assert contains_tags(input_text) is False

def test_contains_tags_case_insensitive():
    assert contains_tags("@summary: This is a lowercase tag @endsummary") is True
    assert contains_tags("@SUMMARY: This is an uppercase tag @ENDSUMMARY") is True
    assert contains_tags("@SuMmArY: This is a mixed case tag @EnDsUmMaRy") is True
    assert contains_tags("This text contains no tags") is False
    assert contains_tags("@InvalidTag: This is not a valid tag @EndInvalidTag") is False

def test_parse_note_case_insensitive():
    input_text = "@summary: This is a lowercase tag @endsummary"
    expected = {'Summary': 'This is a lowercase tag'}
    assert parse_note(input_text) == expected

def test_parse_note_invalid_tag():
    input_text = "@InvalidTag: This is an invalid tag @EndInvalidTag"
    expected = {"error": "Invalid tag(s) found: invalidtag. Only tags listed in TAG_NAMES are allowed."}
    assert parse_note(input_text) == expected

def test_parse_note_mixed_case():
    input_text = "@SuMmArY: This is a mixed case tag @EnDsUmMaRy"
    expected = {'Summary': 'This is a mixed case tag'}
    assert parse_note(input_text) == expected

def test_parse_note_empty():
    input_text = ""
    assert parse_note(input_text) == {}

def test_parse_note_single_tag():
    input_text = "@Summary:\nThis is a single summary.\n@EndSummary"
    expected_output = {'Summary': 'This is a single summary.'}
    assert parse_note(input_text) == expected_output

def test_parse_note_nested_tags():
    input_text = "@Summary: This is a summary @Methodology: with a nested tag @EndMethodology @EndSummary"
    expected = {"error": "Nested tag found within Summary. Nested tags are not allowed."}
    assert parse_note(input_text) == expected

def test_parse_note_nested_tags():
    input_text = "@Summary: This is a summary @Methodology: with a nested tag @EndMethodology @EndSummary"
    expected = {"error": "Nested tag found within Summary. Nested tags are not allowed."}
    assert parse_note(input_text) == expected

    
def test_parse_note_multiple_tags():
    input_text = """@Summary:
This is a summary.
@EndSummary
@Methodology:
This is the methodology.
@EndMethodology
@Findings:
These are the findings.
@EndFindings"""
    expected_output = {
        'Summary': 'This is a summary.',
        'Methodology': 'This is the methodology.',
        'Findings': 'These are the findings.'
    }
    assert parse_note(input_text) == expected_output

def test_parse_note_with_extra_text():
    input_text = """Some extra text
@Summary:
This is a summary.
@EndSummary
More extra text
@Methodology:
This is the methodology.
@EndMethodology
Final extra text"""
    expected_output = {
        'Summary': 'This is a summary.',
        'Methodology': 'This is the methodology.'
    }
    assert parse_note(input_text) == expected_output


def test_parse_note_missing_end_tag():
    input_text = "@Summary: This is a summary without an end tag"
    assert parse_note(input_text) == {}


def test_parse_note_single_tag():
    input_text = "@Summary:\nThis is a single summary.\n@EndSummary"
    expected_output = {'Summary': 'This is a single summary.'}
    assert parse_note(input_text) == expected_output


def test_parse_note_nested_tags():
    input_text = "@Summary: This is a summary @Methodology: with a nested tag @EndMethodology @EndSummary"
    expected = {"error": "Nested tags found. Nested tags are not allowed."}
    assert parse_note(input_text) == expected


def test_parse_note_mismatched_tags():
    input_text = "@Summary: This is a summary @EndMethodology"
    expected = {"error": "Mismatched tags found. Each start tag must have a corresponding end tag."}
    assert parse_note(input_text) == expected


def test_parse_note_invalid_tag():
    input_text = "@InvalidTag: This is an invalid tag @EndInvalidTag"
    expected = {"error": "Invalid tag(s) found: invalidtag. Only tags listed in TAG_NAMES are allowed."}
    assert parse_note(input_text) == expected


def test_parse_note_multiple_valid_tags():
    input_text = "@Summary: This is a summary @EndSummary @Methodology: This is a methodology @EndMethodology"
    expected = {'Summary': 'This is a summary', 'Methodology': 'This is a methodology'}
    assert parse_note(input_text) == expected


@pytest.fixture
def sample_bib_database():
    return {
        'entries': [
            {'ID': 'entry1', 'note': '@Methodology:\nMethod 1\n@EndMethodology'},
            {'ID': 'entry2', 'note': 'No tags here'},
            {'ID': 'entry3', 'note': '@Summary:\nSummary\n@EndSummary\n@Methodology:\nMethod 2\n@EndMethodology'},
            {'ID': 'entry4', 'note': '@Framework:\nFramework\n@EndFramework'},
        ]
    }

def test_process_entries(sample_bib_database):
    all_parsed_notes = process_entries(sample_bib_database)
    
    assert len(all_parsed_notes) == 3
    assert 'entry1' in all_parsed_notes
    assert 'entry2' not in all_parsed_notes
    assert 'entry3' in all_parsed_notes
    assert 'entry4' in all_parsed_notes
    assert all_parsed_notes['entry1'] == {'Methodology': 'Method 1'}
    assert all_parsed_notes['entry3'] == {'Summary': 'Summary', 'Methodology': 'Method 2'}
    assert all_parsed_notes['entry4'] == {'Framework': 'Framework'}

def test_process_entries_empty_database():
    empty_database = {'entries': []}
    assert process_entries(empty_database) == {}

def test_process_entries_no_valid_notes():
    database = {'entries': [
        {'ID': 'entry1', 'note': 'No tags here'},
        {'ID': 'entry2', 'note': 'Also no tags'}
    ]}
    assert process_entries(database) == {}


def test_print_statistics(capsys):
    bib_database_dict = {'entries': [
        {'ID': 'entry1', 'note': '@Methodology:\nMethod 1\n@EndMethodology'},
        {'ID': 'entry2', 'note': 'No tags here'},
        {'ID': 'entry3', 'note': '@Summary:\nSummary\n@EndSummary\n@Methodology:\nMethod 2\n@EndMethodology'},
        {'ID': 'entry4', 'note': '@Framework:\nFramework\n@EndFramework'}
    ]}
    bib_database_list = bib_database_dict['entries']
    all_parsed_notes = {'entry1': {'Methodology': 'Method 1'}, 'entry3': {'Methodology': 'Method 2', 'Summary': 'Summary'}, 'entry4': {'Framework': 'Framework'}}

    # Test with dictionary input
    print_statistics(bib_database_dict, all_parsed_notes)
    captured = capsys.readouterr()
    assert "Entries, Notes, Notes with tags, Parsed notes: 4, 4, 3, 3" in captured.out
    assert "Percentages: 100%, 100%, 75%, 75%" in captured.out

    # Test with list input
    print_statistics(bib_database_list, all_parsed_notes)
    captured = capsys.readouterr()
    assert "Entries, Notes, Notes with tags, Parsed notes: 4, 4, 3, 3" in captured.out
    assert "Percentages: 100%, 100%, 75%, 75%" in captured.out

    # Test with empty input
    print_statistics([], {})
    captured = capsys.readouterr()
    assert "Entries, Notes, Notes with tags, Parsed notes: 0, 0, 0, 0" in captured.out
    assert "Percentages: N/A (no entries)" in captured.out


def test_print_parsed_notes(capsys):
    all_parsed_notes = {
        'entry1': {'Summary': 'Test summary', 'Methodology': 'Test method'},
        'entry2': {'Framework': 'Test framework'}
    }
    print_parsed_notes(all_parsed_notes)
    captured = capsys.readouterr()
    assert "Entry ID: entry1" in captured.out
    assert "Summary:" in captured.out
    assert "Methodology:" in captured.out
    assert "Entry ID: entry2" in captured.out
    assert "Framework:" in captured.out