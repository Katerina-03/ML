import requests
import csv
from lxml import html
import datetime

BASE_URL = "https://spb.cian.ru/cat.php?deal_type=sale&engine_version=2&object_type%5B0%5D=2&offer_type=flat&p="


def getOrDefault(list_prop):
    if len(list_prop) == 0:
        return ""
    else:
        return list_prop[0]


def scrape_flat_details(url):
    response = requests.get(url)
    if response.status_code == 200:
        root = html.fromstring(response.text)

        name_list = root.xpath('//a[@class="a10a3f92e9--link--A5SdC"]/text()')
        geo_list = root.xpath('//div[@class="a10a3f92e9--header-information--w7fS9"]/div[2]/span[1]/@content')
        house_type_list = root.xpath("//div[@class='a10a3f92e9--item--qJhdR']/span[2]/text()")
        rooms_list = root.xpath('//div[@class="a10a3f92e9--header-information--w7fS9"]/div[1]/h1[1]/text()')
        rooms_list_cleaned = [room.split(',')[0].strip() for room in rooms_list]
        squares_list = root.xpath("//div[@class='a10a3f92e9--container--tqDAE']/div[1]/div[2]/span[2]/text()")
        squares_list_cleaned = [square.replace('\xa0', ' ').replace('м²', '') for square in squares_list]
        metro_list = root.xpath('//a[@class="a10a3f92e9--underground_link--VnUVj"]/text()')
        time_to_metro_list = root.xpath('//span[@class="a10a3f92e9--underground_time--YvrcI"]/text()')
        time_to_metro_list_cleaned = [time.replace('мин.', '') for time in time_to_metro_list]
        price_list = root.xpath("//div[@class ='a10a3f92e9--amount--ON6i1']/span[1]/text()")
        price_list_cleaned = [price.replace('\xa0', ' ').replace('₽', '') for price in price_list]
        data_list = root.xpath("//div[@class='a10a3f92e9--added--Xx8oJ']/span/text()")
        data_list_cleaned = []
        for data in data_list:
            data = data.replace('Обновлено: ', '')
            data = data.split(',')[0].strip()
            data = data.replace('сегодня', datetime.datetime.now().strftime('%d.%m'))
            data = data.replace('вчера', (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%d.%m'))
            data = data.strip().replace('сен', '09').replace('окт', '10').replace(' ', '.')
            day, month = data.split('.')
            day = day.zfill(2)
            data = f"{day}.{month}"
            data_list_cleaned.append(data)

        flat_data = {
            'Name complex': getOrDefault(name_list),
            'Geo': getOrDefault(geo_list),
            'State of house': getOrDefault(house_type_list),
            'Rooms amount': getOrDefault(rooms_list_cleaned),
            'Squares,м²': getOrDefault(squares_list_cleaned),
            'Metro': getOrDefault(metro_list),
            'Time to metro,мин.': getOrDefault(time_to_metro_list_cleaned),
            'Price,₽': getOrDefault(price_list_cleaned),
            'Data': getOrDefault(data_list_cleaned)
        }

        return flat_data


def scrape_pages():
    flats_data_list = []

    for i in range(1, 54):
        url = BASE_URL + str(i) + "&region=2"
        response = requests.get(url)
        if response.status_code == 200:
            root = html.fromstring(response.text)
            flat_links = root.xpath('//a[@class="_93444fe79c--media--9P6wN"]/@href')

            for link in flat_links:
                flats_data_list.append(scrape_flat_details(link))

    return flats_data_list


def save_to_csv(data, filename):
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, keys)
        writer.writeheader()
        writer.writerows(data)


def main():
    dataset = scrape_pages()
    save_to_csv(dataset, 'flatsDataset.csv')


if __name__ == '__main__':
    main()
