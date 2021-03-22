"""
This script allows the user to manualy label mails.
The script reads the directory ./data/mails/ and adds a
label under Catégorie inside a new directory ./data/labeled_mails/.

Dependecies:

pip install fast-autocomplete
pip install fast-autocomplete[levenshtein]
"""

import os
import shutil
import sys
import codecs
import json
import readchar
from fast_autocomplete import AutoComplete

"""
Usage:

python3 ./Labelization/add_labels/add_labels.py [ENCODING]
"""
words = {"demenagement": {}, "releve": {}, "reclamation": {},
         "contrat": {}, "facture": {}, "espace": {}}
autocomplete = AutoComplete(words=words)

if len(sys.argv) != 2:
    print("Wrong arguments.")
    print("Usage: python3 ./Labelization/add_labels/add_labels.py [ENCODING]")
    exit(1)

# The URL containing the data
encoding = str(sys.argv[1])


"""
This class is used to add colors to the output of this script.
"""


class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


"""
Used Directories
"""


data_directory = os.path.join("data", "mails")
checkpoint_directory = os.path.join("data", "labeling_checkpoint")
output_directory = os.path.join("data", "labeled_data")
output_directory_labeled = os.path.join(
    os.path.join("data", "labeled_data"), "labeled")
output_directory_unlabeled = os.path.join(
    os.path.join("data", "labeled_data"), "unlabeled")


"""
This function prints the diferent labels that can be used by the user.
It also describes how to save the labelization to the current mail.

To add a mail, the user can write it's name in the terminal.
The user's input will be autocompleted as soon as a match appears.

If the label is not what the user wanted, it is possible to revert
a label using CNTRL-Z.

If the user is done with the labelization of a mail. Pressing ENTER
loads the next mail in the data base.

If the user wishes to use more than one label; it is possible to hit
TAB in order to add more labels.

If the user wants to clear his label proposition; using SUPR will
reset it's label word
"""


def labeling_usage():
    print("* Déménagement (label:" + color.BOLD + " déménagement" + color.END + ")")
    print("* Relève de compteur (label:" + color.BOLD + " relève" + color.END + ")")
    print("* Réclamation (label:" + color.BOLD + " réclamation" + color.END + ")")
    print("* Contrat / Coordonnées personnelles (label:" +
          color.BOLD + " contrat" + color.END + ")")
    print("* Ma facture / Mon paiement (label:" +
          color.BOLD + " facture" + color.END + ")")
    print("* Mon espace client (label:" + color.BOLD + " espace" + color.END + ")")
    print("* ENTER -- Prochain mail")
    print("* TAB -- Ajout d'un label supplémentaire")
    print("* CNTRL-Z -- Supprimer le dernier label ajouté")
    print("* CNTRL-C -- Quitter")


"""
This function reads a mail with path 'filename'.

It prints the object of a mail and its body so the user of this
script can decide which label describes best the mail.
"""


def read_mail(filename):
    with codecs.open(filename, 'r', encoding='utf8') as f:
        data_json = json.load(f)

        for msg in data_json['Mail']:
            corps = msg['Corps']
            obj = msg['Objet']

        print(80*'=')
        print(color.BOLD + color.RED + obj + color.END + color.END)
        print(80*'=')
        print(corps)
        print(80*'=')


"""
This function asks for user input char by char and attempts
to match the user function with one label name (using autocomplete.search)

It also implements the special options like CNTRL-Z, CNTRL-C ect... 
"""


def autocompletion(labels):
    c, user_input = "", ""

    while (c != repr('\r') and c != repr('\t') and c != repr('\x7f') and c != repr('\x1a')):
        c = repr(readchar.readchar())

        if (c == repr('\x03')):  # aborting program on CNTRl-C
            print("\n\nAborted !")
            shutil.rmtree(output_directory)
            exit(0)
        if (c == repr('\x1a')):  # removing label on CNTRL-Z
            if len(labels):
                print("Removed label:",  color.BOLD,
                      labels[-1][0][0], color.END)
                labels.pop()

        user_input += c[1:-1]

        auto_completion = autocomplete.search(
            word=user_input, max_cost=3, size=3)

        # Case of multiple matches or no matches ar all:
        if (len(auto_completion) != 1):
            print(c[1:-1], end="", flush=True)
            continue
        # Found a match
        elif auto_completion not in labels:
            print("-- added label: ", color.BOLD,
                  auto_completion[0][0], color.END)
            labels.append(auto_completion)

    return c, labels


"""
Loops until the user is done with the labelization of a mail.
"""


def input_label():
    labeling_usage()
    labels = []

    while (True):
        print("Label:", end=" ", flush=True)

        last_char, labels = autocompletion(labels)

        if (last_char == repr('\r')):
            if len(labels):
                print("Added labels: ")
                for label in labels:
                    print(color.BOLD + label[0][0] +
                          color.END, end=" ", flush=True)
                print("\nLoading next mail...")
                break
            else:
                print("No labels added.")
                print("\nLoading next mail...")
                break

        print("", flush=True)

    return labels


