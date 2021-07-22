import login as l
import json
from selenium import webdriver

import analitic as a

from bs4 import BeautifulSoup
import copy
import csv
import os
import datetime


date_now = datetime.datetime.now().strftime('%d.%m.%y')
url_table = 'https://3ddd.ru/user/income_new'
url_module = 'https://3ddd.ru/user/sell_rating'
url_e_sells = 'https://3ddd.ru/user/withdraw_history'

def earlier_links(url): # Get Earlier sells linksW
    links = []
    l.driver.get(url)
    html = l.driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find('tbody')
    trs = table.find_all('tr')
    for t in trs:
        tds = t.find_all('td')
        if(tds[4].find('span').text == 'Выплачено'):
            links.append('https://3ddd.ru' + tds[1].find('a')['href'])
    
    print(links)

    return links

earl_arr_links = earlier_links(url_e_sells)

def get_count_page(url):
    l.driver.get(url)
    html_file = l.driver.page_source
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

def earlier_check(file, len):
    with open(f'__pycache__/{file}') as file:
        data = json.load(file)
        len_b = data['earlier_len']
        data['earlier_len'] = len
        print(data)
        
        with open(f'__pycache__/earlier_sells.json', 'w') as file:
            json.dump(data, file, indent=3)

    return (len - int(len_b))

len_earlier = earlier_check('earlier_sells.json', len(earl_arr_links))

def table_url(url, url_arr): # Parse income table
    trs = {'new': [], 'old': []}
    arr = [url] + url_arr
    print(arr)
    for u in range((len_earlier + 1)):
        print(arr[u])
        pages_count = get_count_page(arr[u])
        for page in range(1, (pages_count + 1)):
            # print(f'Парсинг страницы {page} из {pages_count}...')
            if(u == 0):
                l.driver.get(arr[u] + '?page=' + str(page))
            else:
                l.driver.get(arr[u])
            html = l.driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            table = soup.find('tbody')
            trs_one = table.find_all('tr')
            if(u == 0):
                trs['new'].extend(trs_one)
            else:
                trs['old'].extend(trs_one)
    return trs

trs = table_url(url_table, earl_arr_links)

def module_parse(url): # Read module info
    l.driver.get(url)
    html_file2 = l.driver.page_source
    soup2 = BeautifulSoup(html_file2, "html.parser")
    table_sell = soup2.find('tbody')
    links = table_sell.find_all('a')
    links_text = {'strip': [], 'link': []}
    for link in links:
        links_text['strip'].append(link.text.replace('\n', '').strip())
        links_text['link'].append(link['href'])

    return links_text
module_parse_result = module_parse(url_module)

links_text = module_parse_result['strip']
links_clear = module_parse_result['link']


def default_array(links): # Make default models array

    def_array = []
    for m in links:
        def_array.append({
            'name': m,
            'sum': 0, 
            'multi': 0,
            '3dsky': 0,
            '3ddd': 0,
            '3dsky_sum': 0,
            '3ddd_sum': 0,
        })
    return def_array

def_array = default_array(links_text)

def trs_dicts(trs_write):
    dict_info = [] # All dicts tr

    for tr in trs_write: # Run to all trs
        tds = tr.find_all('td') # Finding tds in tr
        date_in = tds[0].text #find date
        model = tds[1].text #find model
        money = tds[2].text #find money

        b = str() # Check words in string
        for c in money:
            if c == ' ':
                money = b
                break
            if c.isdigit() or c == '.':
                b += c

    
        date_have = {'nohave': True}

        i = 0
        j = 0

        while i < len(dict_info):
            if(dict_info[i]['data'] == date_in): 
                date_have['nohave'] = False
                while j < len(dict_info[i]['models']):
                    if(dict_info[i]['models'][j]['name'] == model):
                        dict_info[i]['models'][j]['sum'] += int(float(money))
                        dict_info[i]['models'][j]['multi'] += 1
                        if(float(money) > 100):
                            dict_info[i]['models'][j]['3dsky'] += 1
                            dict_info[i]['models'][j]['3dsky_sum'] += int(float(money))
                        else:
                            dict_info[i]['models'][j]['3ddd'] += 1
                            dict_info[i]['models'][j]['3ddd_sum'] += int(float(money))
                    j+=1
            i+=1

        if(date_have['nohave'] == True):
            dict_tr = {
                'data': date_in,
                'models': copy.deepcopy(def_array)
            }

            for d in dict_tr['models']:
                if(d['name'] == model):
                    d['sum'] += float(money)
                    d['multi'] += 1
                    if(float(money) > 100):
                        d['3dsky'] += 1
                        d['3dsky_sum'] += int(float(money))
                    else:
                        d['3ddd'] += 1
                        d['3ddd_sum'] += int(float(money))
            
            dict_info.append(dict_tr)

    return dict_info

