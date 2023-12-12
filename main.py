import requests
from bs4 import BeautifulSoup
import json
import csv

# URL стартовой страницы с объявлениями
start_url = "https://auto.drom.ru/all/page1/?cid[]=23&cid[]=170&order=price&multiselect[]=9_4_15_all&multiselect[]=9_4_16_all&pts=2&damaged=2&unsold=1"

# заголовки для запросов
headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
}

# получаем ссылки на все страницы с объявлениями
start_req = requests.get(start_url, headers=headers)
start_src = start_req.text
start_response = requests.get(start_url)
start_soup = BeautifulSoup(start_response.text, 'html.parser')
pages = [start_url]
for pages_urls in start_soup.find_all('a', class_='css-14wh0pm e1lm3vns0'):
    pages.append(pages_urls['href'])
for i in range(2, 5):
    url = f"https://auto.drom.ru/all/page{i}/?cid[]=23&cid[]=170&order=price&multiselect[]=9_4_15_all&multiselect[]=9_4_16_all&pts=2&damaged=2&unsold=1"
    pages.append(url)

all_ads_dict = {}
for i, page in enumerate(pages):
    req = requests.get(page, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, "lxml")
    all_ads_hrefs = soup.find_all(class_=("css-xb5nz8 e1huvdhj1"))
    if not all_ads_hrefs:
        continue
    for class_ in all_ads_hrefs:
        for span in class_.find_all('span'):
            span.append(' ')
        for div in class_.find_all('div'):
            div.append(' ')

    for item in all_ads_hrefs:
        href = item.get("href")
        item_text = item.text.replace(' ', '')
        clean_href = href.strip().lower()
        if "/vladivostok/" in clean_href or "/ussuriisk/" in clean_href:  # Если в ссылке есть /vladivostok/ или /ussuriisk/, добавляем ее в словарь
            # условие для проверки наличия "в пути" внутри div
            div_tags = item.find_all('div', class_='css-1r7hfp1 ejipaoe0')
            if div_tags and "в пути" and "под заказ" and "Япония" and "Китай" not in div_tags[0].text.lower():
                continue
            span_tags = item.find_all('span', class_='css-1488ad e162wx9x0')
            if any(city.lower() in span.text.lower() for city in ["Уссурийск", "Владивосток"]):
                item_href = "h" + item.get("href")[1:]
                all_ads_dict[item_text] = item_href

# записываем данные заголовков в json файл
with open('all_ads_headers.json', 'w', encoding='utf-8') as f:
    json.dump(all_ads_dict, f, ensure_ascii=False, indent=4)


# запись данных заголовков в CSV-файл
with open("all_ads_headers.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow([" Марка авто "," Модель авто "," Год "," Комплектация "," Объём двигателя "," Мощность двигателя "," Тип топлива "," Тип коробки передач "," Привод "," Пробег "," Пробег по РФ "," Цена "," Отметка Дром'а по цене "," Город "," Дата "," Ссылка "])
    for item_text, item_href in all_ads_dict.items():
        writer.writerow([item_text, item_href])
