import os
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DecodedStreamObject, NameObject, NumberObject, DictionaryObject
from PIL import Image
import pytest
import scrub
import io


def create_pdf_with_exif_image(pdf_path):
    try:
        import piexif
    except ImportError:
        pytest.skip("piexif not installed; skipping EXIF embedding")

    # Create an image with real EXIF metadata using piexif
    img = Image.new("RGB", (100, 100), color="red")
    exif_dict = {"0th": {piexif.ImageIFD.Artist: "UnitTester"}}
    exif_bytes = piexif.dump(exif_dict)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG", exif=exif_bytes)
    img_data = img_bytes.getvalue()

    # Create a PDF with an image XObject
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    # Create image stream
    stream = DecodedStreamObject()
    stream.set_data(img_data)
    stream.update({
        NameObject("/Type"): NameObject("/XObject"),
        NameObject("/Subtype"): NameObject("/Image"),
        NameObject("/Width"): NumberObject(100),
        NameObject("/Height"): NumberObject(100),
        NameObject("/ColorSpace"): NameObject("/DeviceRGB"),
        NameObject("/BitsPerComponent"): NumberObject(8),
        NameObject("/Filter"): NameObject("/DCTDecode"),
    })
    ref = writer._add_object(stream)

    # Assign to page resources
    page = writer.pages[0]
    resources = DictionaryObject()
    xobj = DictionaryObject()
    xobj[NameObject("/Im0")] = ref
    resources[NameObject("/XObject")] = xobj
    page[NameObject("/Resources")] = resources

    with open(pdf_path, "wb") as f:
        writer.write(f)


@pytest.fixture
def pdf_with_embedded_jpeg(tmp_path):
    pdf_path = tmp_path / "with_image.pdf"
    create_pdf_with_exif_image(str(pdf_path))
    return pdf_path


def test_scrub_pdf_removes_exif(tmp_path, pdf_with_embedded_jpeg):
    # Verify EXIF exists before scrubbing
    reader_orig = PdfReader(str(pdf_with_embedded_jpeg))
    page = reader_orig.pages[0]
    xobjects = page["/Resources"]["/XObject"]
    for name in xobjects:
        obj = xobjects[name].get_object()
        data = obj.get_data()
        img = Image.open(io.BytesIO(data))
        exif = img.getexif()
        assert len(exif) > 0, "EXIF should exist before scrubbing"

    # Run scrub
    output_path = tmp_path / "scrubbed.pdf"
    scrub.scrub_pdf_images_exif(str(pdf_with_embedded_jpeg), str(output_path))
    assert output_path.exists()

    # Verify EXIF removed
    reader = PdfReader(str(output_path))
    page = reader.pages[0]
    xobjects = page["/Resources"]["/XObject"]
    for name in xobjects:
        obj = xobjects[name].get_object()
        data = obj.get_data()
        img = Image.open(io.BytesIO(data))
        exif = img.getexif()
        assert len(exif) == 0, "EXIF data was not stripped"


def test_scrub_script_main_runs(tmp_path, monkeypatch):
    input_pdf = tmp_path / "input.pdf"
    output_pdf = tmp_path / "input_scrubbed.pdf"

    # Create dummy PDF without images
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    with open(input_pdf, "wb") as f:
        writer.write(f)

    monkeypatch.setattr("sys.argv", ["scrub.py", str(input_pdf)])
    scrub.main()

    assert output_pdf.exists()

