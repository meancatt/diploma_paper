from working_with_files import *
from preprocessing import *
import pandas as pd
mystem = Mystem()

# get df with unlemmatized texts
df = pd.read_csv('mfa_texts_df_rhetoric.csv', sep = '\t', encoding = 'utf-8')

# make list of dicts with ids & raw texts
texts = []
for indx, row in df.iterrows():
    text = {}
    text['id'] = indx
    text['text'] = row['text']
    texts.append(text)

# lemmatize texts & save lemmas + pos tags to list of dicts
n = 0
total = len(texts)
for text in texts:
    print('Working with text {} out of {}'.format(n, total))
    text_elements = mystem.analyze(text['text'])
    text['lemmas'] = []
    text['pos_tags'] = []
    for text_element in text_elements:
        if 'analysis' in text_element and text_element['analysis'] != []:
            lex = text_element['analysis'][0]['lex']
            pos_tag = text_element['analysis'][0]['gr'].split(',')[0].split('=')[0]
            text['lemmas'].append(lex)
            text['pos_tags'].append(pos_tag)
        else:
            text['lemmas'].append(text_element['text'])
            text['pos_tags'].append('NO_POS')
    n += 1

# save data to json 
write_json_to_file(texts, 'rhetoric_texts_lemmatized.json')