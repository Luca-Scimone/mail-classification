import os
import json
import re


def to_json(raw_path, de, envoye, cc, objet, piece, corps):
    data = {'Mail': []}

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
        json.dump(data, outfile, ensure_ascii=False, indent=True)


def parse_mail(filename):
    de, envoye, cc, objet, piece, corps = "", "", "", "", "", ""

    with open("./data/raw_mails/" + filename) as fp:
        lines = fp.readlines()
        for line in lines:

            if re.search(re.compile(r'(?i)De[ ]*:'), line):
                de = re.sub(r'(?i)De[ ]*:', '', line, 1)
                continue

            if re.search(re.compile(r'(?i)Envoyé[ ]*:'), line):
                envoye = re.sub(r'(?i)Envoyé[ ]*:', '', line, 1)
                continue

            if re.search(re.compile(r'(?i)Cc[ ]*:'), line):
                cc = re.sub(r'(?i)Cc[ ]*:', '', line, 1)
                continue

            if re.search(re.compile(r'(?i)Objet[ ]*:'), line):
                objet = re.sub(r'(?i)Objet[ ]*:', '', line, 1)
                continue

            if re.search(re.compile(r'(?i)Pièces Jointes[ ]*:'), line):
                piece = re.sub(r'(?i)Pièces Jointes[ ]*:', '', line, 1)
                continue

            corps += line

        return de, envoye, cc, objet, piece, corps


if __name__ == "__main__":
    directory = "./data/raw_mails"
    if not os.path.exists("./data/mails"):
        os.mkdir("./data/mails")

    for filename in os.listdir(directory):
        if filename == "." or filename == "..":
            continue
        else:
            de, envoye, cc, objet, piece, corps = parse_mail(filename)
            to_json("./data/mails/" + filename, de,
                    envoye, cc, objet, piece, corps)
