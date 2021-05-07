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

print(train_data)
exit(0)

# Build the Bayes model --------------------------------------------------------------------------------------------------------------
model = make_pipeline(TfidfVectorizer(), MultinomialNB())  # Train the model using the training data
model.fit(train_data, mails_labels[0:a])  # Predict the categories of the test data
predicted_categories = model.predict(test_data)


# plot the confusion matrix of Bayes
mat = confusion_matrix(predicted_categories, mails_labels[a:])
sns.heatmap(mat, square = True, annot=True, fmt = "d", xticklabels = liste_labels_Bayes, yticklabels = liste_labels_Bayes)
plt.xlabel("true labels")
plt.ylabel("predicted label")
plt.show()
print("The accuracy with Bayes is {}".format(accuracy_score(mails_labels[a:], predicted_categories)))
#End of Bayes model ------------------------------------------------------------------------------------------------------------------


# Build Random Tree Forest model -----------------------------------------------------------------------------------------------------
X = wr.count() # Using a simple couting representation 
X_train = X[0:a]
X_test = X[a:]
# Import the model we are using
from sklearn.ensemble import RandomForestRegressor
# Instantiate model with 1000 decision trees
rf = RandomForestRegressor(n_estimators = 1000, random_state = 42)
# Train the model on training data
rf.fit(X_train, mails_labels_num[0:a])
# Predict the model
predictions = rf.predict(X_test)


# plot the confusion matrix of Random Tree Forest
round_predictions = np.around(predictions)
mat_r = confusion_matrix(round_predictions, mails_labels_num[a:])
sns.heatmap(mat_r, square = True, annot=True, fmt = "d", xticklabels = liste_labels_RTF, yticklabels = liste_labels_RTF)
plt.xlabel("true labels")
plt.ylabel("predicted label")
plt.show()
print("The accuracy with RTF is {}".format(accuracy_score(mails_labels_num[a:], round_predictions)))

#End of Random Tree Forest------------------------------------------------------------------------------------------------------------