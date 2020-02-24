from working_with_files import *
from preprocessing import *
import pandas as pd

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

# save data to df
df = pd.DataFrame(data, columns = ['title', 'date', 'category', 'subheading', 'text'])
df.to_csv('mfa_texts_df.csv', sep='\t', encoding='utf-8')

print('Done with CSV')

# lemmatize texts and save them to df   
df['text_lemmatized'] = df['text'].apply(lemmatize_mystem)
update_csv(df, 'mfa_texts_df')