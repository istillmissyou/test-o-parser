import logging
import random
import re
from itertools import islice
from time import sleep
from urllib.parse import urlparse

import redis
from bs4 import BeautifulSoup
from celery import shared_task
from selenium import webdriver
from test_o_parser.settings import (PARSE_URL, PARSER_SLEEP_TIME, REDIS_HOST,
                                    REDIS_PASSWORD, REDIS_PORT)

from .models import Product
from .tg_report import tg_report

logging.basicConfig(level=logging.INFO, format='%(levelname)s: [%(asctime)s]    %(message)s')
logger = logging.getLogger('parser_ozon')

r = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    charset='utf-8',
    decode_responses=True
)


class Parse:
    def __init__(self, URL, SLEEP_TIME: int):
        if 'ozon.ru' not in URL:
            raise ValueError('Парсер предназначен только для ozon.ru')

        self.URL = URL
        self.SLEEP_TIME = SLEEP_TIME
        self.result = []

    def open_page(self, url, driver: webdriver.Firefox):
        driver.get(url)
        sleep(random.choice(range(7, self.SLEEP_TIME)))
        return {'source': driver.page_source, 'url': url}
    
    @staticmethod
    def is_valid_url(url):
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)
    
    def parse_product(self, item, driver: webdriver.Firefox):
        try:
            name = item.find('span', {'class': 'tsBody500Medium'}).get_text(strip=True)
            product_url = 'https://www.ozon.ru'+item.find('a')['href']
            image_url = item.find('img', {'class': 'c9-a'})['src']

            if not self.is_valid_url(product_url) or not self.is_valid_url(image_url):
                logger.error(f'Некорректный URL. Ссылка на продукт: {product_url}, на картинку: {image_url}')
                return None

            html = self.open_page(product_url, driver)
            soup = BeautifulSoup(html['source'], 'lxml')
            description = soup.find('div', id='section-description')
            description_text = description.get_text(strip=True).replace("Описание", "", 1)
            product_code = int(''.join([i for i in soup.find('span', attrs={'data-widget': 'webDetailSKU'}).get_text(strip=True) if i.isdigit()]))
            new_price, old_price = [int(number.replace(' ', '')) for number in re.findall(r'\b[\d\s]+\b', soup.find('div', attrs={'data-widget': 'webPrice'}).get_text().replace('\u2009', ' '))]


            return {'name': name, 'description': description_text, 'new_price': new_price, 'old_price': old_price, 'product_url': product_url, 'image_url': image_url, 'product_code': product_code}
        except Exception as e:
            logger.error('Ошибка при парсинге озон: ', exc_info=e)
            return None

    def parse(self, products_count):
        with webdriver.Firefox() as driver:
            html = self.open_page(self.URL, driver)
            soup = BeautifulSoup(html['source'], 'lxml')

            items = [div for div in soup.find('div', attrs={'data-widget': 'searchResultsV2'}).find('div').children if div.name == 'div']

            if len(items) < products_count:
                html = self.open_page(self.URL + '?page=2', driver)
                soup = BeautifulSoup(html['source'], 'lxml')

                items += [div for div in soup.find('div', attrs={'data-widget': 'searchResultsV2'}).find('div').children if div.name == 'div']

            logger.info(f'Найдено товаров: {len(items)}')

            for item in islice(items, products_count):
                product = self.parse_product(item, driver)
                if product:
                    print(product)
                    self.result.append(product)

            if not self.result:
                logger.info('Не получилось спарсить товары')


@shared_task
def parser_ozon(products_count: int):
    logger.info(f'Начался парсинг озона на {products_count} товаров')
    parser = Parse(PARSE_URL, PARSER_SLEEP_TIME)
    parser.parse(products_count)

    products_to_update = []
    products_created_count = 0

    parser_result = parser.result
    for item in parser_result:
        name, description, new_price, old_price, url, image_url, product_code = item.values()
        try:
            product, created = Product.objects.get_or_create(product_code=product_code,
                defaults={'name': name, 'description':description, 'new_price': new_price, 'old_price': old_price, 'image_url': image_url, 'url': url})
            if created:
                logger.debug(f'Добавлен товар: {name} ({url})')
                products_created_count += 1
            elif (product.new_price != new_price):
                    product.name = name
                    product.description = description
                    product.new_price = new_price
                    product.old_price = old_price
                    product.image_url = image_url
                    products_to_update.append(product)
                    logger.debug(f'Цены обновлены для товара: {name} ({url})')
            else:
                logger.debug(f'Цены не изменились для товара: {name} ({url})')
        except Exception as e:
            logger.error(f'Ошибка при сохранении товара: {name} ({url})', exc_info=e)
            continue

    logger.info('Новых товаров нет') if products_created_count == 0 else logger.info(f'Добавлено товаров: {products_created_count}')

    if products_to_update:
        Product.objects.bulk_update(products_to_update, ['name', 'description', 'new_price', 'old_price', 'image_url', 'url'])
        logger.info(f'Обновилось товаров: {len(products_to_update)}')

    result_for_cache = ''
    for i, d in enumerate(parser_result, start=1):
        result_for_cache += f"{i}. {d['name']} {d['product_url']}\n"
    
    r.set('last_parsing', result_for_cache)

    tg_report(f'Задача на парсинг товаров с сайта Ozon завершена.\nСохранено: {len(parser_result)} товаров.')
