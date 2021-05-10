import os
import requests
import argparse
from dotenv import load_dotenv
from urllib.parse import urlparse


def shorten_link(link, base_url, headers):
    payload = {
        'long_url': link
        }
    response = requests.post(url=base_url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()['link']


def get_info(base_url, parsed_bitlink, headers):
    url = f'{base_url}{parsed_bitlink}'
    response = requests.get(url, headers=headers)
    if response.ok:
        return response.json()['link']


def count_clicks(base_url, parsed_bitlink, headers):
    payload = {
        'unit': 'day',
        'units': '-1'
        }
    url = f'{base_url}{parsed_bitlink}/clicks/summary'
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()
    return response.json()['total_clicks']


if __name__ == '__main__':
    load_dotenv()
    parser = argparse.ArgumentParser(
        description='Программа сокращает обычные ссылки, '
                    'считает количество кликов по сокращенным ссылкам'
    )
    parser.add_argument(
        'link', help='Обычная ссылка для сокращения, '
                     'скоращенная ссылка(bit.ly) для подсчета кликов')
    args = parser.parse_args()
    link = args.link
    token = os.getenv('BITLY_KEY')
    base_url = 'https://api-ssl.bitly.com/v4/bitlinks/'
    headers = {'Authorization': f'Bearer {token}'}
    parsed = urlparse(link)
    parsed_bitlink = f'{parsed.netloc}/{parsed.path}'
    bitlink_info = get_info(base_url, parsed_bitlink, headers)

    try:
        if bitlink_info:
            clicks_count = count_clicks(base_url, parsed_bitlink, headers)
            print(f'Всего кликов по ссылке: {clicks_count} раз(а)')
        else:
            bitlink = shorten_link(link, base_url, headers)
            print(bitlink)
    except requests.exceptions.HTTPError as error:
        exit(f'Введена неправильная ссылка:\n{error}')
