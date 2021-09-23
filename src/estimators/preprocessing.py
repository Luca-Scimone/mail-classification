import spacy
from nltk import PorterStemmer
from sklearn.base import BaseEstimator, TransformerMixin
from unidecode import unidecode


class Lemme(BaseEstimator, TransformerMixin):
    def __init__(self):
        # on ne charge qu'une seule fois le modèle en mémoire
        self.nlp = spacy.load("fr_core_news_sm")

    def fit(self, x, y=None):
        return self

    def lemme_text(self, text):
        return " ".join(word.lemma_ for word in self.nlp(text))

    def lemme(self, col):
        # on utilise la lemmatisation de la librairie spacy
        return " ".join(word.lemma_ for word in self.nlp(col))
        # return col.apply(self.lemme_text)

    def transform(self, data_text):
        # On applique la lemmatisation à chaque texte de la colonne sélectionnée
        data_text = data_text.apply(self.lemme)
        return data_text


class Stem(BaseEstimator, TransformerMixin):

    def __init__(self):
        self.stemmer = PorterStemmer()

    def fit(self, x, y=None):
        return self

    def stem(self, text):
        # on utilise le stemming de la librairie nltk
        return " ".join(self.stemmer.stem(word) for word in text)

    def transform(self, data_text):
        # Pour chaque ligne de la colonne sélectionnée, on applique le stemming
        data_text.apply(self.stem)
        return data_text


class Purge(BaseEstimator, TransformerMixin):
    # cette classe permet de faire certaines opérations propre à chaque texte. Par exemple,
    # mettre le texte en minuscule, supprimer les mots trop petits...
    # On aurait pu mettre aussi la suppression des stopwords.

    def __init__(self, lowercase=True, remove_short_words=0, normalize_space=True, to_ascii=True):
        self.lowercase = lowercase
        self.remove_short_words = remove_short_words
        self.normalize_space = normalize_space
        self.to_ascii = to_ascii

    def fit(self, x, y=None):
        return self

    def purge(self, text):

        if self.lowercase:
            text = text.lower()

        if self.remove_short_words > 0:
            text = " ".join([word for word in text.split() if len(word) > self.remove_short_words])

        if self.normalize_space:
            text = " ".join(text.split())

        if self.to_ascii:
            text = unidecode(text)

        return text

    def transform(self, data_text):
        # Pour chaque ligne de la colonne sélectionnée, on applique une "purge
        data_text.apply(self.purge)
        return data_text
