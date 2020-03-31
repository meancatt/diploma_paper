from working_with_files import *
from preprocessing import *
import pandas as pd

# get the original json
mfa_texts = get_json_from_file('mfa_texts.json')
# read speech-only df from file and drop unnecessary columns
df1 = pd.read_csv('mfa_texts_df.csv', sep = '\t', encoding = 'utf-8')
for column in ['Unnamed: 0', 'named_entities']:
    df1 = df1.drop(column, 1)

# collect QA data from the original json
# structure: title | date | category | subheading (=answer) |  text | text_lemmatized (=NaN)
qa_data = []
for category, texts in mfa_texts.items():
    print('Working with category', category)
    for text in texts:
        if 'text_blocks' in text:
            for text_block in text['text_blocks']:
                if text_block['type'] == 'qa':
                    row = ([text['title'], text['date'], category, 
                    text_block['question'], text_block['answer'], float('nan')])
                    qa_data.append(row)

# save collected QA data to a separate dataframe
df2 = pd.DataFrame(qa_data, columns = ['title', 'date', 'category', 'subheading', 'text', 'text_lemmatized'])

# concatenate QA and speech-only dataframes into a single dataframe
df_final = pd.concat([df1, df2])

# save final dataframe to csv file
df_final.to_csv('mfa_texts_df_rhetoric.csv', sep='\t', encoding='utf-8')

# lemmatize new QA texts in the dataframe using pymorphy

n = 0
for indx, row in df.iterrows():
    if pd.isna(row['text_lemmatized']): 
        print('Working with text', n, 'out of 22457')
        n += 1   
        df.at[indx, 'text_lemmatized'] = lemmatize_pymorphy(row['text'])

update_csv(df, 'mfa_texts_df_rhetoric')