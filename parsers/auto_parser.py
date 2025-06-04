import requests
from bs4 import BeautifulSoup


def parse_auto(marka):
    url = f'https://auto.ru/cars/all/{marka.lower()}'
    response = requests.get(url)

    # Для отладки выводим URL и первые 500 символов HTML-кода страницы
    print(f"Загружен URL: {url}")
    print(response.text[:500])  # Печатает первые 500 символов HTML-кода страницы

    soup = BeautifulSoup(response.text, 'html.parser')

    cars = []
    for item in soup.find_all('a', {'class': 'Link ListingItemTitle__link'}):
        # Извлекаем название и ссылку
        title = item.text.strip()  # Название автомобиля внутри тега <a>
        link = item['href']
        full_link = f'https://auto.ru{link}'  # Формируем полную ссылку на страницу автомобиля

        # Извлекаем цену автомобиля
        price_element = item.find_next('div', {'class': 'ListingItemPrice__price'})
        price = price_element.text.strip() if price_element else 'Цена не указана'

        # Добавляем данные в список
        cars.append({
            'Марка': title,
            'Цена': price,
            'Ссылка': full_link
        })

    print(f"Auto.ru: Найдено {len(cars)} автомобилей для марки {marka}")
    return cars

