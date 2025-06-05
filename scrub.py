import sys
import os
import io
from pypdf import PdfReader, PdfWriter
from PIL import Image, UnidentifiedImageError

def strip_exif_from_image_stream(stream_data):
    try:
        img = Image.open(io.BytesIO(stream_data))
        # Create a new image without EXIF by saving freshly
        data = io.BytesIO()

        # Preserve the original format
        fmt = img.format
        if fmt not in ("JPEG", "PNG"):
            # Unsupported format for EXIF stripping; return original data
            return stream_data

        # For JPEG, save without exif by default; for PNG, just save again
        img.save(data, format=fmt)
        return data.getvalue()
    except UnidentifiedImageError:
        # Not an image or can't open; return original
        return stream_data
    except Exception as e:
        print(f"Warning: Failed to strip EXIF from image: {e}")
        return stream_data

def scrub_pdf_images_exif(input_pdf_path, output_pdf_path):
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    images_processed = 0
    images_cleaned = 0

    for page_number, page in enumerate(reader.pages, start=1):
        resources = page.get("/Resources")
        if not resources:
            writer.add_page(page)
            continue

        xobjects = resources.get("/XObject")
        if not xobjects:
            writer.add_page(page)
            continue

        xobjects_obj = xobjects.get_object()

        for name in xobjects_obj:
            obj = xobjects_obj[name]
            if obj.get("/Subtype") == "/Image":
                images_processed += 1
                try:
                    raw_data = obj.get_data()
                    cleaned_data = strip_exif_from_image_stream(raw_data)

                    if cleaned_data != raw_data:
                        # Replace image stream data with cleaned data
                        obj._data = cleaned_data
                        images_cleaned += 1
                except Exception as e:
                    print(f"Warning: Could not process image {name} on page {page_number}: {e}")

        writer.add_page(page)

    with open(output_pdf_path, "wb") as f_out:
        writer.write(f_out)

    print(f"Processed {images_processed} images; cleaned {images_cleaned} images.")
    print(f"Saved scrubbed PDF to: {output_pdf_path}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python scrub.py <input_pdf_path>")
        sys.exit(1)

    input_pdf_path = sys.argv[1]
    if not os.path.isfile(input_pdf_path):
        print(f"Error: File not found - {input_pdf_path}")
        sys.exit(1)

    base, ext = os.path.splitext(input_pdf_path)
    output_pdf_path = f"{base}_scrubbed{ext}"

    scrub_pdf_images_exif(input_pdf_path, output_pdf_path)

if __name__ == "__main__":
    main()

