# scrub.py Documentation

This document explains the purpose, usage, and internal workings of the `scrub.py` script, which strips EXIF metadata from images embedded in PDF files.

---

## 📄 Overview

**File:** `scrub.py`

**Purpose:**

* Locate JPEG or PNG image streams embedded in a PDF.
* Extract each image’s binary data.
* Use Pillow to remove EXIF metadata from supported image formats.
* Replace the original image stream with the cleaned version.
* Save a new PDF file with `_scrubbed` appended to the original filename.

**Key dependencies:**

* `pypdf` (for parsing and writing PDFs)
* `Pillow` (for handling and re-saving image data)

---

## 🔧 Installation

Ensure you have Python 3.7+ and install required packages:

```bash
pip install pypdf Pillow
```

---

## 🚀 Usage

Run from the command line, passing a single PDF path:

```bash
python scrub.py <input_pdf_path>
```

* If `<input_pdf_path>` does not exist, the script prints an error and exits.
* Otherwise, it creates a new file named `<base>_scrubbed.pdf` in the same directory.

**Example:**

```bash
python scrub.py report.pdf
# Generates report_scrubbed.pdf
```

---

## 📑 Main Functions

### `strip_exif_from_image_stream(stream_data)`

* **Input:** Raw bytes of an image stream (e.g., JPEG or PNG data).
* **Process:**

  1. Attempt to open the bytes as an image via Pillow.
  2. If format is `JPEG` or `PNG`, re-save the image into a `BytesIO` buffer without preserving EXIF.
  3. Return the cleaned bytes.
  4. If not a supported image type or unopenable, return the original bytes.
* **Output:** Cleaned image bytes (no EXIF) or the original data.

### `scrub_pdf_images_exif(input_pdf_path, output_pdf_path)`

* **Input:**

  * `input_pdf_path`: Path to the source PDF.
  * `output_pdf_path`: Path to write the cleaned PDF.
* **Process:**

  1. Open the input PDF with `PdfReader`.
  2. Create a `PdfWriter` to collect cleaned pages.
  3. For each page:

     * Check if `/Resources` and `/XObject` exist.
     * For each XObject entry, identify if `/Subtype` is `/Image`.
     * If so, extract raw image data via `obj.get_data()`.
     * Pass raw data to `strip_exif_from_image_stream()`. If the returned data differs, replace `obj._data`.
     * Count total images and how many were cleaned.
     * Add the (possibly modified) page to the writer.
  4. Write all pages to `output_pdf_path`.
  5. Print a summary of images processed vs. cleaned.
* **Output:** Creates `output_pdf_path` containing the same pages but with EXIF-free image streams.

### `main()`

* Parses `sys.argv` to get a single argument: input PDF path.
* Validates file existence.
* Computes `output_pdf_path` by appending `_scrubbed.pdf`.
* Calls `scrub_pdf_images_exif(...)`.

---

## ⚠️ Limitations & Notes

* Only JPEG and PNG streams are handled for EXIF stripping; other formats pass through unchanged.
* Some PDF images might use uncommon filters or color spaces not recognized as `/Image` XObjects.
* The script always writes a new file; it does **not** modify the original in-place.
* Image quality/compression might slightly change when re-saving via Pillow.

---

## 📂 Testing

A `test_scrub.py` suite (for pytest) can:

1. Generate a minimal PDF containing a JPEG with real EXIF (using `piexif`).
2. Verify that EXIF is present initially and removed after scrubbing.
3. Confirm that pages count remains unchanged for PDFs without images.

To run tests:

```bash
pip install pytest pillow pypdf piexif
pytest test_scrub.py
```

