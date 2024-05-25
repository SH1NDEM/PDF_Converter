import os
import cv2
import fitz  # PyMuPDF
from google.oauth2 import service_account
from googleapiclient.discovery import build
import flet as ft
import threading

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

def main(page: ft.Page):
    page.title = "PDF Downloader and Processor"
    page.window_width = 340
    page.window_height = 470
    page.window_resizable = False

    def start_process(e):
        folder_id = folder_id_input.value
        cropped_images_folder = cropped_images_folder_input.value
        start_index = int(start_index_input.value)
        end_index = int(end_index_input.value)
        offset = int(offset_input.value)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        pdf_folder = os.path.join(current_dir, "downloaded_pdfs")
        converted_pdfs = os.path.join(current_dir, "Converted_pdfs")
        # ИЗМЕНИТЬ ПРИ ПЕРЕДАЧЕ
        creds_json = os.path.join(current_dir, r"C:\Users\WILLMA\Desktop\PDF_Downloader\Sources\pdf-converter-424314-8e8d5973c577.json")

        def process():
            # Clear previous messages
            page.controls.clear()
            page.update()

            page.add(ft.Text("Downloading PDFs..."))
            page.update()
            download_google_docs_as_pdfs(folder_id, pdf_folder, start_index, end_index, creds_json)

            page.controls.clear()
            page.add(ft.Text("Converting PDFs to images..."))
            page.update()
            for i in range(start_index, end_index + 1):
                pdf_file = f"{i}.pdf"
                pdf_path = os.path.join(pdf_folder, pdf_file)
                pdf_converted_folder = os.path.join(converted_pdfs, f"{i}")
                convert_pdf_to_images(pdf_path, pdf_converted_folder)

            page.controls.clear()
            page.add(ft.Text("Cropping images..."))
            page.update()
            process_images(converted_pdfs, cropped_images_folder, offset)

            page.controls.clear()
            page.add(ft.Text("Process completed."))
            page.update()

        threading.Thread(target=process).start()

    folder_id_input = ft.TextField(label="ID папки с файлами", width=300)
    cropped_images_folder_input = ft.TextField(label="Итог", width=300)
    start_index_input = ft.TextField(label="Начальный файл", width=300)
    end_index_input = ft.TextField(label="Последний файл", width=300)
    offset_input = ft.TextField(label="Отступ снизу", width=300, value="10")

    start_button = ft.ElevatedButton(text="Start Process", on_click=start_process)

    page.add(
        folder_id_input,
        cropped_images_folder_input,
        start_index_input,
        end_index_input,
        offset_input,
        start_button
    )

ft.app(target=main)
