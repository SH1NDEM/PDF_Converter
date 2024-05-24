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

    # Получить список всех файлов в папке
    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)
        if os.path.isfile(file_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            cropped_image = crop_image_by_black_border(file_path, offset)
            output_path = os.path.join(output_folder, filename)
            cv2.imwrite(output_path, cropped_image)
            print(f'Processed and saved: {output_path}')


# Указание путей к папкам
input_folder = r"C:\Users\WILLMA\Desktop\PDF_Downloader\Converted_pdfs\48"
output_folder = r"C:\Users\WILLMA\Desktop\PDF_Downloader\cut_jpgs"

# Запуск обработки изображений
process_images(input_folder, output_folder, offset=10)
