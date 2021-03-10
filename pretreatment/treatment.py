## Importing Libraries
import numpy as np
import spacy
import json
import nltk
import csv
import codecs
import pandas as pd
from IPython.display import display 
from spacy import displacy
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
import warnings
import os

from nltk.stem.snowball import SnowballStemmer


##load french dictionary
nlp = spacy.load("fr_core_news_sm")
stemmer = SnowballStemmer(language='french')

##configuration of stopwords
stopWords = set(stopwords.words('french'))

## getting upper path
path_parent = os.path.dirname(os.getcwd())
os.chdir(path_parent)
main_dir = os.getcwd()

# navigating to the data folder
data_path = os.path.join(main_dir, "data")

# navigating to the mail folder
data_mail_json = os.path.join(data_path, "mails")
data_raw_mails = os.path.join(data_path, "raw_mails")


def return_token(sentence):
    # Tokeniser la phrase
    doc = nlp(sentence)
    # Retourner le texte de chaque token
    return [X.text for X in doc]

def clean_stop_words(token_list):
    clean_words = []
    for token in token_list:
        if token not in stopWords :
            clean_words.append(token)
    return clean_words

def return_stem(clean_text):
    return [stemmer.stem(X) for X in clean_text]


tokenizer = nltk.RegexpTokenizer(r'\w+')

def freq_mot(text_token):
    listunique = []
    freq = dict()
    i = 0
    for mot in text_token :
        if mot not in listunique :
            listunique.append(mot)
            freq[i] = {mot : text_token.count(mot)}
            i+= 1 
    return freq



corps = []
# Iterating the contents of the folder
for root, sub_dir,files in os.walk(data_mail_json):
    ## only reading the first file (set to 1)
    for i,f in enumerate(files[0:1]):
        file_path = os.path.join(data_mail_json,f)
        print ("processing file no :", i+1,'\n')
        with codecs.open(file_path, 'r', encoding='utf8') as f:
            data_json = json.load(f)
        for msg in data_json :
            corps.append(msg['Corps'])
            text = msg['Corps']
        print(corps)

        ##On met tout en minuscule
        text = text.lower()
        #print(text)
        
        ##On tokenize
        token_text = tokenizer.tokenize(text)
        #print(token_text)
        
        #On nettoie le texte
        text_clean = clean_stop_words(token_text)
        #print(text_clean)
        
        #petit bonus voire la fréquence de chaque mot
        b = freq_mot(token_text)
        b2 = freq_mot(text_clean)

        #On créer le DataFrame
        df = pd.DataFrame.from_dict(b)
        df2 = pd.DataFrame.from_dict(b2)

        #On remplace tout les NaN par 0
        df = df.replace(np.nan, 0)
        df2 = df2.replace(np.nan, 0)

        #On l'exporte en csv
        df.to_csv(r'file1.csv', index = True)
        df2.to_csv(r'file2.csv', index =True)

        #On effectue le stemming
        text_stem = return_stem(text_clean)
        print(text_stem)