trs_dict = trs_dicts(trs['new'])
trs_dict_old = trs_dicts(trs['old'])

trs_dict_nt = trs_dicts(trs['new'])

def earlier_check(file, array):
    with open(f'__pycache__/{file}') as file:
        data = json.load(file)
        data['array_sells'].extend(array)
        
        with open(f'__pycache__/earlier_sells.json', 'w') as file:
            json.dump(data, file)
    return data['array_sells']

trs_dict_old = earlier_check('earlier_sells.json', trs_dict_old)

def count_m(items):
    model_sum = [0] * len(links_text)
    model_average = []

    days_sum = len(items)

    for i in items:
        j = 0
        while j < len(i['models']):
            model_sum[j] += int(i['models'][j]['sum'])
            j+=1
    
    for m in model_sum:
        model_average.append(int(m / days_sum))

    return {'model_sum': model_sum, 'model_average': model_average, 'days_sum': days_sum}

count_models = count_m(trs_dict + trs_dict_old)


def money_average(url, model_sum): # Find money_average
    l.driver.get(url)
    html_file = l.driver.page_source
    soup = BeautifulSoup(html_file, "html.parser")
    table_sell = soup.find('tbody')
    trs = table_sell.find_all('tr')
    model_m = {'model_sells': [], 'money_average': [], 'sum_day': [], 'total_sells': [], 'grand_total': [0]}
    for s in trs:
        model_m['model_sells'].append(int(s.find_all('td')[2].text))
    l.driver.get('https://3ddd.ru/user/withdraw_history')
    html_file2 = l.driver.page_source
    soup2 = BeautifulSoup(html_file2, "html.parser")
    money = soup2.find('div', attrs={'class': 'total_price'}).text
    money_int = ''

    with open('__pycache__/earlier_sells.json') as file:
        data = json.load(file)
        earlier_sells = count_models['model_sum']

        days_dif = []

        for d in range(len(a.models_info['make_data'])):

            make_date = a.models_info['make_data'][d]
            print(make_date)
            last_date = trs_dict_nt[0]

            f_date = datetime.date(int(make_date[1:5]), int(make_date[6:8]), int(make_date[9:11]))
            l_date = datetime.date(int(last_date['data'][6:10]), int(last_date['data'][3:5]), int(last_date['data'][0:2]))
            
            days = l_date - f_date
            print(days)
            days_str = str(days)

            days_dif.append(days_str.split()[0])
        
        for d in range(len(days_dif)):
                mon_average = int(((int(model_sum['model_sum'][d]))) / int(days_dif[d]))
                model_m['sum_day'].append(mon_average)
        
        for d in range(len(model_m['model_sells'])):
                model_m['total_sells'].append(model_sum['model_sum'][d])

        for s in model_m['total_sells']:
            model_m['grand_total'][0] += int(s)

    return model_m

def ratio_sites(items, links_text):
    ratio_dict = {}
    for l in links_text:
        ratio_dict[l] = {'3ddd': 0, '3dsky': 0, '3ddd_sum': 0, '3dsky_sum': 0}
        for i in items:
            for model in i['models']:
                if(model['name'] == l):
                    ratio_dict[l]['3ddd'] += model['3ddd']
                    ratio_dict[l]['3dsky'] += model['3dsky']
                    ratio_dict[l]['3ddd_sum'] += model['3ddd_sum']
                    ratio_dict[l]['3dsky_sum'] += model['3dsky_sum']
    return ratio_dict

