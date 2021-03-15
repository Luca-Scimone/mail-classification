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
Nom_mail = []
Objet_mail = []
Corps_mail = []
Label_mail = []
Cleaned_Mails = []


def return_token(sentence):
    # Tokenize the sentence
    doc = nlp(sentence)
    # Return the text of each token
    return [X.text for X in doc]

# Fonction that cleans stop words
def clean_stop_words(token_list):
    clean_words = []
    for token in token_list:
        if token not in stopWords:
            clean_words.append(token)
    return clean_words

# Fonction that returns the text stemmed
def return_stem(clean_text):
    return [stemmer.stem(X) for X in clean_text]


tokenizer = nltk.RegexpTokenizer(r'\w+')

# Fonction that returns the bag of words of evry mail in data set
def to_bag_of_words(mails):
    listunique = []
    for mail in mails:
        for word in mail:
            if word not in listunique:
                listunique.append(word)
    return listunique

# Fonction that returns the bag of words for each mail
def to_bag_of_words_per_mail(mails):
    listeunique_mail = []
    for mail in mails:
        listunique = []
        for word in mail:
            if word not in listunique:
                listunique.append(word)
        listeunique_mail.append(listunique)
    return listeunique_mail

# Fonction that transforms a list of token of a mail in a string
def to_vector_of_mails(mails):
    output = []
    for mail in mails:
        mail_str = ""
        for token in mail:
            mail_str += token + " "
        output.append(mail_str)

    return output

def list_label():
    return Label_mail

def list_nom():
    return Nom_mail

class mails_data:
    """
    A class used to represent mails_data

    ...

    Attributes
    ----------
    mails: list of str
        A list of string of each mails
        For example : ["Ceci est un mail", "Ceci est un autre mail"]
    
    cleaned_mails : list of list of str
        A list of token of each mails
        For example : [['Ceci', 'est', 'un', 'mail'], ['Ceci' 'est', 'un', 'autre','mail']]

    Methods
    -------
    vector_of_mails()
        Returns a list of strings of each cleaned mail
        For example : ["Ceci est mail", "Ceci est autr mail"]
    
    bag_of_words()
        Returns a list of token which represent the bag
        of words of every cleaned mail in the dataset
        For example : ['Je', 'suis', 'sac', 'mots]
    
    bag_of_words_per_mails()
        Returns a list of token which reprensent the bag
        of words of each cleaned mail
        For example : [['Je', 'suis', 'sac', 'mots', 'mail', '1'],['Je', 'suis', 'sac', 'mots', 'mail', '2']]
    """

    def __init__(self):
        """
        Parameters
        ----------
        Mails: list of str
            List of string of mails in dataset
        Cleaned_Mails: str
            List of token of each mails cleaned
        """

        init()
        self.mails = Mails
        self.cleaned_mails = Cleaned_Mails



    def vector_of_mails(self):
        return to_vector_of_mails(self.cleaned_mails)

    def bag_of_words(self):
        return to_bag_of_words(self.cleaned_mails)

    def bag_of_words_per_mail(self):
        return to_bag_of_words_per_mail(self.cleaned_mails)
    
    def get_mails_label(self):
        return list_label()
    
    def get_mails_nom(self):
        return list_nom()


# Fonction that initialise every global variables
def init():
    for _, _, files in os.walk(data_mail_json):
        # Reading evry file in the folder
        for i, f in enumerate(files[:]):
            temp = []
            file_path = os.path.join(data_mail_json, f)
            
            # Ouvrir avec les bon codecs utf8
            with codecs.open(file_path, 'r', encoding='utf8') as f:
                data_json = json.load(f)
                file_name = os.path.basename(file_path)
                Nom_mail.append(file_name)

            for msg in data_json['Mail']:
                corps = msg['Corps']
                obj = msg['Objet']
                cat = msg['Catégorie']
            Objet_mail.append(obj)
            Corps_mail.append(corps)
            Label_mail.append(cat)
            temp = obj + corps
            Mails.append(temp)

    for mail in Mails:
        # On supprime les liens et les adresse mails contenue dans les mails
        mail = re.sub(r'<[^>]+>', '', mail, flags=re.MULTILINE)
        mail = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b',
                      '', mail, flags=re.MULTILINE)

        # On supprime les chiffres
        mail = re.sub(r'[0-9]', '', mail, flags=re.MULTILINE)

        # On met tout en minuscule
        mail = mail.lower()

        # On tokenize
        mail = tokenizer.tokenize(mail)

        # On nettoie le texte
        mail = clean_stop_words(mail)

        # On effectue le stemming
        # mail = return_stem(mail)

        Cleaned_Mails.append(mail)