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

    if (category != 'briefings' or 
    (category == 'briefings' and ('cовместный' in title.lower() or 'совместный' in title.lower() or 'внеочередной' in title.lower()))):
        paragraphs = driver.find_elements_by_css_selector('div.text.article-content > p')
        if paragraphs == []:
            paragraphs = driver.find_elements_by_css_selector('p.dxl-par')
        paragraphs_clean = []
        for paragraph in paragraphs:
            style = paragraph.get_attribute('style')
            if 'center' not in style and 'right' not in style:
                paragraphs_clean.append(paragraph.text)
        text = '\n'.join(paragraphs_clean).strip().strip('\n')

        if category in ['answers', 'minister_speeches', 'deputy_ministers_speeches']:
            qa_text_blocks = parse_qa(text)
            if qa_text_blocks != []:
                text_blocks = []
                first_question = qa_text_blocks[0]['question']
                speech = text.split(first_question)[0].strip(' \n')
                if speech != '' and re.match('Вопрос[ А-ЯЁа-яёA-Za-z\.\(\)]*?:', speech) == None:
                    strings_to_del = []
                    strings_to_del.append(re.search('Вопрос[ А-ЯЁа-яёA-Za-z\.\(\)]*?:', speech))
                    strings_to_del.append(re.match('[А-ЯЁ]\.[А-ЯЁ]\.[А-ЯЁ][^\n]+:', speech))
                    for string_to_del in strings_to_del:
                        if string_to_del != None:
                            speech = speech.replace(string_to_del.group(), '')
                    speech = speech.strip(' \n')
                    speech_text_block = {}
                    speech_text_block['type'] = 'speech'
                    speech_text_block['text'] = speech 
                    text_blocks.append(speech_text_block)
                text_blocks += qa_text_blocks
                text_data['text_blocks'] = text_blocks
    else:
        parsed_briefing = parse_briefing(driver)
        text_blocks = parsed_briefing[0] + parse_qa(parsed_briefing[1])
        text_data['text_blocks'] = text_blocks

    # save scraped data to dict
    text_data['url'] = url
    text_data['title'] = title
    text_data['date'] = date
    if 'text_blocks' not in text_data:
        text_data['text'] = text

    return text_data

def parse_qa(text):
    questions = (re.findall
    ('(?:^|\n)Вопрос[ А-ЯЁа-яёA-Za-z\.\(\)]*?:([\w\s\d\D]+?)(?:\n[А-ЯЁ]\.[А-ЯЁ]\.[А-ЯЁ][^\n]+|\nОтвет[ А-ЯЁа-яёA-Za-z\.\(\)]*?):', 
    text))
    answers = (re.findall
    ('\n(?:Ответ[ А-ЯЁа-яёA-Za-z\.\(\)]*?|[А-ЯЁ]\.[А-ЯЁ]\.[А-ЯЁ][^\n]+):([\w\s\d\D]+?)(?:\nВопрос[ А-ЯЁа-яёA-Za-z\.\(\)]*?:|$)',
     text))
    if len(questions) != len(answers):
        print('Неравное количество QA')
    qa = zip(questions, answers)
    text_blocks = []
    for pair in qa:
        text_block = {}
        text_block['type'] = 'qa'
        text_block['question'] = pair[0]
        text_block['answer'] = pair[1]
        text_blocks.append(text_block)
    return text_blocks

def parse_briefing(driver):
    # get the whole text on the page
    text = driver.find_element_by_css_selector('div.text.article-content')

    # check if the page has a table of contents
    if re.match('^[\n ]*содержание|^[\n ]*оглавление', text.text.lower()):
        topics = text.find_elements_by_css_selector('p')
        topics = [topic for topic in topics if 'center' in topic.get_attribute('style')]
    else:
        topics = ([topic for topic in text.find_elements_by_css_selector('p.dxl-par')  
        if 'center' in topic.get_attribute('style')])

        if topics == []:
            topics = text.find_elements_by_css_selector('div')
            topics = [topic for topic in topics if 'center' in topic.get_attribute('style')]

        if topics == []:
            topics = text.find_elements_by_css_selector('p')
            topics = [topic for topic in topics if 'center' in topic.get_attribute('style')]
    
    # clean topics
    topics_clean = []
    for topic in topics:
        topic = topic.text.strip(' \n*')
        if topic != '' and re.match('^[\n ]*содержание|^[\n ]*оглавление', topic.lower()) == None:
            topics_clean.append(topic)

    # get and clean paragraphs to parse into topics texts
    paragraphs = text.find_elements_by_tag_name('p') 
    paragraphs_clean = []
    for paragraph in paragraphs:
        paragraph = paragraph.text.strip(' \n')
        if paragraph != '' and re.search('к оглавлению', paragraph.lower()) == None:
            paragraphs_clean.append(paragraph)

    try:
        start_indx = paragraphs_clean.index(topics_clean[0])
    except ValueError:
        paragraphs_clean = [paragraph.strip(' \n') for paragraph in text.text.split('\n')]
        start_indx = paragraphs_clean.index(topics_clean[0])

    paragraphs_clean = paragraphs_clean[start_indx:]
    
    # parse paragraphs into topics texts
    text_blocks = []
    indexes_to_skip = []
    for i in range(len(paragraphs_clean)):
        if i not in indexes_to_skip:
            if i != len(paragraphs_clean) - 1:
                current_paragraph = paragraphs_clean[i]
                next_paragraph = paragraphs_clean[i+1]
                if current_paragraph in topics_clean:
                    if next_paragraph in topics_clean:
                        print('Разъехался подзаг -- фиксю')
                        topic = current_paragraph + ' ' + next_paragraph
                        indexes_to_skip.append(i+1)
                    else:
                        topic = current_paragraph
                        if i != 0:
                            text_blocks.append(text_block) 
                    text_block = {}
                    text_block['type'] = 'speech'
                    text_block['title'] = topic
                    text_block['text'] = ''
                elif (re.match('(Из ответов на вопросы[ А-ЯЁа-яёA-Za-z\.\(\)]*?:?|Вопрос[ А-ЯЁа-яёA-Za-z\.\(\)]*?:)', 
                current_paragraph) == None or 'Из ответов на вопросы:' in paragraphs_clean[i+1:]):
                    text_block['text'] = text_block['text'] + '\n' + current_paragraph
                else:
                    text_blocks.append(text_block)
                    if 'Из ответов на вопросы' in current_paragraph:
                        text = '\n'.join(paragraphs_clean[i+1:])
                    else:
                        text = '\n'.join(paragraphs_clean[i:])
                    break
            else:
                text_block['text'] = text_block['text'] + '\n' + paragraphs_clean[i]
                text_blocks.append(text_block)
                text = ''

    if len(text_blocks) != len(topics_clean) and len(indexes_to_skip) == 0:
        print('Кривые подзаги ¯\_(ツ)_/¯')

    return text_blocks, text

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

<<<<<<< HEAD
write_texts_to_file(['comments'])
=======
write_texts_to_file(['minister_speeches'])
>>>>>>> upd texts scraper & add all texts
