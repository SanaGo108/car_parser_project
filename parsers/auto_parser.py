import requests
from bs4 import BeautifulSoup


def parse_auto(marka):
    url = f'https://auto.ru/cars/all/{marka.lower()}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    cars = []
    for item in soup.find_all('div', {'class': 'ListingItem__content'}):
        title = item.find('a', {'class': 'Link Link_theme_blue'})
        price = item.find('div', {'class': 'ListingItemPrice__price'})

        if title and price:
            cars.append({
                'Марка': title.text.strip(),
                'Цена': price.text.strip(),
                'Ссылка': f'https://auto.ru{title["href"]}'
            })

    print(f"Auto.ru: Найдено {len(cars)} автомобилей для марки {marka}")
    return cars
