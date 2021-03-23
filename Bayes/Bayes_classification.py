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
    "treatement", os.path.abspath(os.getcwd()) + "/pretreatment/treatment.py")
pretreatement = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pretreatement)
mails = pretreatement.mails_data()

directory = "./data/mails/"

# Load the dataset
data = mails.vector_of_mails()  # Get the text categories

# Get the label of each mail
mails_labels = mails.get_mails_label()

liste_labels = ["Déménagement","Relève_compteur","Réclamation", "Contrat", "Facture","Espace_Client"]

mails_nom = mails.get_mails_nom()
print(mails_nom)

# define the training set 
# 30% training 70% test
x = len(data)
a = math.floor(0.7 * x)
train_data = data[0:a]
test_data = data[a:]

print("Number of training samples ")
print(len(train_data))
print("Number of test samples ")
print(len(test_data))

# Build the model
model = make_pipeline(TfidfVectorizer(), MultinomialNB())  # Train the model using the training data
model.fit(train_data, mails_labels[0:a])  # Predict the categories of the test data
predicted_categories = model.predict(test_data)
print(np.array(mails_labels))

# plot the confusion matrix
mat = confusion_matrix(mails_labels[a:], predicted_categories)
sns.heatmap(mat.T, square = True, annot=True, fmt = "d", xticklabels=liste_labels,yticklabels=liste_labels)
plt.xlabel("true labels")
plt.ylabel("predicted label")
plt.show()
#print("The accuracy is {}".format(accuracy_score(mails_labels, predicted_categories)))