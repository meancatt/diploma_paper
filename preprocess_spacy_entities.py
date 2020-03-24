# process wikidata json with countries info
wiki_countries = get_json_from_file('wikidata_countries.json')

countries = {}
for wiki_country in wiki_countries:
    country = {}
    if wiki_country['countryLabel'] not in ['Китай', 'Китайская Республика']:
        for k, v in wiki_country.items():
            if re.match('Q\d+', v) == None:
                if k != 'formerLabel':
                    country[k] = v
                else:
                    if ('ССР' in v or 'Советская Социалистическая' in v 
                      or country['countryLabel'] in ['Азербайджан', 'Узбекистан', 'Молдова']):
                        country['post_soviet'] = 1
                    else:
                        country['post_soviet'] = 0
        if country['country'] not in countries:
            countries[country['country']] = country
        else:
            country_old = countries[country['country']]
            for k, v in country.items():
                if k in country_old:
                    if type(country_old[k]) == str and country_old[k] != country[k]:
                        if type(country_old[k]) == str:
                            country_old[k] = [country_old[k]]
                            country_old[k].append(country[k])
                        if type(country_old[k]) == list and country[k] not in country_old[k]:
                            country_old[k].append(country[k])
                else:
                    country_old[k] = country[k]
            countries[country['country']] = country_old

# collect data from wikidata
wp.set_lang('ru')
synonyms = {}
total = len(df)
n = 0
for nes in df['named_entities_preprocessed']:
    print('Working with line', n, 'out of', total)
    if type(nes) != float:
        nes = nes.split('\n')
        for ne in nes:
            try:
                if ne != 'no_count':
                    lemma = ne.split('|')[3]
                    search_results = wp.search(lemma, results=1)
                    if search_results != []:
                        synonyms[lemma] = search_results[0].lower()
            except:
                print('exception')
                pass
    n += 1

print('DONE WITH PART I')

# aggregate all synonyms
values = list(synonyms.values())
num_occur = dict(Counter(values))
values_with_synonyms = [occur for occur, num in list(num_occur.items()) if num > 1]

synonyms_upd = {}
for occur, synonym in synonyms.items():
    if synonym in values_with_synonyms: 
        synonyms_upd[synonym] = []
        for occur1, synonym1 in synonyms.items():
            if synonym == synonym1:
                synonyms_upd[synonym].append(occur1)
                
print('DONE WITH PART II')

# save synonyms dict to json-file
with open('wikipedia_synonyms.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(synonyms_upd, ensure_ascii=False, indent=4)) 


# drop values appearing in a corpus less than 1 time 
with open('wikipedia_synonyms.json', 'r', encoding='utf-8') as f:
    wiki_synonyms = json.loads(f.read())

top = dict(get_top_x_ne(df))

wiki_synonyms_clean = {}
for keyword, synonyms in wiki_synonyms.items():
    new_synonyms_lst = []
    for synonym in synonyms:
        if synonym in top and top[synonym] >= 2:
            new_synonyms_lst.append(synonym)
    if (len(new_synonyms_lst) > 2 or 
        (len(new_synonyms_lst) == 2 and new_synonyms_lst[0].strip() != new_synonyms_lst[1].strip())):
        wiki_synonyms_clean[keyword.split(',')[0]] = new_synonyms_lst

print('Found', len(wiki_synonyms_clean), 'matching entities')

with open('wikipedia_synonyms_clean.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(wiki_synonyms_clean, ensure_ascii=False, indent=4)) 