import spacy
from working_with_files import *
import pandas as pd

def sort_by_official_dates(df):
    df1 = pd.DataFrame() # < 2008
    df2 = pd.DataFrame() # 2008 - 2013
    df3 = pd.DataFrame() # 2013 - 2016
    df4 = pd.DataFrame() # > 2016
    date1 = datetime.strptime('15-07-2008', '%d-%m-%Y').date()
    date2 = datetime.strptime('20-02-2013', '%d-%m-%Y').date()
    date3 = datetime.strptime('30-11-2016', '%d-%m-%Y').date()
    for index, row in df.iterrows():
        if int(row['Unnamed: 0']) not in [10995, 11494]:
            try:
                date = datetime.strptime(row['date'].strip(), '%d-%m-%Y').date()
            except ValueError:
                date = datetime.strptime(row['date'], '%m-%Y').date()
            if date <= date1:
                df1 = df1.append(row, ignore_index=True)
            if date > date1 and date <= date2:
                df2 = df2.append(row, ignore_index=True)
            if date > date2 and date <= date3:
                df3 = df3.append(row, ignore_index=True)
            if date > date3:
                df4 = df4.append(row, ignore_index=True)
    return df1, df2, df3, df4

def get_entities(text):
    ents = ''
    doc = model(text)
    for ent in doc.ents:
        ents = ents + ent.text + '|' + ent.start_char + '|' + ent.end_char + '|' + ent.lemma_ + '|' + ent.label_ + '\n'
    return ents

df = pd.read_csv('mfa_texts_df.csv', sep = '\t', encoding = 'utf-8')
sorted_dfs = sort_by_official_dates(df)

model = spacy.load('ru2', disable=['tagger', 'parser', 'NER'])
for df in sorted_dfs:
    df['named_entities'] = df['text'].apply(get_entities)