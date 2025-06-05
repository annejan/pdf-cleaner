# PDF Metadata Cleaner

A simple Python CLI tool to remove metadata from PDF files.  
Supports single files, batch processing, recursive folder traversal, and in-place replacement with automatic backup.

---

## 🚀 Features

- 🧼 Strips metadata from PDF files
- 📁 Supports multiple files or folders
- 🔁 Optional recursive folder scanning (`-r`)
- 💥 In-place file replacement (`-i`) with `.bak` backup
- 📝 Logs removed metadata to `pdf_metadata_removal.log`

---

## 📦 Installation

1. Clone or download this repository.
2. Install dependencies:

```bash
pip install pypdf
```

---

## 🔧 Usage

```bash
python clean_pdf.py [OPTIONS] path1 [path2 ...]
```

### Options

| Option            | Description                                      |
|-------------------|--------------------------------------------------|
| `-i`, `--in-place`| Replace original files (creates `.bak` backups) |
| `-r`, `--recursive`| Recursively scan folders for `.pdf` files      |

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

---

## 📝 Logging

All actions and removed metadata are logged to `pdf_metadata_removal.log`.

---

## 🛡️ Notes

- Always check `.bak` files before deleting, especially when using `-i`.
- Does not modify PDF contents — only strips metadata.

---

## 📃 License

This package is open-source and released under the [European Union Public License version 1.2](https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12).
You are free to use, modify, and distribute the package in accordance with the terms of the license.

## 👷 Contributing

For contributions, bug reports, or suggestions, please visit the project repository on GitHub.

