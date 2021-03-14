import os
import json
import re
import sys

if len(sys.argv) != 2:
    print("Wrong arguments.")
    print("Usage: python3 ./data_processing/to_json.py [ENCODING]")
    exit (1)

# The URL containing the data
encoding = str(sys.argv[1])



def to_json(raw_path, de, envoye, cc, objet, piece, a, corps):
    data = {'Mail': []}

    data['Mail'].append({
        'De': de,
        'Envoyé': envoye,
        'À': a,
        'Cc': cc,
        'Objet': objet,
        'Pièces jointes': piece,
        'Corps': corps
    })

    path = raw_path + ".json"
    with open(path, 'w') as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=True)


def parse_mail(filename):
    de, envoye, cc, objet, piece, a, corps = "", "", "", "", "", "", ""

    with open("./data/raw_mails/" + filename, encoding=encoding) as fp:
        lines = fp.readlines()
        for line in lines:

            if de == "":
                match = re.search(re.compile(r'(?i)De[ ]*:'), line)
                if match:
                    de = line[match.end():]
                    continue

            if envoye == "":
                match = re.search(re.compile(r'(?i)Envoyé[ ]*:'), line)
                if match:
                    envoye = line[match.end():]
                    continue

            if cc == "":
                match = re.search(re.compile(r'(?i)Cc[ ]*:'), line)
                if match:
                    cc = line[match.end():]
                    continue

            if objet == "":
                match = re.search(re.compile(r'(?i)Objet[ ]*:'), line)
                if match:
                    objet = line[match.end():]
                    continue

            if piece == "":
                match = re.search(re.compile(r'(?i)Pièces Jointes[ ]*:'), line)
                if match:
                    piece = line[match.end():]
                    continue

            if a == "":
                match = re.search(re.compile(r'(?i)À[ ]*:'), line)
                if match:
                    a = line[match.end():]
                    continue

            corps += line

        return de, envoye, cc, objet, piece, a, corps


if __name__ == "__main__":
    directory = "./data/raw_mails"
    if not os.path.exists("./data/mails"):
        os.mkdir("./data/mails")

    for filename in os.listdir(directory):
        if filename == "." or filename == "..":
            continue
        else:
            de, envoye, cc, objet, piece, a, corps = parse_mail(filename)
            to_json("./data/mails/" + filename, de,
                    envoye, cc, objet, piece, a, corps)
