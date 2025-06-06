import os
import shutil
import pypdf
import logging
import argparse

logging.basicConfig(filename='pdf_metadata_removal.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s')

def clean_pdf_metadata(input_pdf_path, in_place=False, deep_clean=False):
    input_pdf_path = os.path.abspath(input_pdf_path)

    if not os.path.exists(input_pdf_path):
        logging.error(f"File does not exist: {input_pdf_path}")
        return

    if deep_clean:
        try:
            import pikepdf
        except ImportError:
            logging.error("pikepdf is required for deep clean. Please install it via `pip install pikepdf`.")
            return

        try:
            with pikepdf.open(input_pdf_path) as pdf:
                has_changes = False

                if pdf.docinfo:
                    pdf.docinfo = pdf.make_indirect(pikepdf.Dictionary())
                    has_changes = True

                for key in ["/Metadata", "/PieceInfo"]:
                    if key in pdf.Root:
                        del pdf.Root[key]
                        has_changes = True

                if not has_changes:
                    logging.info(f"No removable metadata found in {input_pdf_path}. Skipping deep clean.")
                    return

                if in_place:
                    backup_path = input_pdf_path + ".bak"
                    shutil.copy2(input_pdf_path, backup_path)
                    logging.info(f"Backup created: {backup_path}")

                output_pdf_path = input_pdf_path if in_place else input_pdf_path.replace(".pdf", "_cleaned.pdf")
                pdf.save(output_pdf_path)
                logging.info(f"Deep cleaned PDF saved to: {output_pdf_path}")
                print(f"Processed: {output_pdf_path}")
                return

        except Exception as e:
            logging.error(f"Deep clean failed for {input_pdf_path}: {e}")
            return

    with open(input_pdf_path, 'rb') as file:
        reader = pypdf.PdfReader(file)
        metadata = reader.metadata

        # Check if metadata is empty or only has /Producer (which pypdf adds by default)
        metadata_keys = set(metadata.keys()) if metadata else set()
        metadata_needs_cleaning = metadata_keys and metadata_keys != {'/Producer'}

        if not metadata_needs_cleaning:
            logging.info(f"No removable metadata found in {input_pdf_path}. Skipping cleaning.")
            return

    if in_place:
        backup_path = input_pdf_path + ".bak"
        try:
            shutil.copy2(input_pdf_path, backup_path)
            logging.info(f"Backup created: {backup_path}")
        except Exception as e:
            logging.error(f"Failed to create backup for {input_pdf_path}: {e}")
            return

    try:
        with open(input_pdf_path, 'rb') as file:
            reader = pypdf.PdfReader(file)

            if reader.is_encrypted:
                try:
                    reader.decrypt("")
                except Exception as e:
                    logging.warning(f"Skipping encrypted PDF: {input_pdf_path} ({e})")
                    return

            writer = pypdf.PdfWriter()

            metadata = reader.metadata
            if metadata:
                logging.info(f"Original metadata for {input_pdf_path}:")
                for key, value in metadata.items():
                    logging.info(f"  {key}: {value}")
            else:
                logging.info(f"No metadata found in {input_pdf_path}.")

            for page in reader.pages:
                writer.add_page(page)

            writer.add_metadata({})
            logging.info(f"Metadata removed from {input_pdf_path}")

            output_pdf_path = input_pdf_path if in_place else input_pdf_path.replace(".pdf", "_cleaned.pdf")

            try:
                with open(output_pdf_path, 'wb') as output_file:
                    writer.write(output_file)
                    logging.info(f"Cleaned PDF saved to: {output_pdf_path}")
                    print(f"Processed: {output_pdf_path}")
            except Exception as e:
                logging.error(f"Failed to write {output_pdf_path}: {e}")

    except Exception as e:
        logging.error(f"Failed to process {input_pdf_path}: {e}")

def find_pdfs(paths, recursive=False):
    pdf_files = []
    for path in paths:
        if os.path.isfile(path) and path.lower().endswith('.pdf'):
            pdf_files.append(path)
        elif os.path.isdir(path):
            if recursive:
                for root, _, files in os.walk(path):
                    for file in files:
                        if file.lower().endswith('.pdf'):
                            pdf_files.append(os.path.join(root, file))
            else:
                logging.warning(f"Skipping directory (use -r to process): {path}")
        else:
            logging.warning(f"Path not found or not a PDF: {path}")
    return pdf_files

def main():
    parser = argparse.ArgumentParser(description="Remove metadata from PDF files.")
    parser.add_argument("paths", nargs='+', help="Path(s) to PDF file(s) or folder(s)")
    parser.add_argument("-i", "--in-place", action="store_true", help="Replace original file(s) in-place (creates .bak backups)")
    parser.add_argument("-r", "--recursive", action="store_true", help="Search directories recursively for PDF files")
    parser.add_argument("-d", "--deep-clean", action="store_true", help="Perform a deep clean using pikepdf to remove additional metadata")
    args = parser.parse_args()

    pdf_files = find_pdfs(args.paths, recursive=args.recursive)

    if not pdf_files:
        print("No PDF files found.")
        return

    for pdf_file in pdf_files:
        clean_pdf_metadata(pdf_file, in_place=args.in_place, deep_clean=args.deep_clean)


    print(f"Processed {len(pdf_files)} file(s). See 'pdf_metadata_removal.log' for details.")

if __name__ == "__main__":
    main()

