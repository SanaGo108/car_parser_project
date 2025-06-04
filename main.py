import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import json
import time
import random
import sqlite3
import asyncio
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fpdf import FPDF

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler()
    ]
)

# --- Прокси и User-Agent ---
proxies = [
    None,
    'http://123.123.123.123:8000',
    'http://234.234.234.234:8000',
    'http://345.345.345.345:8000'
]

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
]

def get_random_user_agent():
    return random.choice(user_agents)

def robust_request(url):
    for attempt, proxy in enumerate(proxies, 1):
        try:
            logging.info(f"Попытка {attempt}: запрос к {url} через прокси {proxy if proxy else 'без прокси'}")
            response = requests.get(url, headers={'User-Agent': get_random_user_agent()}, proxies={"http": proxy, "https": proxy} if proxy else None, timeout=10)
            response.raise_for_status()
            return response
        except Exception as e:
            logging.warning(f"Ошибка запроса через прокси {proxy}: {e}")
            time.sleep(2)
    logging.error(f"Не удалось получить данные с {url}")
    return None

# --- Залоговая стоимость (пример: 75% от цены) ---
def calculate_collateral(price):
    try:
        digits = ''.join(filter(str.isdigit, str(price)))
        return int(digits) * 0.75 if digits else None
    except:
        return None

# --- Сохранение данных ---
def save_to_excel(data, filename="cars_output.xlsx"):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    logging.info(f"Результаты сохранены в {filename}")

def save_to_csv(data, filename="cars_output.csv"):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    logging.info(f"Результаты сохранены в {filename}")

def save_to_pdf(data, filename="cars_output.pdf"):
    df = pd.DataFrame(data)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Отчет по автомобилям", ln=True, align='C')

    col_widths = [60, 30, 60, 30]
    cols = ["Марка", "Цена", "Ссылка", "Залоговая стоимость"]
    for i, col in enumerate(cols):
        pdf.cell(col_widths[i], 10, col, border=1)
    pdf.ln()

    for _, row in df.iterrows():
        pdf.cell(col_widths[0], 10, str(row['Марка'])[:35], border=1)
        pdf.cell(col_widths[1], 10, str(row['Цена']), border=1)
        pdf.cell(col_widths[2], 10, str(row['Ссылка'])[:35], border=1)
        pdf.cell(col_widths[3], 10, str(row['Залоговая стоимость']), border=1)
        pdf.ln()

    pdf.output(filename)
    logging.info(f"Результаты сохранены в {filename}")

def save_to_db(data, db_file="cars.db"):
    conn = sqlite3.connect(db_file)
    df = pd.DataFrame(data)
    with conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS cars (
            Марка TEXT,
            Цена TEXT,
            Ссылка TEXT,
            "Залоговая стоимость" REAL
        )
        """)
    df.to_sql("cars", conn, if_exists="append", index=False)
    conn.close()
    logging.info(f"Результаты сохранены в базу данных {db_file}")

# --- Реализация парсера Drom.ru ---
def parse_drom(marka, region):
    marka_url = marka.lower().replace(' ', '/').strip()
    region_url = f"{region}/" if region != 'all' else ''
    base_url = f"https://auto.drom.ru/{region_url}{marka_url}/"

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)

    data = []
    try:
        for page in range(1, 4):
            url = f"{base_url}?page={page}"
            logging.info(f"Открытие страницы: {url}")
            driver.get(url)
            time.sleep(random.uniform(2, 4))

            cards = driver.find_elements(By.CSS_SELECTOR, 'a.css-16z3f8k')
            if not cards:
                logging.warning(f"Drom fallback: не найдено карточек для {marka_url} на странице {page}")
                break

            for card in cards:
                try:
                    title = card.find_element(By.CSS_SELECTOR, 'div.css-16v5mdi').text
                    price = card.find_element(By.CSS_SELECTOR, 'span.css-1dv8s3l').text
                    link = card.get_attribute("href")
                    collateral = calculate_collateral(price)
                    data.append({
                        "Марка": title,
                        "Цена": price,
                        "Ссылка": link,
                        "Залоговая стоимость": collateral
                    })
                except Exception as e:
                    logging.warning(f"Ошибка при разборе карточки: {e}")

    except Exception as e:
        logging.error(f"Ошибка при парсинге Drom: {e}")
    finally:
        driver.quit()

    return data

# --- Заглушки других парсеров ---
def parse_avito(marka):
    logging.warning("Avito: заглушка парсера, не реализован")
    return []

def parse_autoru(marka):
    logging.warning("Auto.ru: заглушка Selenium парсера, не реализован")
    return []

# --- Главная точка входа ---
def main():
    marka = input("Введите марку автомобиля для поиска: ").strip()
    region = input("Введите регион (например, moscow, spb, all): ").strip().lower()
    logging.info(f"Парсим данные для {marka} в регионе {region}...")

    all_data = []

    all_data.extend(parse_avito(marka))
    all_data.extend(parse_autoru(marka))
    all_data.extend(parse_drom(marka, region))

    if all_data:
        df = pd.DataFrame(all_data)
        print(df)
        save_to_excel(all_data)
        save_to_csv(all_data)
        save_to_pdf(all_data)
        save_to_db(all_data)
    else:
        logging.warning(f"Данные по {marka} не найдены")

if __name__ == '__main__':
    main()
