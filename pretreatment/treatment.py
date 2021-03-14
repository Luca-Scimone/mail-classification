# Importing Libraries
import spacy
import json
import nltk
import codecs
from nltk.corpus import stopwords
import os
import re

from nltk.stem.snowball import SnowballStemmer


# load french dictionary
nlp = spacy.load("fr_core_news_sm")
stemmer = SnowballStemmer(language='french')

# configuration of stopwords
stopWords = set(stopwords.words('french'))

# getting path: assuming the program is launched in pi
main_dir = os.getcwd()

# navigating to the data folder
data_path = os.path.join(main_dir, "data")

# navigating to the mail folder
data_mail_json = os.path.join(data_path, "mails")
data_raw_mails = os.path.join(data_path, "raw_mails")

# Global variables
Mails = []
Objet_mail = []
Corps_mail = []
Cleaned_Mails = []


def return_token(sentence):
    # Tokeniser la phrase
    doc = nlp(sentence)
    # Retourner le texte de chaque token
    return [X.text for X in doc]


def clean_stop_words(token_list):
    clean_words = []
    for token in token_list:
        if token not in stopWords:
            clean_words.append(token)
    return clean_words


def return_stem(clean_text):
    return [stemmer.stem(X) for X in clean_text]


tokenizer = nltk.RegexpTokenizer(r'\w+')


def to_bag_of_words(mails):
    listunique = []
    for mail in mails:
        for word in mail:
            if word not in listunique:
                listunique.append(word)
    return listunique


def to_bag_of_words_per_mail(mails):
    listeunique_mail = []
    for mail in mails:
        listunique = []
        for word in mail:
            if word not in listunique:
                listunique.append(word)
        listeunique_mail.append(listunique)
    return listeunique_mail


def to_vector_of_mails(mails):
    output = []
    for mail in mails:
        mail_str = ""
        for token in mail:
            mail_str += token + " "
        output.append(mail_str)

    return output


class mails_data:
    def __init__(self):
        init()
        self.mails = Mails
        self.cleaned_mails = Cleaned_Mails

    """
    The method returns the data like a vector of strings.
    Each string being a mail.
    For exemple: ['Ceci est un mail', 'Ceci est un autre mail']
    -------
    """

    def vector_of_mails(self):
        return to_vector_of_mails(self.cleaned_mails)

    """
    The method returns the general bag of words of every mail in the data set.
    For exemple: ['Ceci', 'est', 'un', 'autre', 'mail']
    -------
    """

    def bag_of_words(self):
        return to_bag_of_words(self.cleaned_mails)

    """
    The method returns the bag of words per mail.
    For exemple: [['Ceci', 'est', 'un', 'mail'],['Ceci', 'est', 'un', 'autre', 'mail']]

    The diference between words_by_words() and bag_of_words_per_mail() comes from the fact
    that bag_of_words outputs vectors with unique occurences of words.
    -------
    """

    def bag_of_words_per_mail(self):
        return to_bag_of_words_per_mail(self.cleaned_mails)


# fonction qui initialise toutes les varibles globales
def init():
    for _, _, files in os.walk(data_mail_json):
        # Reading evry file in the folder
        for i, f in enumerate(files[:]):
            temp = []
            file_path = os.path.join(data_mail_json, f)
            
            # Ouvrir avec les bon codecs utf8
            with codecs.open(file_path, 'r', encoding='utf8') as f:
                data_json = json.load(f)

            for msg in data_json['Mail']:
                corps = msg['Corps']
                obj = msg['Objet']
            Objet_mail.append(obj)
            Corps_mail.append(corps)
            temp = obj + corps
            Mails.append(temp)

    for mail in Mails:
        # On supprime les liens et les adresse mails contenue dans les mails
        mail = re.sub(r'<[^>]+>', '', mail, flags=re.MULTILINE)
        mail = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b',
                      '', mail, flags=re.MULTILINE)

        # On met tout en minuscule
        mail = mail.lower()

        # On tokenize
        mail = tokenizer.tokenize(mail)

        # On nettoie le texte
        mail = clean_stop_words(mail)

        # On effectue le stemming
        # mail = return_stem(mail)

        Cleaned_Mails.append(mail)