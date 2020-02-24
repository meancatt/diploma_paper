import pymorphy2
morph = pymorphy2.MorphAnalyzer()

from pymystem3 import Mystem
mystem = Mystem() 

def get_all_texts(df):
    all_texts = ''
    for text in df['text']:
        all_texts += text
    return all_texts

def generate_symbols_to_del(text):
    symbols_to_del = []
    for symbol in set(text):
        if symbol.isalpha() == False and symbol not in [' ', '-']:
            symbols_to_del.append(symbol)
    return symbols_to_del

def lemmatize_pymorphy(text):
    words = text.split()
    lemmatized_text = []
    for word in words:
        word = morph.parse(word)[0].normal_form
        lemmatized_text.append(word)
    return ' '.join(lemmatized_text)

def lemmatize_mystem(text):
    return ''.join(mystem.lemmatize(text))

def clean(text, symbols_to_del):
    for symbol_to_del in symbols_to_del:
        text = text.replace(symbol_to_del, ' ')
    text = ' '.join([symbol for symbol in text.split() if symbol != ' '])
    return text