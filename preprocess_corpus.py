from json_functions import *
import pandas as pd
import pymorphy2
morph = pymorphy2.MorphAnalyzer()

mfa_texts = get_json_from_file('mfa_texts.json')

# transform neccessary texts & their metadata to list of lists
# structure: title | date | category | header (if any) |  text

data = [] 
for category, texts in mfa_texts.items():
    if category not in ['answers']:
        for text in texts:
            text_data = []
            text_data.append(text['title'])
            text_data.append(text['date'])
            text_data.append(category)
            if 'text' in text:
                text_data.append(('nan'))
                text_data.append(text['text'])
                data.append(text_data)
            else:
                for text_block in text['text_blocks']:
                    text_data_copy = text_data.copy()
                    if text_block['type'] == 'speech':
                        if 'title' in text_block:
                            text_data_copy.append(text_block['title'])
                        else:
                            text_data_copy.append(float('nan'))
                        text_data_copy.append(text_block['text'])
                        data.append(text_data_copy)
                    else:
                        break

df = pd.DataFrame(data, columns = ['title', 'date', 'category', 'subheading', 'text'])
df.to_csv('mfa_texts_df.csv', sep='\t', encoding='utf-8')

# function for updating mfa_texts dataframe

def update_csv(df, filename):
    copyfile(filename + '.csv', filename + '_backup.csv')
    df.to_csv(filename + '.csv', sep='\t', encoding='utf-8')

# functions for text preprocessing

def get_all_texts(df):
    all_texts = ''
    for text in df['text']:
        all_texts += text
    return all_texts

def generate_symbols_to_del(text):
    symbols_to_del = []
    for symbol in set(text):
        if symbol.isalpha() == False and symbol != ' ':
            symbols_to_del.append(symbol)
    return symbols_to_del

def lemmatize(text):
    words = text.split()
    lemmatized_text = []
    for word in words:
        word = morph.parse(word)[0].normal_form
        lemmatized_text.append(word)
    return ' '.join(lemmatized_text)

def clean(text, symbols_to_del):
    for symbol_to_del in symbols_to_del:
        text = text.replace(symbol_to_del, ' ')
    text = ' '.join([symbol for symbol in text.split() if symbol != ' '])
    return text

#symbols_to_del = generate_symbols_to_del(get_all_texts(df))
    
df['text_lemmatized'] = df['text'].apply(lemmatize)
update_csv(df, 'mfa_texts_df')