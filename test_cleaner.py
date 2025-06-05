import os
import shutil
import tempfile
from pathlib import Path
from pypdf import PdfWriter, PdfReader

import pytest
import cleaner


@pytest.fixture
def sample_pdf_with_metadata(tmp_path):
    pdf_path = tmp_path / "test_with_meta.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.add_metadata({
        '/Author': 'UnitTester',
        '/Title': 'Test PDF'
    })
    with open(pdf_path, 'wb') as f:
        writer.write(f)
    return pdf_path


@pytest.fixture
def sample_pdf_without_metadata(tmp_path):
    pdf_path = tmp_path / "test_no_meta.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    # No metadata added
    with open(pdf_path, 'wb') as f:
        writer.write(f)
    return pdf_path


def test_clean_metadata_creates_cleaned_copy(sample_pdf_with_metadata):
    cleaner.clean_pdf_metadata(str(sample_pdf_with_metadata), in_place=False)
    cleaned_path = str(sample_pdf_with_metadata).replace(".pdf", "_cleaned.pdf")
    assert os.path.exists(cleaned_path)

    reader = PdfReader(cleaned_path)
    metadata = reader.metadata
    # Only /Producer should remain after cleaning
    assert set(metadata.keys()) == {'/Producer'}


def test_in_place_mode_creates_backup_and_removes_metadata(sample_pdf_with_metadata):
    cleaner.clean_pdf_metadata(str(sample_pdf_with_metadata), in_place=True)
    backup_path = str(sample_pdf_with_metadata) + ".bak"
    assert os.path.exists(backup_path)

    reader = PdfReader(str(sample_pdf_with_metadata))
    metadata = reader.metadata
    # Only /Producer should remain after cleaning
    assert set(metadata.keys()) == {'/Producer'}


def test_in_place_mode_skips_backup_when_no_metadata(sample_pdf_without_metadata):
    # No metadata except possibly /Producer, so no backup and no rewriting
    cleaner.clean_pdf_metadata(str(sample_pdf_without_metadata), in_place=True)
    backup_path = str(sample_pdf_without_metadata) + ".bak"
    assert not os.path.exists(backup_path)

    # File should remain unchanged, so metadata keys should be /Producer or empty
    reader = PdfReader(str(sample_pdf_without_metadata))
    metadata = reader.metadata or {}
    # Should be either empty or only /Producer (pypdf adds it by default)
    assert metadata == {} or set(metadata.keys()) == {'/Producer'}


def test_cleaning_skips_when_no_metadata(sample_pdf_without_metadata):
    # Cleaning in non-in-place mode also skips if no meaningful metadata
    cleaner.clean_pdf_metadata(str(sample_pdf_without_metadata), in_place=False)
    cleaned_path = str(sample_pdf_without_metadata).replace(".pdf", "_cleaned.pdf")
    # The cleaned file should NOT be created because nothing to clean
    assert not os.path.exists(cleaned_path)


def test_nonexistent_file_logs_error(tmp_path):
    fake_path = tmp_path / "nonexistent.pdf"
    try:
        cleaner.clean_pdf_metadata(str(fake_path), in_place=False)
    except Exception:
        pytest.fail("clean_pdf_metadata() raised an exception unexpectedly.")


def test_find_pdfs_single_file(sample_pdf_with_metadata):
    found = cleaner.find_pdfs([str(sample_pdf_with_metadata)])
    assert len(found) == 1
    assert found[0] == str(sample_pdf_with_metadata)


def test_find_pdfs_directory_nonrecursive(tmp_path, sample_pdf_with_metadata):
    found = cleaner.find_pdfs([str(tmp_path)], recursive=False)
    assert found == []


def test_find_pdfs_directory_recursive(tmp_path, sample_pdf_with_metadata):
    found = cleaner.find_pdfs([str(tmp_path)], recursive=True)
    assert str(sample_pdf_with_metadata) in found

