# PDF Metadata Cleaner

A simple Python CLI tool to remove metadata from PDF files.  
Supports single files, batch processing, recursive folder traversal, and in-place replacement with automatic backup.

---

## 🚀 Features

- 🧼 Strips metadata from PDF files  
- 📁 Supports multiple files or folders  
- 🔁 Optional recursive folder scanning (`-r`)  
- 💥 In-place file replacement (`-i`) with `.bak` backup  
- 🔍 Deep cleaning option (`-d`) to remove embedded XMP metadata using `pikepdf`  
- 📝 Logs removed metadata to `pdf_metadata_removal.log`  

---

## 📦 Installation

1. Clone or download this repository.  
2. Install dependencies:

```bash
pip install pypdf pikepdf
````

*Note: `pikepdf` requires system dependencies (like `qpdf`) — see [pikepdf installation docs](https://pikepdf.readthedocs.io/en/latest/installation.html) for help.*

---

## 🔧 Usage

```bash
python clean_pdf.py [OPTIONS] path1 [path2 ...]
```

### Options

| Option               | Description                                                               |
| -------------------- | ------------------------------------------------------------------------- |
| `-i`, `--in-place`   | Replace original files (creates `.bak` backups)                           |
| `-r`, `--recursive`  | Recursively scan folders for `.pdf` files                                 |
| `-d`, `--deep-clean` | Perform a deep clean to remove embedded XMP metadata (requires `pikepdf`) |

---

## 📂 Examples

### Clean a single file (non-destructive)

```bash
python clean_pdf.py document.pdf
# Outputs: document_cleaned.pdf
```

### Clean and replace in-place with backup

```bash
python clean_pdf.py document.pdf -i
# Creates document.pdf.bak and overwrites document.pdf
```

### Recursively clean all PDFs in a folder

```bash
python clean_pdf.py myfolder -r
# Outputs cleaned versions in the same directory
```

### Recursively clean and replace all PDFs in-place

```bash
python clean_pdf.py myfolder another_folder -r -i
# Backs up and cleans all PDFs in both folders and subfolders
```

### Deep clean to remove embedded XMP metadata

```bash
python clean_pdf.py sensitive.pdf -d
# Uses pikepdf to remove XMP metadata; outputs sensitive_cleaned.pdf
```

---

## 📝 Logging

All actions and removed metadata are logged to `pdf_metadata_removal.log`.

---

## 🛡 Notes

* Always check `.bak` files before deleting, especially when using `-i`.
* The tool does **not** modify PDF contents — only strips metadata.
* Deep cleaning requires `pikepdf` and its dependencies.
* Deep cleaning currently does not support in-place mode to avoid file corruption risks.

---

## 👩‍💻 Development & Testing

### Setup

Create a virtual environment and install development dependencies:

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
```

### Running Tests

Run the automated tests with:

```bash
pytest
```

Tests cover metadata removal, backup creation, recursive scanning, and deep clean functionality.

---

## 📃 License

This package is open-source and released under the [European Union Public License version 1.2](https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12).
You are free to use, modify, and distribute the package in accordance with the terms of the license.

---

## 🙌 Contributing

For contributions, bug reports, or suggestions, please visit the project repository on GitHub.

