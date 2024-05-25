import fitz  # PyMuPDF
import os

def convert_pdf_to_images(pdf_path, output_folder):
    if not os.path.isfile(pdf_path):
        print(f"File does not exist: {pdf_path}")
        return

    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]

    # Проверка существования папки, если нет - создать
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    print(f"Converting PDF to images: {pdf_path}")

    pdf = fitz.open(pdf_path)

    for page_num in range(pdf.page_count):
        page = pdf.load_page(page_num)
        image = page.get_pixmap()
        image_path = os.path.join(output_folder, f"{pdf_name}_page_{page_num + 1}.jpg")
        image.save(image_path)

    pdf.close()

# Пример использования
pdf_folder = r"C:\Users\WILLMA\Desktop\PDF_Downloader\downloaded_pdfs"  # Путь к папке с PDF-файлами
output_base_folder = r"C:\Users\WILLMA\Desktop\PDF_Downloader\Converted_pdfs"  # Путь к папке для сохранения изображений
start_number = 349  # Начальный номер файла
end_number = 415  # Конечный номер файла

for i in range(start_number, end_number + 1):
    pdf_file = f"{i}.pdf"
    pdf_path = os.path.join(pdf_folder, pdf_file)
    output_folder = os.path.join(output_base_folder, f"{i}")  # Папка для сохранения изображений
    convert_pdf_to_images(pdf_path, output_folder)
