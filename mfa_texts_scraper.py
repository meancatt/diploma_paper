from selenium.webdriver import Chrome
from selenium.common.exceptions import NoSuchElementException
import time
import os
from json_functions import *
import re

def get_text_data(url, category, driver):
    #create empty dict for text data
    text_data = {}

    # open page in browser
    driver.get(url)
    time.sleep(3)

    # get text data from page
    headers = driver.find_elements_by_tag_name('h1')
    title = ''
    i = 0
    while title in ['', 'Министерство иностранных дел Российской Федерации']:
        title = headers[i].text
        i += 1
    try:
        date = '-'.join(driver.find_element_by_css_selector('span.nowrap').text.split('-')[1:])
    except NoSuchElementException:
        date_time = driver.find_element_by_css_selector('div.article-status-line > span').text
        date_list = re.search('\d\d?\.\d{2}\.\d{2}', date_time).group().split('.')
        date = '-'.join(date_list[0:2]) + '-20' + date_list[2]
    paragraphs = driver.find_elements_by_css_selector('div.text.article-content > p')
    if paragraphs == []:
        paragraphs = driver.find_elements_by_css_selector('p.dxl-par')
    paragraphs_clean = []
    for paragraph in paragraphs:
        style = paragraph.get_attribute('style')
        if 'center' not in style and 'right' not in style:
            paragraphs_clean.append(paragraph.text)
    text = '\n'.join(paragraphs_clean).strip().strip('\n')

    # save scraped data to dict
    text_data['url'] = url
    text_data['title'] = title
    text_data['date'] = date
    text_data['text'] = text

    return text_data

def write_texts_to_file(categories):

    driver = Chrome(executable_path="C://Users//User/chromedriver.exe")
    mfa_texts = get_json_from_file('mfa_texts.json')
    mfa_links = get_json_from_file('mfa_links.json')

    # scrape texts from each category
    for category in categories:
        print('Working with category', category)
        category_texts = []
        category_links = mfa_links[category]
        num_links = len(category_links)
        n = 0
        for category_link in category_links:
            print('Working with link', n, 'out of', num_links)
            try:
                text_data = get_text_data(category_link, category, driver)
            except NoSuchElementException:
                time.sleep(60)
                text_data = get_text_data(category_link, category, driver)
            category_texts.append(text_data)
            n += 1

        # save category texts to dict & write changes to file
        mfa_texts[category] = category_texts
        update_json(mfa_texts, 'mfa_texts.json')
    
    driver.close()

write_texts_to_file(['comments'])