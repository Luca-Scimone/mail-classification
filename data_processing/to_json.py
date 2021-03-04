import os
import json


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
    head = 0
    de, envoye, cc, objet, piece, corps = "", "", "", "", "", ""

    with open("./data/raw_mails/" + filename) as fp:
        lines = fp.readlines()
        for line in lines:

            line_split = line.split(sep=':')

            if line.strip().startswith("De:"):
                de = line_split[1]
                head = 1

            if line.strip().startswith("Envoyé:"):
                envoye = line_split[1]
                head = 1

            if line.strip().startswith("Cc:"):
                cc = line_split[1]
                head = 1

            if line.strip().startswith("Objet:"):
                objet = line_split[1]
                head = 1

            if line.strip().startswith("Pièces jointes:"):
                piece = line_split[1]
                head = 1

            if head:
                head = 0
            else:
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
