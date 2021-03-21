"""
This script allows the user to manualy label mails.
The script reads the directory ./data/mails/ and adds a
label under Catégorie inside a new directory ./data/labeled_mails/.

Dependecies:

pip install fast-autocomplete
pip install fast-autocomplete[levenshtein]
"""

import os
import time
import sys
import codecs
import json
import readchar
from fast_autocomplete import AutoComplete

words = {"demenagement": {}, "releve": {}, "reclamation": {}, "contrat": {}, "facture" : {}, "espace" : {}}
autocomplete = AutoComplete(words=words)

if len(sys.argv) != 2:
    print("Wrong arguments.")
    print("Usage: python3 ./Labelization/add_labels/add_labels.py [ENCODING]")
    exit(1)

# The URL containing the data
encoding = str(sys.argv[1])


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


def usage ():
    print("* Déménagement (label:" + color.BOLD +  " déménagement" + color.END + ")")
    print("* Relève de compteur (label:" + color.BOLD +  " relève" + color.END + ")")
    print("* Réclamation (label:" + color.BOLD +  " réclamation" + color.END + ")")
    print("* Contrat / Coordonnées personnelles (label:" + color.BOLD +  " contrat" + color.END + ")")
    print("* Ma facture / Mon paiement (label:" + color.BOLD +  " facture" + color.END + ")")
    print("* Mon espace client (label:" + color.BOLD +  " espace" + color.END + ")")
    print("* ENTER -- Prochain mail")
    print("* TAB -- Ajout d'un label supplémentaire")
    print("* SUPR -- Supprimer le dernier label ajouté")
    print("* CNTRL-C -- Quitter")    


def read_mail (filename):
    with codecs.open(filename, 'r', encoding='utf8') as f:
        data_json = json.load(f)

        for msg in data_json['Mail']:
            corps = msg['Corps']
            obj = msg['Objet']

        print(80*'=')
        print (color.BOLD + color.RED + obj + color.END + color.END)
        print(80*'=')
        print (corps)
        print(80*'=')


def input_label ():
    usage ()
    labels = []

    while (1):
        print("Label:", end = " ", flush=True)
        c = ""
        prev_auto_completion = ""
        user_input = ""

        while (c != repr('\t')):
            if (c == repr('\r')):
                break
            if (c == repr('\x03')):
                print ("\n\nAborted !")
                exit (0)
            if ( c == repr('\x7f')):
                if (len(labels) > 0):
                    print("Removed label:",  color.BOLD, labels[-1][0][0], color.END)
                    labels.pop()
                break

            c = repr(readchar.readchar())
            user_input += c[1:-1]
            
            auto_completion = autocomplete.search(word=user_input, max_cost=3, size=3)

            if (len(auto_completion) != 1):
                print (c[1:-1], end = "", flush=True)
                continue

            if prev_auto_completion == "":
                print ("-- added label: ", color.BOLD, auto_completion [0][0], color.END)
                if auto_completion not in labels:
                    labels.append(auto_completion)
                prev_auto_completion = auto_completion
            
            if prev_auto_completion != auto_completion:
                print (c[1:-1], end = "", flush=True)
                prev_auto_completion = auto_completion

        if (c == repr('\r')):
            if len(labels):
                print("Added labels: ")
                for label in labels:
                    print(color.BOLD + label[0][0] + color.END, end = " ", flush=True)
                print("\nLoading next mail...") 
                break
            else:
                print("No labels added.")
                print("\nLoading next mail...")
                break

        print ("", flush=True)

    return labels


def write_label(filename, data_directory, labeled_data_directory, labels):
    f = open(data_directory + filename, "r", encoding=encoding)
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

    f = open(labeled_data_directory + filename, "w")
    json.dump(json_object, f, ensure_ascii=False, indent=True)
    f.close()


def parse_mails (data_directory, labeled_data_directory):
    for filename in os.listdir(data_directory):
        if filename == "." or filename == "..":
            continue
        if os.path.exists(labeled_data_directory + filename):
            print("Mail", filename, "already labeled.")
            continue
        else:
            read_mail (data_directory + filename)
            labels = input_label ()
            write_label (filename, data_directory, labeled_data_directory, labels)


if __name__ == "__main__":
    data_directory = "./data/mails/"
    directory = "./data/labeled_mails/"
    
    try:
        os.mkdir(directory)
    except OSError:
        print ("Creation of the directory %s failed" % directory)

    if not os.path.exists(data_directory):
        print("error: no data to parse (path: ./data/mails does not exists)")
        exit (1)

    parse_mails (data_directory, directory)