import numpy as np, pandas as pd
import seaborn as sns
import math
import os
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.metrics import confusion_matrix, accuracy_score
sns.set() # use seaborn plotting style

import importlib.util
spec = importlib.util.spec_from_file_location(
    "treatement", os.path.abspath(os.getcwd()) + "/pretreatment/treatment.py")
pretreatement = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pretreatement)
mails = pretreatement.mails_data()


directory = "./data/mails/"

# Load the dataset
data = mails.vector_of_mails()# Get the text categories

#Get the label of each mail 
# (pas encore disponible puisque mail non labélisé)
mails_labels = mails.get_mails_label()

mails_nom = mails.get_mails_nom()
print(mails_nom)

# define the training set 
#30% training 70% test 
x = len(data)
a = math.floor(0.7*x)
train_data = data[0:a]
test_data = data[a:]

print("Number of training samples ")
print(len(train_data))
print("Number of test samples ")
print(len(test_data))

# Build the model
model = make_pipeline(TfidfVectorizer(), MultinomialNB())# Train the model using the training data
model.fit(train_data.data, train_data.target)# Predict the categories of the test data
predicted_categories = model.predict(test_data.data)