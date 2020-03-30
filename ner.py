from collections import Counter
import pandas as pd
from datetime import datetime
import wikipedia as wp
import json
import re
from working_with_files import *
from preprocessing import *

# FUNCTIONS FOR 'CLEANING' NAMED ENTITIES
def check_lemma_by_dicts(lemma, entity_type, named_entities):
        # mark meaningless entities
        entities_stoplist = get_json_from_file('entities_stoplist.json')
        if lemma in entities_stoplist:
            return 'no_count'
        
        # keep only last names of PER
        if entity_type == 'PER':
            last_name = ''
            if ' ' in lemma:
                lemma = lemma.split()[-1].strip()
                last_name = lemma
            if re.match('\w+\.\w*\.?.+', lemma):
                last_name = lemma.split('.')[-1].strip()
            elif re.match('.+\w+\.\w*\.?', lemma):
                last_name = lemma.split('.')[0].strip()
            if last_name == 'лавр':
                return 'лавров'
            elif last_name != '':
                return last_name
        
        # replace synonyms with one word
        if (lemma == 'содружество' and '|снг|' in named_entities) or lemma == 'содружество независимый государство':
            return 'снг'
        if 'озхий' in lemma:
            return 'озхо'
        if 'скрипал' in lemma:
            return 'скрипаль'
        synonyms = get_json_from_file('synonyms.json')
        for keyword, synonyms in synonyms.items():
            if lemma in synonyms:
                return keyword
        return 'nan'
    
def check_lemma_by_rules(lemma, named_entities, all_entities):
    synonyms = {}
    if '(' in lemma:
        lemma_elements = lemma.split('(')
        full_name = lemma_elements[0].strip()
        abbr = lemma_elements[1].strip(' )')
        if full_name in all_entities or abbr in all_entities:
            synonyms[full_name] = [abbr, lemma]
    if '«' in lemma:
        lemma_elements = lemma.split('«')
        name = lemma_elements[1].strip(' »')
        if name in all_entities:
            synonyms[name] = [lemma]
    for keyword, synonyms in synonyms.items():
        if lemma in synonyms:
            return keyword
    return 'nan'

# replace entities-synonyms with one word using wikidata
def unify_entities(nes):
    if not pd.isna(nes):
        entities = nes.split('\n')
        entities_upd = []
        synonyms = get_json_from_file('wikidata_synonyms.json')
        for entity in entities:
            if entity != 'no_count':
                entity_data = entity.split('|')
                lemma = entity_data[3]
                new_lemma = None
                for keyword, keyword_synonyms in synonyms.items():
                    if lemma in keyword_synonyms:
                        new_lemma = keyword
                if new_lemma == None:
                    new_lemma = lemma
                entity_data_upd = '|'.join(entity_data[:3] + [new_lemma] + entity_data[4:])
            else:
                entity_data_upd = 'no_count'
            entities_upd.append(entity_data_upd)
        entities = '\n'.join(entities_upd)
        return entities
    else:
        return float('nan')
    
def clean_named_entities(named_entities):
    if type(named_entities) != float:
        entities = named_entities.split('\n')
        entities_upd = []
        all_entities = open('all_entities.txt', 'r', encoding='utf-8').read().split('\n')
        for entity in entities:
            entity_data = entity.split('|')
            lemma = entity_data[3]
            entity_type = entity_data[-1]
            new_lemma = check_lemma_by_rules(lemma, named_entities, all_entities)
            if new_lemma == 'nan':
                new_lemma = check_lemma_by_dicts(lemma, entity_type, named_entities)
            if new_lemma == 'nan':
                new_lemma = lemma
            if new_lemma != 'no_count':
                entity_data_upd = '|'.join(entity_data[:3] + [new_lemma] + entity_data[4:])
            else:
                entity_data_upd = 'no_count'
            entities_upd.append(entity_data_upd)
        entities = '\n'.join(entities_upd)
        return entities
    else:
        return float('nan')
    
