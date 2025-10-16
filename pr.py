import requests
from bs4 import BeautifulSoup as BS
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import time
from datetime import datetime
import random

url = 'https://example.com'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Referer': 'https://www.amazon.com/'
}
# r = requests.get(url, headers=headers)

driver = webdriver.Chrome()

data = {'Название': [], 'рейтинг товара': [], 'Ссылка на товар': [], 'Дата парсинга страницы': [], 'Время парсинга страницы': []}
df = pd.DataFrame(data)
wait = WebDriverWait(driver, 10)

seen_urls = set()  # множество для отслеживания уже добавленных ссылок

for i in range (1, 20):
    session = requests.Session()
    resp = session.get(f"https://www.amazon.com/s?i=garden&rh=n%3A510106&s=popularity-rank&fs=true&page={i}&xpid", headers=headers)
    time.sleep(random.randint(30, 60))
    # провека стат ответа
    if resp.status_code == 200:
        print('сраница получена')
    else:
        print(f'ошибка: {resp.status_code}')
        continue

    # получаем html код страницы
    html_content = resp.text
    soup = BS(html_content, 'html.parser')
    # поиск всех объяв 
    boats = soup.find_all('div', class_="sg-col-inner")
    # print(boats)

    for boat in boats:
        # название
        title_tag = boat.find('h2', class_="a-size-base-plus a-spacing-none a-color-base a-text-normal")
        if title_tag is not None:
            span_tag = title_tag.find('span')
            if span_tag is not None and span_tag.text.strip():
                title = span_tag.text.strip()
            else:
                title = 'название не найдено'
        else:
            title  = 'название не найдено'
            
        # рейтинг товара
        reit_tag = boat.find('div', class_="a-row a-size-small")
        if reit_tag is not None:
            span_tag = reit_tag.find('span')
            if span_tag is not None and span_tag.text.strip():
                reit = span_tag.text.strip() + ' звезд'
            else:
                reit = 'рейтинг не найден'
        else:
            reit  = 'рейтинг не найден'
                
        # ссылка на товар
        tag = boat.find('a', class_="a-link-normal s-line-clamp-4 s-link-style a-text-normal")
        if tag is not None and tag.get('href'):
            url_tag = tag['href']
            if url_tag:
                url_tovar = url_tag if not url_tag.startswith('/') else 'https://www.amazon.com' + url_tag
            else:
                url_tovar = 'ссылка не найдена'
        else:
            url_tovar  = 'ссылка не найдена'
        
        # проверяем дубли по ссылке: если ссылка уже была — пропускаем
        dedup_key = url_tovar
        if dedup_key in seen_urls:
            continue
        seen_urls.add(dedup_key)
        
        if title != 'название не найдено' and reit != 'рейтинг не найден' and url_tovar != 'ссылка не найдена':
            df.loc[len(df.index)] = [title, reit, url_tovar, datetime.now().date(), datetime.now().time()] 

    print('идет обработка')
    df.to_csv('ob.csv', index = True, index_label='№')
    print('объявления : ' ,len(boats) ) # колво объяв

driver.quit()
