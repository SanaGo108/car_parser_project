import os
import pandas as pd
from parsers.avito_parser import parse_avito  # Импортируем функцию для парсинга Avito
from parsers.auto_parser import parse_auto    # Импортируем функцию для парсинга Auto.ru
from parsers.drom_parser import parse_drom    # Импортируем функцию для парсинга Drom.ru

# Функция для сохранения данных в Excel
def save_to_excel(data, filename='data/cars_data.xlsx'):
    # Проверяем, существует ли файл
    if os.path.exists(filename):
        # Если файл существует, добавляем новые данные в существующий файл
        df = pd.read_excel(filename)
        new_data = pd.DataFrame(data)
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_excel(filename, index=False)
    else:
        # Если файл не существует, создаем новый файл
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)

# Основная функция для сбора данных
def get_cars_data():
    marka = input("Введите марку автомобиля для поиска: ").strip()  # Вводим марку

    # Парсим данные с разных сайтов
    print(f"Парсим данные для марки {marka}...")
    avito_data = parse_avito(marka)  # Парсим данные с Avito
    auto_data = parse_auto(marka)    # Парсим данные с Auto.ru
    drom_data = parse_drom(marka)    # Парсим данные с Drom.ru

    # Объединяем все собранные данные
    all_cars = avito_data + auto_data + drom_data

    # Сохраняем собранные данные в Excel
    save_to_excel(all_cars)

    # Выводим собранные данные
    df = pd.DataFrame(all_cars)
    print(df)

    print(f'Данные сохранены в файл {marka}_cars_data.xlsx')

# Запуск программы
if __name__ == "__main__":
    get_cars_data()
