import cv2
import os


def crop_image_by_black_border(image_path, offset=10):
    # Загрузить изображение
    image = cv2.imread(image_path)

    # Преобразовать изображение в оттенки серого
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Найти черную рамку внизу
    _, thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY_INV)

    # Найти контуры
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Найти самый нижний контур
    max_y = 0
    for contour in contours:
        _, y, _, h = cv2.boundingRect(contour)
        if y + h > max_y:
            max_y = y + h

    # Обрезать изображение с учетом отступа
    crop_y = max_y + offset
    if crop_y > image.shape[0]:
        crop_y = image.shape[0]

    cropped_image = image[:crop_y, :]

    return cropped_image


def process_images(input_folder, output_folder, offset=10):
    # Создать выходную папку, если она не существует
    os.makedirs(output_folder, exist_ok=True)

    # Обойти все вложенные папки
    for root, dirs, files in os.walk(input_folder):
        for dir_name in dirs:
            input_subfolder = os.path.join(root, dir_name)
            output_subfolder = os.path.join(output_folder, dir_name)

            # Создать выходную подпапку, если она не существует
            os.makedirs(output_subfolder, exist_ok=True)

            # Счетчик для имен файлов в каждой подпапке
            file_counter = 1

            # Получить список всех файлов в подпапке
            for filename in os.listdir(input_subfolder):
                file_path = os.path.join(input_subfolder, filename)
                if os.path.isfile(file_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    cropped_image = crop_image_by_black_border(file_path, offset)
                    output_filename = f"{file_counter}.jpg"
                    output_path = os.path.join(output_subfolder, output_filename)
                    cv2.imwrite(output_path, cropped_image)
                    print(f'Processed and saved: {output_path}')
                    file_counter += 1


# Указание путей к папкам
input_folder = r"C:\Users\WILLMA\Desktop\PDF_Downloader\Converted_pdfs"  # Путь к папке с PDF-файлами
output_folder = r"C:\Users\WILLMA\Desktop\PDF_Downloader\cut_jpgs"  # Путь к папке для сохранения изображений

# Запуск обработки изображений
process_images(input_folder, output_folder, offset=10)
