import os
import json
from docx_parser import DocumentParser
from docx import Document

# Основной метод для извлечения текста из документа
def extract_text_from_docx(file_path):
    try:
        doc = Document(file_path)
        text_data = []

        # Извлекаем текст из параграфов
        for para in doc.paragraphs:
            para_text = para.text.strip()
            if para_text:
                text_data.append(para_text)

        # Извлекаем текст из таблиц
        table_data = extract_table_data(file_path)  # Используем второй метод для таблиц
        for table_row in table_data:
            text_data.append(" | ".join(table_row))  # Склеиваем данные ячеек таблицы

        # Объединяем все извлеченные данные в одну строку
        merge_text = " ".join(text_data)
        return merge_text

    except Exception as e:
        print(f"Ошибка при обработке {os.path.basename(file_path)}: {e}")
        return []

# Метод для извлечения данных из таблиц
def extract_table_data(docx_path):
    doc = Document(docx_path)
    table_data = []

    # Проходим по всем таблицам в документе
    for table in doc.tables:
        for row in table.rows:
            row_data = []

            for idx, cell in enumerate(row.cells):
                cell_text = cell.text.strip()

                # Если в ячейке несколько строк, например, во втором столбце
                if '\n' in cell_text:
                    # Разделяем строки по символу новой строки
                    cell_text = " ".join(cell_text.split('\n')).strip()

                row_data.append(cell_text)

            table_data.append(row_data)

    return table_data

def process_docx_directory(directory_path):
    result = {}

    # Ищем все DOCX файлы
    docx_files = [f for f in os.listdir(directory_path)
                  if f.lower().endswith('.docx')]

    for filename in docx_files:
        file_path = os.path.join(directory_path, filename)
        print(f"Обрабатывается: {filename}")

        # Извлекаем текст
        text_content = extract_text_from_docx(file_path)
        result[filename] = text_content

    return result


if __name__ == "__main__":
    directory_path = r'C:\Users\Евгения\OneDrive\Desktop\downloaded_files'

    output_json = r'C:\Users\Евгения\OneDrive\Desktop\Универ\Курсовая\scrapy_parse\out_spider\out_spider\spiders\parsed_docx.json'

    text_data = process_docx_directory(directory_path)

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(text_data, f, ensure_ascii=False, indent=2)

    # Статистика
    total_files = len(text_data)
    total_text_elements = sum(len(texts) for texts in text_data.values())
    print(f"Обработано файлов: {total_files}")
    print(f"Всего текстовых элементов: {total_text_elements}")