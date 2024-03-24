import requests
import csv
from lxml import html

BASE_URL = 'https://www.woman.ru/forum/{}/?sort=all'


def getOrDefault(list_prop):
    if len(list_prop) == 0:
        return ""
    else:
        return list_prop[0]


def scrape_post_details(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        if response.status_code == 200:
            root = html.fromstring(response.text)
            name_list = root.xpath('//h1[@class="card__topic-title"]/text()')

            post_data = {
                'Name': getOrDefault(name_list),
            }

            return post_data
    except requests.RequestException as e:
        print(f"Ошибка при скрапинге {url}: {e}")
        return {}


def scrape_pages():
    post_data_list = []

    for i in range(1, 40):
        url = BASE_URL.format(i)
        response = requests.get(url)
        if response.status_code == 200:
            root = html.fromstring(response.text)
            post_links = root.xpath('//a[@class="list-item__link "]/@href')

            for relative_link in post_links:
                complete_url = f"https://www.woman.ru{relative_link}"
                post_data_list.append(scrape_post_details(complete_url))

    return post_data_list


def save_to_csv(data, filename):
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, keys)
        writer.writeheader()
        writer.writerows(data)


def parser():
    post_names = scrape_pages()
    save_to_csv(post_names, 'forumPostNames.csv')


if __name__ == '__main__':
    parser()
