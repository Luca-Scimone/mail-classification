import os
import json


def to_json(raw_path, de, envoye, cc, objet, piece, corps):
    data = {}
    data['Mail'] = []

    data['Mail'].append({
        'De': de,
        'Envoyé': envoye,
        'Cc': cc,
        'Objet': objet,
        'Pièces jointes': piece,
        'Corps': corps
    })

    path = raw_path + ".json"

    with open(path, 'w') as outfile:
        json.dump(data, outfile)


def parse_mail(filename):
    head = 0
    de, envoye, cc, objet, piece, corps = "", "", "", "", "", ""

    with open("../data/raw_mails/" + filename) as fp:
        line = fp.readline()
        while line:
            if line[:3] == "De:":
                de = line[3:]
                head = 1

            if line[:7] == "Envoyé:":
                envoye = line[7:]
                head = 1

            if line[:3] == "Cc:":
                cc = line[3:]
                head = 1

            if line[:6] == "Objet:":
                objet = line[6:]
                head = 1

            if line[:15] == "Pièces jointes:":
                piece = line[15:]
                head = 1

            if head:
                head = 0
            else:
                corps += line

            line = fp.readline()

        return de, envoye, cc, objet, piece, corps


if __name__ == "__main__":
    directory = "../data/raw_mails"

    for filename in os.listdir(directory):
        if filename == "." or filename == "..":
            continue
        else:
            de, envoye, cc, objet, piece, corps = parse_mail(filename)
            to_json("../data/mails/" + filename, de,
                    envoye, cc, objet, piece, corps)
