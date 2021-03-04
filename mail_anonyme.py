# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import hashlib
import locale
import re
from typing import TextIO
import argparse

# ajouter un mot de civilité si non pris en compte. Attention Madame et madame ne sont pas équivalents.
CIVILITE = "(madame|Madame|monsieur|Monsieur|mr|Mr|mme|Mme|melle|Mlle)\s*.\s*"

# ajouter une formule si manquante. Insensible à la casse (Cordialement et cordialement sont équivalents)
END_OF_MAIL = "(cordialement|cdt|amicalement|sincèrement|sincère salutation|bien cordialement|bien " \
              "sincèrement|cordialement " \
              "vôtre|bien à vous|avec mes salutations)[,.;]?\s*[,.;]?\s*"
# Cette chaine définit par quoi sera remplacé les prénoms-noms. Attentions, les nombres et l'expéditeur ne sont
# pas concernés.
ANONYME = ' anonyme-anonyme '
ENCODE_READ = 'UTF-8'
ENCODE_WRITE = 'UTF-8'
# Don't edit bellow
# ---------------------------------------------------------------------------------- #
REGEX_MAIL = r'[^\s]*@[^\s]*'


# TODO
# si certains mots sont remplacés par anonyme, ajouter dans la liste suivante pour ne plus les remplacer
# Par exemple, si M.Albert Camus apprait, il ne sera plus supprimé
# EXCLUDE_WORDS = ['Albert Camus', 'De La Rochefoucault']

def parse() -> argparse.Namespace:
    """
    This function parses arguments from user command siline. It uses parseargs, a very simple Python module.
    Returns
    -------
    args : Simple subclass object returning by parse_args method that contains parsed attributes.
    """
    des: str = """Ce programme permet d'anonymiser les mails. Par exemple, prenons le mail suivant : "De : Wagner" """ \
               """ Bonjour Monsieur Machin. Le projet avec les élèves de TPS avance lentement mais spurement.  """ \
               """ Cordialement. Wagner. Ce mail sera donc remplacé par : "De : IDENTIFIANT_UNIQUE Bonjour Monsieur""" \
               """ anonyme. Le projet avec les élèves de TPS avence lentement mais sûrement. Cordialement. anonyme """

    # Start Parsing
    all_args: argparse.ArgumentParser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=des
    )

    # add argument to the parser

    hel: str = """Entrez le fichier à traiter. Le fichier doit ête en plain text et contient des mails.""" \
               """Un mail est défini comme une """ \
               """suite de phrases dont la première phrase est "de:" ou "De:" """
    all_args.add_argument("--file", required=True, help=hel)

    hel: str = """Sélectionner ce mode pour avoir des informations supplémentaires.NON IMPLEMENTER"""
    all_args.add_argument("--verbose", help=hel, action="store_true")

    args = all_args.parse_args()
    return args


def levenshtein(a, b):
    if not a:
        return len(b)
    if not b:
        return len(a)
    return min(levenshtein(a[1:], b[1:]) + (a[0] != b[0]),
               levenshtein(a[1:], b) + 1,
               levenshtein(a, b[1:]) + 1)


def hash_user(user: str):
    """
    :param user: It is a string to hash.
    :return: The hash of user in hexadecimal. The algorithm chosen is blake2
    """
    user_h = hashlib.blake2b(digest_size=32)
    user_utf8 = user.encode(encoding=ENCODE_WRITE)
    user_h.update(user_utf8)
    return user_h.hexdigest()