ratio = ratio_sites((trs_dict + trs_dict_old), links_text)
print(ratio)

def make_csv(new_items, old_items, path, model_m, ratio_sells):
    items = new_items + old_items

    with open(path, 'w', encoding='utf-8-sig', newline='') as file:
        ru_procent_count = []
        en_procent_count = [] 
        ru_procent_money = []
        en_procent_money = [] 
        ru_count = []
        en_count = []
        ru_money = []
        en_money = []
        
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['names'] + links_text)
        writer.writerow(['make_data'] + a.models_info['make_data'])
        writer.writerow(['render'] + a.models_info['render'])
        writer.writerow(['size'] + a.models_info['size'])
        writer.writerow([''])
        writer.writerow(['sales_pcs'] + model_m['model_sells'])


        for sell in ratio_sells:
            sum_count = ratio_sells[sell]['3ddd'] + ratio_sells[sell]['3dsky']
            sum_money = ratio_sells[sell]['3ddd_sum'] + ratio_sells[sell]['3dsky_sum']

            ru_procent_count.append(str(int(ratio_sells[sell]['3ddd'] / sum_count * 100)) + '%')
            en_procent_count.append(str(int(ratio_sells[sell]['3dsky'] / sum_count * 100)) + '%')
            ru_procent_money.append(str(int(ratio_sells[sell]['3ddd_sum'] / sum_money * 100)) + '%')
            en_procent_money.append(str(int(ratio_sells[sell]['3dsky_sum'] / sum_money * 100)) + '%')
            ru_count.append(ratio_sells[sell]['3ddd'])
            en_count.append(ratio_sells[sell]['3dsky'])
            ru_money.append(ratio_sells[sell]['3ddd_sum'])
            en_money.append(ratio_sells[sell]['3dsky_sum'])

        
        writer.writerow([''])

        writer.writerow(['3ddd_pcs'] + ru_count)
        writer.writerow(['3sky_pcs'] + en_count)
        writer.writerow(['3ddd_percent_pcs'] + ru_procent_count)
        writer.writerow(['3sky_percent_pcs'] + en_procent_count)

        writer.writerow([''])
        
        writer.writerow(['3ddd_money'] + ru_money)
        writer.writerow(['3sky_money'] + en_money)
        writer.writerow(['3ddd_percent_money'] + ru_procent_money)
        writer.writerow(['3sky_percent_money'] + en_procent_money)


        writer.writerow([''])
        writer.writerow(['total sells'] + model_m['total_sells'])
        writer.writerow(['money_average'] + model_m['sum_day'])
        writer.writerow([''])
        writer.writerow(['GRAND_TOTAL'] + model_m['grand_total'])
        writer.writerow([''])
        
        writer.writerow(['date\/'])
        
        for item in items:
            list_write = [f" {str(item['data'])} "]
            for d in item['models']:
                list_write.append(str(d["sum"])) 
            writer.writerow(list_write)
    
    if(os.path.isfile(f'result/{date_now}.csv')):
        os.remove(f'result/{date_now}.csv')

    os.replace(f'{date_now}.csv', f'result/{date_now}.csv')

make_csv(trs_dict, trs_dict_old, f'{date_now}.csv', money_average('https://3ddd.ru/user/sell_rating', count_models), ratio)

def js_grafic(): #last_call 
    with open(f'__pycache__/earlier_sells.json') as file:
        f = open('grafic.js', 'r', encoding='utf-8')
        with open(f'time.json', 'w') as fi:
            data = json.load(file)
            data['array_sells'].extend(trs_dict)
            json.dump(data, fi, indent=3)
        fi = open('time.json', 'r', encoding='utf-8')
        l.driver.close()

        driver_new = webdriver.Chrome(executable_path='driver\\chromedriver.exe')
        driver_new.get('https://3ddd.ru/user/')
        driver_new.execute_script(
            f"let JSON_object = `{fi.read()}`; let modelNames = {links_text}; {f.read()}"
        )

        fi.close
        f.close()
    pass

js_grafic()

