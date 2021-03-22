# Importing Libraries
import json
import sys
import os

directory = "./data/mails/"

if len(sys.argv) != 3:
    print("Wrong arguments.")
    print("Usage: python3 ./data_processing/to_json.py [ENCODING]")
    exit (1)

f1 = str(sys.argv[1])
f2 = str(sys.argv[2])

#code
def category(file_json, num):
    l=[]
    for msg in file_json['Mail']:
        for val in msg['Catégorie']:
            l.append(val['Mon déménagement'])
            l.append(val['Ma relève de compteur'])
            l.append(val['Je veux faire une réclamation '])
            l.append(val['Mon contrat – Mes coordonnées personnelles'])
            l.append(val['Ma facture – Mon paiement '])
            l.append(val['Mon Espace client'])

            print("List number",num, l)
        return l

def dist(l1, l2):
    val = 0
    for i in range(len(l1)):
        if ( l1[i] != l2[i]):
            val += 1
    return val

def diff(file1, file2):
    json_f1 = open(file1)
    json_f2 = open(file2)
    data1 = json.load(json_f1)
    data2 = json.load(json_f2)

    l1 = category(data1, 1)
    l2 = category(data2, 2)

    for i in range(len(l1)):
        if ( l1[i] != l2[i]):
            print("Differences between labels")
            a = dist(l1, l2)
            print ( "The value of the difference is :", a)
            data1.close()
            data2.close()
            return 0

    print("Same Labels ")
    data1.close()
    data2.close()
    return 0

    
diff(f1, f2)
