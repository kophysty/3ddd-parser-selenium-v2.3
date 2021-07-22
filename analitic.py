from login import driver
from bs4 import BeautifulSoup
import json


url_models = 'https://3ddd.ru/user/models'
url_module = 'https://3ddd.ru/user/sell_rating'


def get_count_page(url):
    driver.get(url)
    html_file = driver.page_source
    soup = BeautifulSoup(html_file, "html.parser")
    count = str() # Check words in string
    try:
        count_text = soup.find('div', attrs={'class': 'count'}).text
    except Exception as exc:
        count = 1
    
    if(count != 1):
        for c in count_text:
            if c.isdigit():
                count += c

    return int(count)


def take_hrefs(url):
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    items = soup.find_all('div', attrs={'class': 'item'})

    links_items = []
    for l in items:
        if(l.find('div', attrs={'id': 'model_status'}).text == 'pro'):
            links_items.append('https://3ddd.ru/3dmodels/show/' + l['data-slug'])

    return links_items

def models_parse(url): # Read module info
    pages_count = get_count_page(url)
    hrefs = []
    for page in range(1, pages_count + 1):
        hrefs.extend(take_hrefs(url + '?page=' + str(page)))
    
    with open(f'__pycache__/earlier_sells.json') as file:
        data = json.load(file)
        data['models'] = len(hrefs)
        with open(f'__pycache__/earlier_sells.json', 'w') as file:
            json.dump(data, file)
        
    return hrefs

hrefs = models_parse(url_models)

def module_parse(url): # Read module info
    links_text = []
    driver.get(url)
    html_file2 = driver.page_source
    soup2 = BeautifulSoup(html_file2, "html.parser")
    table_sell = soup2.find('tbody')
    trs = table_sell.find_all('tr')

    models = []

    for tr in trs:
        tds = tr.find_all('td')
        models.append({'link': tds[1].find('a'), 'pcs': tds[2].text})

    for link in models:
        if(link['pcs'] != '0'):
            links_text.append(link['link']['href'])
    return links_text

links_text = module_parse(url_module)

def dict_models(hrefs):

    with open(f'__pycache__/earlier_sells.json', encoding='utf-8') as file:
        data = json.load(file)
        earlier_m = data['models_info']

    dict_m = {}
    for h in hrefs:
        if(h in earlier_m):
            dict_m[h] = earlier_m[h]
        else:
            driver.get(h)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            table = soup.find('tbody')

            dict_m[h] = {'make_data': '', 'render': '', 'size': ''}
            dict_m[h]['make_data'] = f" {table.find_all('tr')[3].find_all('td')[1].text} "
            dict_m[h]['render'] = table.find_all('tr')[1].find_all('td')[1].text
            dict_m[h]['size'] = table.find_all('tr')[2].find_all('td')[1].text

    with open(f'__pycache__/earlier_sells.json') as file:
        data = json.load(file)
        data['models_info'] = dict_m
        with open(f'__pycache__/earlier_sells.json', 'w') as file:
            json.dump(data, file)

    
    return dict_m


def sort_model(hrefs, links_clear, items): 
    links_items = {}
    for l in links_clear:
        links_items['https://3ddd.ru' + l] = (items['https://3ddd.ru' + l])
        
    print(links_items)

    with open(f'__pycache__/earlier_sells.json') as file:
        data = json.load(file)
        data['models_info'] = links_items
        with open(f'__pycache__/earlier_sells.json', 'w') as file:
            json.dump(data, file)

    return links_items

models_items = dict_models(hrefs)

model_sorted = sort_model(hrefs, links_text, models_items)

def make_models_info(models_items):
    models_info = {
        'make_data': [],
        'render': [],
        'size': []
    }

    for k in models_items:
        models_info['make_data'].append(models_items[k]['make_data'])
        models_info['render'].append(models_items[k]['render'])
        models_info['size'].append(models_items[k]['size'])

    return models_info

models_info = make_models_info(model_sorted)