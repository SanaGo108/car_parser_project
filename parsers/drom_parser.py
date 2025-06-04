import requests
from bs4 import BeautifulSoup


def parse_drom(marka):
    url = f'https://www.drom.ru/{marka.lower()}/'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка на успешный ответ
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении данных с {url}: {e}")
        return []  # Возвращаем пустой список в случае ошибки

    soup = BeautifulSoup(response.text, 'html.parser')

    cars = []
    # Находим все ссылки на автомобили
    for item in soup.find_all('a', href=True):
        # Ищем только те ссылки, которые ведут на страницы с автомобилями
        if 'auto.drom.ru' in item['href']:
            title = item.find('img')['alt'] if item.find(
                'img') else 'Без названия'  # Название из alt атрибута изображения
            link = f'https://auto.drom.ru{item["href"]}'  # Полная ссылка на страницу автомобиля

            # Цена автомобиля - поиск ближайшего элемента с ценой
            price_element = item.find_next('div', {'class': 'css-ac6cb6'})  # Используем класс для поиска цены
            price = price_element.text.strip() if price_element else 'Цена не указана'

            # Добавляем автомобиль в список
            cars.append({
                'Марка': title,
                'Цена': price,
                'Ссылка': link
            })

    print(f"Drom.ru: Найдено {len(cars)} автомобилей для марки {marka}")
    return cars