"""
Writes the label choice of the user into a json file.
"""


def write_label(filename, labels):
    f = open(os.path.join(data_directory, filename), "r", encoding=encoding)
    json_object = json.load(f)
    f.close()

    if len(labels) == 0:
        print("No label to write into", filename)

    for l in labels:
        label = l[0][0]
        if label == "demenagement":
            print("writing label déménagement into", filename)
            json_object["Mail"][0]["Catégorie"][0]['Déménagement'] = 1
        if label == "releve":
            print("writing label relève de compteur into", filename)
            json_object["Mail"][0]["Catégorie"][0]['Relève de compteur'] = 1
        if label == "reclamation":
            print("writing label réclamation into", filename)
            json_object["Mail"][0]["Catégorie"][0]['Réclamation'] = 1
        if label == "contrat":
            print("writing label contrat into", filename)
            json_object["Mail"][0]["Catégorie"][0]['Contrat – Coordonnées personnelles'] = 1
        if label == "facture":
            print("writing label facture/paiement into", filename)
            json_object["Mail"][0]["Catégorie"][0]['Facture – Paiement'] = 1
        if label == "espace":
            print("writing label espace client into", filename)
            json_object["Mail"][0]["Catégorie"][0]['Espace client'] = 1

    f = open(os.path.join(checkpoint_directory, filename), "w")
    json.dump(json_object, f, ensure_ascii=False, indent=True)
    f.close()


"""
Returns true or false, depending if a mail has any label or not
"""


def mail_labeled(path):
    out = 0

    f = open(path, "r", encoding=encoding)
    json_object = json.load(f)
    f.close()

    out += json_object["Mail"][0]["Catégorie"][0]['Déménagement']
    out += json_object["Mail"][0]["Catégorie"][0]['Relève de compteur']
    out += json_object["Mail"][0]["Catégorie"][0]['Réclamation']
    out += json_object["Mail"][0]["Catégorie"][0]['Contrat – Coordonnées personnelles']
    out += json_object["Mail"][0]["Catégorie"][0]['Facture – Paiement']
    out += json_object["Mail"][0]["Catégorie"][0]['Espace client']

    return out > 0


"""
This functions is called after the labelization is done.

If a mail was labeled, it will be moved to the labeled directory
If a mail was not labeled, it will be moved to the unlabeled directory
"""


def labelization_done():
    print("All mails were labeled ! Saving labelization output...")
    for filename in os.listdir(checkpoint_directory):
        if filename == "." or filename == "..":
            continue
        else:
            if mail_labeled(os.path.join(checkpoint_directory, filename)):
                shutil.move(os.path.join(checkpoint_directory, filename),
                            os.path.join(output_directory_labeled, filename))
            else:
                shutil.move(os.path.join(checkpoint_directory, filename), os.path.join(
                    output_directory_unlabeled, filename))


"""
This function parses the data directory in order to show the
mails to the user.

For each mail, there are three important functions:
- read_mail: reading the mail's object and body
- input_labels: returns the labelization gave by user input
- write_label: writes the user's choice into a new json file
"""


def parse_mails():
    for filename in os.listdir(data_directory):
        if filename == "." or filename == "..":
            continue
        if os.path.exists(os.path.join(checkpoint_directory, filename)):
            print("Mail", filename, "already labeled.")
            continue
        else:
            read_mail(os.path.join(data_directory, filename))
            labels = input_label()
            write_label(filename, labels)
    labelization_done()
    shutil.rmtree(checkpoint_directory)


"""
Creates a directory
"""


def mkdir(path):
    try:
        os.mkdir(path)
    except OSError:
        print("Creation of the directory %s failed" % path)


"""
Checks the status of the directory of the user. Avoids any earasements.
"""


def data_directory_status():
    if not os.path.exists(data_directory):
        print("error: no data to parse (path: ./data/mails does not exists)")
        exit(1)

    if os.path.exists(output_directory):
        print("An output directory of this script already exists.")
        i = input("Do you wish to erase it ? [Y/n]")

        if i == "Y" or i == "y":
            shutil.rmtree(output_directory)
            print("Removed previous label directory.")
            print("Recreating directory")
            mkdir(output_directory)
            mkdir(output_directory_labeled)
            mkdir(output_directory_unlabeled)
        else:
            print("\n\nAborted !")
            exit(0)
    else:
        mkdir(output_directory)
        mkdir(output_directory_labeled)
        mkdir(output_directory_unlabeled)

    if os.path.exists(checkpoint_directory):
        print("Using previous checkpoint")
    else:
        mkdir(checkpoint_directory)


if __name__ == "__main__":

    data_directory_status()
    parse_mails()
