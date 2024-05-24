import os
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

def download_google_docs_as_pdfs(folder_id, destination_folder, start_index, end_index, creds_json):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    file_ids = get_google_docs_ids(folder_id, creds_json)

    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    creds = service_account.Credentials.from_service_account_file(creds_json, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)

    for file_id, file_name in file_ids:
        try:
            file_number = int(file_name.split('.')[0])
            if start_index <= file_number <= end_index:
                request = service.files().export_media(fileId=file_id, mimeType='application/pdf')
                file_path = os.path.join(destination_folder, f"{file_name}.pdf")

                with open(file_path, 'wb') as f:
                    f.write(request.execute())

                print(f"Downloaded {file_path}")
        except ValueError:
            # Имя файла не начинается с числа, игнорируем его
            continue

# Пример использования:
folder_id = '13AqHYhJVZNuzJQN8M6UNnjExM1zMVl6a'
destination_folder = r"C:\Users\WILLMA\Desktop\PDF_Downloader\downloaded_pdfs"
start_index = 48  # Начальный индекс
end_index = 50  # Конечный индекс
creds_json = r"C:\Users\WILLMA\Desktop\PDF_Downloader\Sources\pdf-converter-424314-8e8d5973c577.json"
download_google_docs_as_pdfs(folder_id, destination_folder, start_index, end_index, creds_json)

