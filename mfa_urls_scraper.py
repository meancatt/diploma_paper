from selenium.webdriver import Chrome
import time
import os
import json
from shutil import copyfile
import string
import re

def write_json_to_file(d, filename):
    path = 'Desktop//учебка_ВШЭ//diploma_paper//' + filename
    with open(path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=4)) 
        
def get_json_from_file(filename):
    path = 'Desktop//учебка_ВШЭ//diploma_paper//' + filename
    with open(path, 'r', encoding='utf-8') as f:
        d = json.loads(f.read(), object_hook=lambda d: {int(k) if k.lstrip('-').isdigit() else k: v for k, v in d.items()})
    return d

def update_json(d, filename):
    copyfile('Desktop//учебка_ВШЭ//diploma_paper//' + filename, 
             'Desktop//учебка_ВШЭ//diploma_paper//' + filename + '_backup.json')
    with open('Desktop//учебка_ВШЭ//diploma_paper//' + filename, 'w', encoding='utf-8') as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=4)) 

def get_links(start_url):
    mfa_links = get_json_from_file('mfa_links.json')
    driver = Chrome(executable_path="C://Users//User/chromedriver.exe")
    
    # open page 1 and count pages
    driver.get(start_url + '1')
    time.sleep(3)
    num_pages = int(driver.find_elements_by_css_selector('div.paginates > ul > li')[-2].text)
    
    # generate pages urls list
    pages = [start_url + str(i) for i in range(1, num_pages + 1)]
    
    # get links to texts from every page
    all_links = []
    for page in pages:
        driver.get(page)
        time.sleep(3)
        links = [link.get_attribute('href') for link in driver.find_elements_by_css_selector('a.anons-title')]
        all_links.extend(links)
        
    # save scraped data to file    
    category = re.compile('/(\w+)\?').findall(start_url)[0]
    mfa_links[category] = all_links 
    update_json(mfa_links, 'mfa_links.json')
    
    driver.close()

categories_links = [
    'https://www.mid.ru/ru/press_service/spokesman/official_statement?p_p_id=101_INSTANCE_t2GCdmD8RNIr&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_pos=1&p_p_col_count=2&_101_INSTANCE_t2GCdmD8RNIr_delta=10&_101_INSTANCE_t2GCdmD8RNIr_keywords=&_101_INSTANCE_t2GCdmD8RNIr_advancedSearch=false&_101_INSTANCE_t2GCdmD8RNIr_andOperator=true&p_r_p_564233524_resetCur=false&_101_INSTANCE_t2GCdmD8RNIr_cur=',
    'https://www.mid.ru/ru/press_service/spokesman/briefings?p_p_id=101_INSTANCE_D2wHaWMCU6Od&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_pos=1&p_p_col_count=2&_101_INSTANCE_D2wHaWMCU6Od_delta=20&_101_INSTANCE_D2wHaWMCU6Od_keywords=&_101_INSTANCE_D2wHaWMCU6Od_advancedSearch=false&_101_INSTANCE_D2wHaWMCU6Od_andOperator=true&p_r_p_564233524_resetCur=false&_101_INSTANCE_D2wHaWMCU6Od_cur=',
    'https://www.mid.ru/ru/press_service/spokesman/answers?p_p_id=101_INSTANCE_OyrhusXGz9Lz&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_pos=1&p_p_col_count=2&_101_INSTANCE_OyrhusXGz9Lz_delta=10&_101_INSTANCE_OyrhusXGz9Lz_keywords=&_101_INSTANCE_OyrhusXGz9Lz_advancedSearch=false&_101_INSTANCE_OyrhusXGz9Lz_andOperator=true&p_r_p_564233524_resetCur=false&_101_INSTANCE_OyrhusXGz9Lz_cur=',
    'https://www.mid.ru/ru/kommentarii?p_p_id=101_INSTANCE_2MrVt3CzL5sw&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_pos=1&p_p_col_count=2&_101_INSTANCE_2MrVt3CzL5sw_delta=20&_101_INSTANCE_2MrVt3CzL5sw_keywords=&_101_INSTANCE_2MrVt3CzL5sw_advancedSearch=false&_101_INSTANCE_2MrVt3CzL5sw_andOperator=true&p_r_p_564233524_resetCur=false&_101_INSTANCE_2MrVt3CzL5sw_cur=',
    'https://www.mid.ru/ru/press_service/minister_speeches?p_p_id=101_INSTANCE_7OvQR5KJWVmR&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_pos=1&p_p_col_count=2&_101_INSTANCE_7OvQR5KJWVmR_delta=10&_101_INSTANCE_7OvQR5KJWVmR_keywords=&_101_INSTANCE_7OvQR5KJWVmR_advancedSearch=false&_101_INSTANCE_7OvQR5KJWVmR_andOperator=true&p_r_p_564233524_resetCur=false&_101_INSTANCE_7OvQR5KJWVmR_cur=',
    'https://www.mid.ru/ru/press_service/deputy_ministers_speeches?p_p_id=101_INSTANCE_O3publba0Cjv&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_pos=1&p_p_col_count=2&_101_INSTANCE_O3publba0Cjv_delta=10&_101_INSTANCE_O3publba0Cjv_keywords=&_101_INSTANCE_O3publba0Cjv_advancedSearch=false&_101_INSTANCE_O3publba0Cjv_andOperator=true&p_r_p_564233524_resetCur=false&_101_INSTANCE_O3publba0Cjv_cur='
    ]

for category_link in categories_links:
    print('Working with url', category_link)
    get_links(category_link)