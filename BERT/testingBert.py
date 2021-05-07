from Bert import Bert
import seaborn as sns
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import confusion_matrix, accuracy_score
import matplotlib.pyplot as plt

X_train, X_test, y_train, y_test = Bert(batch_size=100).embedding()

label_names = ['Déménagement', 'Relève de compteur', 'Réclamation',
    'Contrat – Coordonnées personnelles', 'Facture – Paiement', 'Espace client']

### --- Testing BERT feature extraction with Gaussian Naive Bayes --- ###
gnb = GaussianNB()
y_pred = gnb.fit(X_train, y_train).predict(X_test).astype('int')

print (accuracy_score(y_test, y_pred))

# Ploting the confusion matrix
mat = confusion_matrix(y_pred, y_test)
sns.heatmap(mat.T, square = True, annot=True, fmt = "d", xticklabels=label_names,yticklabels=label_names)
plt.title("Using Bayes Classification")
plt.xlabel("predicted label")
plt.ylabel("true labels")
plt.show()