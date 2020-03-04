import spacy
from working_with_files import *
from preprocessing import *
import pandas as pd

def get_entities(text):
    ents = ''
    doc = model(text)
    for ent in doc.ents:
        if ent.label_ in ['ORG', 'LOC', 'PER']:
            ents = (ents + ent.text.strip('\n') + '|' + str(ent.start_char) + '|' + str(ent.end_char) + '|' 
            + ent.lemma_ + '|' + ent.label_ + '\n')
    return ents

def update_lemmatization(named_entities):
    if type(named_entities) != float:
        entities = named_entities.strip('\n').split('\n')
        entities_upd = []
        for entity in entities:
            entity_data = entity.split('|')
            if len(entity_data) != 5:
                print(named_entities)
                print(entity_data)
            lemma = lemmatize_pymorphy(entity_data[3])
            entity_data_upd = entity_data[:3] + [lemma] + entity_data[4:]
            entity_data_upd = '|'.join(entity_data_upd)
            entities_upd.append(entity_data_upd)
    else:
        return float('nan')
    return '\n'.join(entities_upd)

# perform NER
df = pd.read_csv('mfa_texts_df.csv', sep = '\t', encoding = 'utf-8')
model = spacy.load('ru2', disable=['tagger', 'parser', 'NER'])
df['named_entities'] = df['text'].apply(get_entities)
update_csv(df, 'mfa_texts_df')

# relemmatize entities
df['named_entities'] = df['named_entities'].apply(update_lemmatization)
update_csv(df, 'mfa_texts_df')