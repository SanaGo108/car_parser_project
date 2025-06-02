import requests
from bs4 import BeautifulSoup


def parse_avito(marka):
    url = f'https://www.avito.ru/moskva/avtomobili/{marka.lower()}'
    response = requests.get(url)

    # Для отладки выводим HTML код страницы
    print(f"Загружен URL: {url}")
    print(response.text[:500])  # Печатает первые 500 символов HTML-кода страницы

    soup = BeautifulSoup(response.text, 'html.parser')

    cars = []
    for item in soup.find_all('a', {'itemprop': 'url'}):
        # Извлекаем название и ссылку
        title = item['title'] if item.has_attr('title') else 'Без названия'
        link = f'https://www.avito.ru{item["href"]}'

        # Попробуем извлечь цену
        price = item.find_next('span', {'class': 'price-text-1Wr3W'})  # Цена после ссылки
        price = price.text.strip() if price else 'Цена не указана'

        cars.append({
            'Марка': title,
            'Цена': price,
            'Ссылка': link
        })

    print(f"Avito: Найдено {len(cars)} автомобилей для марки {marka}")
    return cars


