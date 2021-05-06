import os
import json
import codecs
import seaborn as sns
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.naive_bayes import GaussianNB
import matplotlib.pyplot as plt
import torch
import transformers as ppb
import warnings

from transformers import CamembertModel, CamembertTokenizer, CamembertConfig

warnings.filterwarnings('ignore')


### Creating a panda dataframe from the mails
print ("Creating a panda dataframe from the mails")
# =============================================================================

mails = []
labels = []

path = os.path.join(os.path.join(os.getcwd(), "data"), "mails")

for _, _, files in os.walk(path):
    for f in files[:]:
        file_path = os.path.join(path, f)
            
        with codecs.open(file_path, 'r', encoding='utf8') as json_f:
            data_json = json.load(json_f)

        for msg in data_json['Mail']:
            corps = msg['Corps']
            obj   = msg['Objet']
            cat   = msg['Catégorie']

        label = [i for i, label in enumerate(list(cat[0].values())) if label == 1][0]
        mails.append([obj + corps, label])

# Use the mails in a panda dataframe

df = pd.DataFrame(mails,columns=['mail','label']).transpose()
# =============================================================================



### Importing the BERT model and tokenizer
print ("Importing the BERT model and tokenizer")
# =============================================================================

tokenizer = CamembertTokenizer.from_pretrained("camembert-base")
config = CamembertConfig.from_pretrained("camembert-base", output_hidden_states=True)
model = CamembertModel.from_pretrained("camembert-base", config=config)

# =============================================================================


## Preparing the dataset
print ("Preparing the dataset")
# =============================================================================

# This turns every sentence into the list of ids.
# WARNING: BERT cannot handle tokens with a length greater than 512 characters
tokenized = df.iloc[0].apply((lambda x: tokenizer.encode(x, truncation = True, max_length = 100, add_special_tokens=True)))

# Padding
max_len = 0
for i in tokenized.values:
    if len(i) > max_len:
        max_len = len(i)

padded = np.array([i + [0]*(max_len-len(i)) for i in tokenized.values])

# Masking
attention_mask = np.where(padded != 0, 1, 0)
attention_mask.shape

# =============================================================================


## Training the model
print ("Training the model (this might take a while)")
# =============================================================================
input_ids = torch.tensor(padded)  
attention_mask = torch.tensor(attention_mask)

with torch.no_grad():
    last_hidden_states = model(input_ids, attention_mask=attention_mask)

# Fetching the features
features = last_hidden_states[0][:,0,:].numpy()

# The labels
labels = df.iloc[1]

X_train, X_test, y_train, y_test = train_test_split(features, labels)

# Ensuring the labels are integers
y_train = y_train.astype('int')
y_test  = y_test.astype('int')

## Evaluating
print ("Evaluating")
# =============================================================================

label_names = ['Déménagement', 'Relève de compteur', 'Réclamation',
    'Contrat – Coordonnées personnelles', 'Facture – Paiement', 'Espace client']

### --- Testing BERT feature extraction with Random Tree Forest --- ###
rf = RandomForestRegressor(n_estimators = 1000, random_state = 42)
y_pred = rf.fit(X_train, y_train).predict(X_test).astype('int')

# Ploting the confusion matrix
mat = confusion_matrix(y_pred, y_test)
sns.heatmap(mat.T, square = True, annot=True, fmt = "d", xticklabels=label_names,yticklabels=label_names)
plt.title("Using Random Tree Forest")
plt.xlabel("predicted label")
plt.ylabel("true labels")
plt.show()

### --- Testing BERT feature extraction with Gaussian Naive Bayes --- ###
gnb = GaussianNB()
y_pred = gnb.fit(X_train, y_train).predict(X_test).astype('int')

# Ploting the confusion matrix
mat = confusion_matrix(y_pred, y_test)
sns.heatmap(mat.T, square = True, annot=True, fmt = "d", xticklabels=label_names,yticklabels=label_names)
plt.title("Using Bayes Classification")
plt.xlabel("predicted label")
plt.ylabel("true labels")
plt.show()