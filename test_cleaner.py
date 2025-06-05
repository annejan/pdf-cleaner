import os
import shutil
import tempfile
from pathlib import Path
from pypdf import PdfWriter, PdfReader

import pytest
import cleaner


@pytest.fixture
def sample_pdf(tmp_path):
    pdf_path = tmp_path / "test.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.add_metadata({
        '/Author': 'UnitTester',
        '/Title': 'Test PDF'
    })
    with open(pdf_path, 'wb') as f:
        writer.write(f)
    return pdf_path


def test_clean_metadata_creates_cleaned_copy(sample_pdf):
    cleaner.clean_pdf_metadata(str(sample_pdf), in_place=False)
    cleaned_path = str(sample_pdf).replace(".pdf", "_cleaned.pdf")
    assert os.path.exists(cleaned_path)

    reader = PdfReader(cleaned_path)
    metadata = reader.metadata
    assert set(metadata.keys()) == {'/Producer'}


def test_in_place_mode_creates_backup_and_removes_metadata(sample_pdf):
    cleaner.clean_pdf_metadata(str(sample_pdf), in_place=True)
    backup_path = str(sample_pdf) + ".bak"
    assert os.path.exists(backup_path)

    reader = PdfReader(str(sample_pdf))
    metadata = reader.metadata
    assert set(metadata.keys()) == {'/Producer'}


def test_nonexistent_file_logs_error(tmp_path):
    fake_path = tmp_path / "nonexistent.pdf"
    try:
        cleaner.clean_pdf_metadata(str(fake_path), in_place=False)
    except Exception:
        pytest.fail("clean_pdf_metadata() raised an exception unexpectedly.")


def test_find_pdfs_single_file(sample_pdf):
    found = cleaner.find_pdfs([str(sample_pdf)])
    assert len(found) == 1
    assert found[0] == str(sample_pdf)


def test_find_pdfs_directory_nonrecursive(tmp_path, sample_pdf):
    found = cleaner.find_pdfs([str(tmp_path)], recursive=False)
    assert found == []


def test_find_pdfs_directory_recursive(tmp_path, sample_pdf):
    found = cleaner.find_pdfs([str(tmp_path)], recursive=True)
    assert str(sample_pdf) in found

