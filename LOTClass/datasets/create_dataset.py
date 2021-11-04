import pandas as pd
from sklearn.model_selection import train_test_split

def append_to_file(p, path):
    i = 0
    with open(path, "a") as f:
        for index, row in p.iteritems():
            if i > len(p):
                break
            else:
                f.write(row + "\n")
                i += 1


def create_dataset(X, y, test_size=0.33, random_state=42):
    # Removing new lines
    X = X.replace({r'\s+$': '', r'^\s+': ''}, regex=True)
    X = X.replace(r'\n',  ' ', regex=True)

    X_train, X_test, _, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state)

    append_to_file(X_train, "./LOTClass/datasets/train.txt")
    append_to_file(X_test, "./LOTClass/datasets/test.txt")
    append_to_file(y_test, "./LOTClass/datasets/test_label.txt")


# main

df = pd.read_csv("all_mails_labeled.csv")

X = df["Corps"]
y = df["Catégorie"]

labels = set(y.values.tolist())

with open("./LOTClass/datasets/label_names.txt", "a") as f:
    for label in labels:
        f.write(label + "\n")

create_dataset(X, y)
