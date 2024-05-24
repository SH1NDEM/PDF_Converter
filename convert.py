import fitz  # PyMuPDF
import os

def convert_pdf_to_images(pdf_path, output_folder):
    print(f"Converting PDF to images: {pdf_path}")
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]

    # Проверка существования папки, если нет - создать
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    pdf = fitz.open(pdf_path)
    for page_num in range(pdf.page_count):
        page = pdf.load_page(page_num)
        image = page.get_pixmap()
        image_path = os.path.join(output_folder, f"{pdf_name}_page_{page_num + 1}.jpg")
        image.save(image_path)

# Пример использования:
pdf_path = r"C:\Users\WILLMA\Desktop\PDF_Downloader\downloaded_pdfs\48.pdf"
output_folder = r"C:\Users\WILLMA\Desktop\PDF_Downloader\Converted_pdfs\48"
convert_pdf_to_images(pdf_path, output_folder)
