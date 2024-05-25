import os
import cv2
import fitz  # PyMuPDF
from google.oauth2 import service_account
from googleapiclient.discovery import build

def get_google_docs_ids(folder_id, creds_json):
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = service_account.Credentials.from_service_account_file(creds_json, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)

    file_ids = []
    page_token = None

    while True:
        response = service.files().list(q=f"'{folder_id}' in parents",
                                        spaces='drive',
                                        fields='nextPageToken, files(id, name)',
                                        pageToken=page_token).execute()

        for file in response.get('files', []):
            file_ids.append((file['id'], file['name']))

        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break

    return file_ids

def download_google_docs_as_pdfs(folder_id, download_folder, start_index, end_index, creds_json):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    file_ids = get_google_docs_ids(folder_id, creds_json)

    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    creds = service_account.Credentials.from_service_account_file(creds_json, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)

    for file_id, file_name in file_ids:
        try:
            file_number = int(file_name.split('.')[0])
            if start_index <= file_number <= end_index:
                request = service.files().export_media(fileId=file_id, mimeType='application/pdf')
                file_path = os.path.join(download_folder, f"{file_number}.pdf")

                with open(file_path, 'wb') as f:
                    f.write(request.execute())

                print(f"Downloaded {file_path}")
        except ValueError:
            # Имя файла не начинается с числа, игнорируем его
            continue

def convert_pdf_to_images(pdf_path, Converted_pdfs):
    if not os.path.isfile(pdf_path):
        print(f"File does not exist: {pdf_path}")
        return

    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]

    if not os.path.exists(Converted_pdfs):
        os.makedirs(Converted_pdfs)

    print(f"Converting PDF to images: {pdf_path}")

    pdf = fitz.open(pdf_path)

    for page_num in range(pdf.page_count):
        page = pdf.load_page(page_num)
        image = page.get_pixmap()
        image_path = os.path.join(Converted_pdfs, f"{pdf_name}_page_{page_num + 1}.jpg")
        image.save(image_path)

    pdf.close()

def crop_image_by_black_border(image_path, offset=10):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    max_y = 0
    for contour in contours:
        _, y, _, h = cv2.boundingRect(contour)
        if y + h > max_y:
            max_y = y + h

    crop_y = max_y + offset
    if crop_y > image.shape[0]:
        crop_y = image.shape[0]

    cropped_image = image[:crop_y, :]
    return cropped_image

def process_images(input_folder, output_folder, offset=10):
    os.makedirs(output_folder, exist_ok=True)

    for root, dirs, files in os.walk(input_folder):
        for dir_name in dirs:
            input_subfolder = os.path.join(root, dir_name)
            output_subfolder = os.path.join(output_folder, dir_name)

            os.makedirs(output_subfolder, exist_ok=True)

            file_counter = 1
            for filename in os.listdir(input_subfolder):
                file_path = os.path.join(input_subfolder, filename)
                if os.path.isfile(file_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    cropped_image = crop_image_by_black_border(file_path, offset)
                    output_filename = f"{file_counter}.jpg"
                    output_path = os.path.join(output_subfolder, output_filename)
                    cv2.imwrite(output_path, cropped_image)
                    print(f'Processed and saved: {output_path}')
                    file_counter += 1

# Пути:
folder_id = '13AqHYhJVZNuzJQN8M6UNnjExM1zMVl6a'
pdf_folder = r"C:\Users\WILLMA\Desktop\PDF_Downloader\downloaded_pdfs"
Converted_pdfs = r"C:\Users\WILLMA\Desktop\PDF_Downloader\Converted_pdfs"
cut_jpgs = r"C:\Users\WILLMA\Desktop\PDF_Downloader\Cropped"
creds_json = r"C:\Users\WILLMA\Desktop\PDF_Downloader\Sources\pdf-converter-424314-8e8d5973c577.json"

start_index = 48
end_index = 50

# Загрузка файлов Google Docs в PDF
download_google_docs_as_pdfs(folder_id, pdf_folder, start_index, end_index, creds_json)

# Конвертация PDF в изображения
for i in range(start_index, end_index + 1):
    pdf_file = f"{i}.pdf"
    pdf_path = os.path.join(pdf_folder, pdf_file)
    pdf_converted_folder = os.path.join(Converted_pdfs, f"{i}")
    convert_pdf_to_images(pdf_path, pdf_converted_folder)

# Обрезка изображений
process_images(Converted_pdfs, cut_jpgs, offset=10)
