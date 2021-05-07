import math
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

sns.set()  # use seaborn plotting style

import importlib.util

spec = importlib.util.spec_from_file_location(
    "WordRepresentation", os.path.abspath(os.getcwd()) + "/pretreatment/WordRepresentation.py")
WordRepresentation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(WordRepresentation)
wr = WordRepresentation.WordRepresentation()

directory = "./data/mails/"

# Load the dataset
data = wr.data

# Get the label of each mail
mails_labels_num, mails_labels = wr.init_unique_labels()

liste_labels = wr.label_names

mails_nom = wr.pretreatement_obj.get_mails_nom()

liste_labels_Bayes = ['Contrat – Coordonnées personnelles', 'Déménagement', 'Espace client', 'Facture – Paiement', 'Relève de compteur', 'Réclamation']
liste_labels_RTF = ['Déménagement','Relève de compteur', 'Réclamation', 'Contrat – Coordonnées personnelles', 'Facture – Paiement', 'Espace client']
# define the training set 
# 30% training 70% test
x = len(data)
print(x)
a = math.floor(0.7 * x)
train_data = data[0:a]
test_data = data[a:]

print("Number of training samples ")
print(len(train_data))
print("Number of test samples ")
print(len(test_data))

# Build the Bayes model ------------------------------------------------
model = make_pipeline(TfidfVectorizer(), MultinomialNB())  # Train the model using the training data
model.fit(train_data, mails_labels[0:a])  # Predict the categories of the test data
predicted_categories = model.predict(test_data)
print(np.array(mails_labels))

print (accuracy_score(mails_labels[a:], predicted_categories))

# plot the confusion matrix
mat = confusion_matrix(predicted_categories, mails_labels[a:])
sns.heatmap(mat.T, square = True, annot=True, fmt = "d", xticklabels=liste_labels,yticklabels=liste_labels)
plt.xlabel("predicted label")
plt.ylabel("true labels")
plt.show()
print("The accuracy with RTF is {}".format(accuracy_score(mails_labels_num[a:], round_predictions)))

#End of Random Tree Forest------------------------------------------------------------------------------------------------------------