# join entities that were incorrectly split up
def join_split_entities(df):
    for indx, row in df.iterrows():
        nes = row['named_entities_preprocessed']
        if type(nes) != float:
            nes = nes.split('\n')
            nes_upd = []
            next_lemma = ''
            for i in range(len(nes)):
                ne = nes[i]
                if ne != 'no_count' and next_lemma != 'no_count':
                    curr_ne_data = ne.split('|')
                    end_char_current = int(curr_ne_data[2])
                    curr_lemma = curr_ne_data[3]
                    ent_type_curr = curr_ne_data[4]
                    if i != len(nes)-1 and nes[i+1] != 'no_count':
                        next_ne_data = nes[i+1].split('|')
                        start_char_next = int(next_ne_data[1]) 
                        ent_type_next = next_ne_data[4]
                        if (end_char_current == start_char_next - 1 and ent_type_next != 'PER' 
                        and (ent_type_curr == 'LOC' and ent_type_next == 'LOC') == False):
                            curr_lemma = curr_ne_data[3] + ' ' + next_ne_data[3]
                            next_lemma == 'no_count'
                        else:
                            next_lemma = ''
                    ne_data_str = '|'.join(curr_ne_data[:3] + [curr_lemma] + curr_ne_data[4:])
                    nes_upd.append(ne_data_str)
                else:
                    nes_upd.append('no_count')
                    next_lemma = ''
            nes_upd_str = '\n'.join(nes_upd)
            df.at[indx, 'named_entities_preprocessed'] = nes_upd_str  
    return df

# SORT DFS
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

# GET MOST FREQ ENTITIES
def get_ne(df, types):
    all_entities = []
    for index, row in df.iterrows():
        named_entities = row['named_entities_preprocessed']
        if type(named_entities) != float:
            all_lemmas = []
            named_entities = named_entities.split('\n')
            for named_entity in named_entities:
                if named_entity != 'no_count':
                    entity_data = named_entity.split('|')
                    entity_type = entity_data[4]
                    lemma = entity_data[3]
                    if entity_type in types and lemma not in get_json_from_file('entities_stoplist.json'):
                        all_lemmas.append(lemma)
            unique_lemmas = list(set(all_lemmas))
            all_entities.extend(unique_lemmas)

    freq_dict = dict(Counter(all_entities))
    top = sorted(freq_dict.items(), key = lambda kv: kv[1], reverse=True)
    return top

def show_top_x_ne(df, x, types):
    top = get_ne(df, types)
    print(top[:x])
    return top

# GET STAT BY REGION
def match_entity_to_country(entity, countries, region_type):
    for country in countries.values():
        country_name = country['countryLabel'].lower()
        country_lemma = country['countryLabelLemmatized']
        region = country[region_type + 'Label']
        wikidata_synonyms = get_json_from_file('wikidata_synonyms.json')
        if ' ' in country_lemma:
            country_lemma_words = country_lemma.split()
            if ((len(country_lemma_words) == 2 and country_lemma_words[0] in ['республика', 'южная', 'южный', 
                'экваториальная', 'королевство', 'государство', 'восточный']) or 
                country_lemma.startswith('демократический республика')):
                alternative_country_name = country_lemma_words[-1]
        else:
            alternative_country_name = None
        if entity in [country_name, country_lemma, alternative_country_name] or alternative_country_name in entity.split():
            return country_name.title(), region
        elif entity in wikidata_synonyms:
            synonyms = wikidata_synonyms[entity]
            for name in [country_name, country_lemma, alternative_country_name]:
                if name in synonyms:
                    return country_name.title(), region   
            for synonym in synonyms:
                if alternative_country_name in synonym.split():
                    return country_name.title(), region 


def get_stat_by_region(df, region_type):
    country_to_region = get_json_from_file('country_to_region_new.json')
    all_countries = []
    all_regions = []
    for indx, row in df.iterrows():
        print(indx)
        nes = row['named_entities_preprocessed']
        if not pd.isna(nes):
            article_countries = []
            article_regions = []
            nes = nes.split('\n')
            for ne in nes:
                if ne != 'no_count':
                    ne = ne.split('|')
                    lemma = ne[3]
                    match = match_entity_to_country(lemma, country_to_region, region_type)
                    if match:
                        article_countries.append(match[0])
                        if match[0] != 'Россия':
                            article_regions.append(match[1])
        article_countries = list(set(article_countries))
        article_regions = list(set(article_regions))
        all_countries.extend(article_countries)
        all_regions.extend(article_regions)
    countries_stat = sorted(dict(Counter(all_countries)).items(), key=lambda kv: kv[1], reverse=True)
    regions_stat = sorted(dict(Counter(all_regions)).items(), key=lambda kv: kv[1], reverse=True) 
    print('COUNTRIES TOP:\n', countries_stat, '\n')
    print('REGIONS TOP:\n', regions_stat)