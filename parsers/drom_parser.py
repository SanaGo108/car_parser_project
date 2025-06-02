import requests
from bs4 import BeautifulSoup


def parse_drom(marka):
    url = f'https://www.drom.ru/{marka.lower()}/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    cars = []
    for item in soup.find_all('div', {'class': 'b-card__inner'}):
        title = item.find('a', {'class': 'b-card__title'})
        price = item.find('div', {'class': 'b-card__price'})

        if title and price:
            cars.append({
                'Марка': title.text.strip(),
                'Цена': price.text.strip(),
                'Ссылка': f'https://www.drom.ru{title["href"]}'
            })

    print(f"Drom.ru: Найдено {len(cars)} автомобилей для марки {marka}")
    return cars
