import spacy
from working_with_files import *
from preprocessing import *
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
        if ent.label_ in ['ORG', 'LOC', 'PER']:
            ents = (ents + ent.text + '|' + str(ent.start_char) + '|' + str(ent.end_char) + '|' 
            + ent.lemma_ + '|' + ent.label_ + '\n')
    return ents

# df = pd.read_csv('mfa_texts_df.csv', sep = '\t', encoding = 'utf-8')

# model = spacy.load('ru2', disable=['tagger', 'parser', 'NER'])
# df['named_entities'] = df['text'].apply(get_entities)

# update_csv(df, 'mfa_texts_df')

df = pd.read_csv('mfa_texts_df.csv', sep = '\t', encoding = 'utf-8')

def update_lemmatization(named_entities):
    entities = named_entities.split('\n')
    entities_upd = []
    for entity in entities:
        entity_data = entity.split('|')
        try:
            lemma = lemmatize_mystem(entity_data[3])
            entity_data_upd = entity_data[:3] + [lemma] + entity_data[4:]
            entity_data_upd = '|'.join(entity_data_upd)
            entities_upd.append(entity_data_upd)
        except IndexError:
            return float('nan')
    return '\n'.join(entities_upd)

df['named_entities'] = df['named_entities'].apply(update_lemmatization)

update_csv(df, 'mfa_texts_df')