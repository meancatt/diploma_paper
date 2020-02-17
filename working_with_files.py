import json
from shutil import copyfile

def write_json_to_file(d, filename):
    path = filename
    with open(path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=4)) 
        
def get_json_from_file(filename):
    path = filename
    with open(path, 'r', encoding='utf-8') as f:
        d = json.loads(f.read(), object_hook=lambda d: {int(k) if k.lstrip('-').isdigit() else k: v for k, v in d.items()})
    return d

def update_json(d, filename):
    copyfile(filename, filename + '_backup.json')
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=4)) 

def update_csv(df, filename):
    copyfile(filename + '.csv', filename + '_backup.csv')
    df.to_csv(filename + '.csv', sep='\t', encoding='utf-8')

def get_lexicon_from_file(filename): 
    lexicon = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            lexicon.append(line.strip('\n').lstrip('\ufeff').lower())   
    return lexicon