def process_mail(mail: str, fd: TextIO):
    """
    This function take a string, split it in sentences and remove from each sentences all confidential data. Finally,
    sentences are written in fd file after removing sensible information.
    :param mail: An entire string mail to process. A mail start with "de:Machin" and end with EOF or with another
    "de:autre_Machin".
    :param fd: It is the file where mails without confidential data are written.
    :return:
    """
    hash_link = dict()
    # print(mail)

    # we start to tackle special cases (lines that starts with 'de:','à:'...)
    # print(re.findall(r"(de\s*:\s*)([^\n]*)", mail, re.IGNORECASE))
    result = re.search(r"(de\s*:\s*)([^\n]*)", mail, re.IGNORECASE)
    if result:
        # on récupère le deuxième groupe
        user_from: str = result.group(2).strip()
        hash_link[user_from] = hash_user(user_from)
        mail = re.sub("{}".format(user_from), hash_link[user_from], mail)

    # The receiver have to be hide too. Sincce  there can be several receivers, we should use findall. Findall
    # return a list of tuple ! There are as many elements in the tuple as there are groups in the regex.
    results = re.findall(r"(à\s*:)([^\n]*)", mail, re.IGNORECASE)
    # print(re.findall("(à\\s*:)([^\n]*)", mail, re.IGNORECASE))
    for result in results:
        user_to = result[1].strip()
        hash_link[user_to] = hash_user(user_to)
        mail = re.sub("{}".format(user_to), hash_link[user_to], mail)

    # all people in CC are replaced with ANONYME string
    result = re.search(r"(cc\s*:)([^\n]*)", mail, re.IGNORECASE)
    if result:
        cc = result.group(2).strip()
        mail = re.sub("{}".format(cc), ANONYME, mail)

    # an email often finishes with "cordialement, best regards..." and then the name of the sender.
    result = re.search(END_OF_MAIL, mail, re.IGNORECASE)
    if result:
        mail = re.sub(r"{}([A-Z][a-zéà]*\s*)+".format(result.group()),
                      result.group() + ANONYME + "\n", mail)

    # replace all mail by anonymous string. Mail in metadata have already been processed.
    mail = re.sub(REGEX_MAIL, ANONYME, mail)

    # Match sensible data in corpus mail
    # match data as monsieur Machin Bidule or Mme. Machine or...
    # print(re.findall(r"{}\s*([A-Z][a-z]*\s*)+".format(CIVILITE), mail))
    # si CIVILITE est trop long a remplir, la distance de levenshtein pourrait etre utile
    mail = re.sub(r"{}\s*([A-Z][a-z]*\s*)+".format(CIVILITE), ANONYME + " ", mail)

    # Enfin, on affiche les derniers dont on n'est pas sûr
    regex_hash = "[a-z0-9]{32}"
    result = re.findall(r"[A-Z][\S]*\s*(?:[A-Z][\S]*\s*)+", mail)
    print("Les mots suivants n'ont pas été anonymisés et pourtant ce sont peut-être des prénoms :")
    for maybe_is_name in result:
        if not re.match(regex_hash, maybe_is_name):
            print(re.sub(r'\s', " ", maybe_is_name))
    print("\n")
    fd.write(mail)
    return hash_link


def main():
    # print(locale.getpreferredencoding(do_setlocale=True))
    fd = open("output", mode='w', encoding=ENCODE_WRITE)
    fd_link_hash = open("secret", mode='w', encoding=ENCODE_WRITE)
    my_args = parse()
    with open("data/mails/mail1.json", encoding='ascii') as test:
        lines = test.readlines()
        for line in lines:
            print(line)

    with open(my_args.file, encoding=ENCODE_READ) as f:
        mail = ""
        lines = f.readlines()
        hash_dict = dict()
        for line in lines:
            if line.lower().strip().startswith('de:'):
                # on traite le mail précédent
                hash_dict = process_mail(mail, fd)
                for key, value in hash_dict.items():
                    fd_link_hash.write('{}:{}\n'.format(key, value))
                mail = ""

            mail = mail + line

        # On traite le dernier mail
        hash_dict = process_mail(mail, fd)
        for key, value in hash_dict.items():
            fd_link_hash.write('{}:{}\n'.format(key, value))

    fd_link_hash.close()
    fd.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
