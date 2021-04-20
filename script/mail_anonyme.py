"""
Ce script permet d'anonymiser les mails pour le projet ingénieur.
Il s'appelle comme suit : python3 mail_anonyme.py --file f
Il lit alors le fichier f, extrait les mails et les anonymise (remplace par exemple les prénoms,
numéro de téléphone...). Il écrit les mails anonymisés dans un fichier output. Le destinataire et l'émetteur du mail
sont hashés. La correspondance strinh/hash_string est écrite dans un fichier 'secret'.

Pour un directory : python3 mail_anonyme.py --dir d --rec
"""
import csv
import hashlib
import os
import re
from typing import TextIO
import argparse
from random import *
import stanza
from langdetect import detect

# ajouter un mot de civilité si non pris en compte. Attention Madame et madame ne sont pas équivalents.
# CIVILITE = r"(?:madame|Madame|monsieur|Monsieur|mr|Mr|mme|Mme|melle|Mlle|M|m)\s*.\s*"

# ajouter une formule si manquante. Insensible à la casse (Cordialement et cordialement sont équivalents)
# END_OF_MAIL = r"(cordialement|cdt|amicalement|sincèrement|sincère salutation|bien cordialement|bien " \
#               r"sincèrement|cordialement " \
#              r"vôtre|bien à vous|avec mes salutations)[,.;]?\s*[,.;]?\s*"
# Cette chaine définit par quoi sera remplacé les prénoms-noms. Attentions, les nombres et l'expéditeur ne sont
# pas concernés.
ANONYME = ' anonyme-anonyme '
ANONYME_PERSONNE = ' anonyme-personne '
ANONYME_LOCALISATION = ' anonyme-localisation '
ANONYME_NUMBER = " anonyme_number "
ANONYME_MAIL = " anonyme_mail "

RANDOM_NUMBER = str(randint(0, 9))
ENCODE_READ = 'cp1252'

# Don't edit bellow
# ---------------------------------------------------------------------------------- #
ENCODE_WRITE = 'utf8'
REGEX_MAIL = r'[^\s]*@[\S]*'
NAME_RE = r"[A-Z][A-Za-zéàè]+"
NAMES_RE = r"(?:" + NAME_RE + r"[ ]+){1,3}(?:" + NAME_RE + r")"
FROM_RE = r"(de\s*:\s*)([^{}]*)".format(os.linesep)
PHONE_NUMBER_RE = r"[+]?[(]?[0-9]{2}[)]?[-\s.]?[0-9]?[-\s.]?(?:[0-9][-\s.]?){6,10}[0-9]"
TO_RE = r"(à\s*:)([^{}]*)".format(os.linesep)
CC_RE = r"(cc\s*:)([^{}]*)".format(os.linesep)
NUMERO = r"[0-9]"
MAJUSCULE_TEXT = r"[ ][A-Z][A-Za-zéàè]+([ ]|[\n])"

NLP_FR = stanza.Pipeline(lang="fr", processors='tokenize,ner',
                         dir="data", use_gpu=True, pos_batch_size=3000)
NLP_EN = stanza.Pipeline(lang="en", processors='tokenize,ner',
                         dir="data", use_gpu=True, pos_batch_size=3000)
NLP_DE = stanza.Pipeline(lang="de", processors='tokenize,ner',
                         dir="data", use_gpu=True, pos_batch_size=3000)

anonymized_words = []
analysed_words = []

if not os.path.isdir("data"):
    os.mkdir("data")

if not os.path.isdir(os.path.join("data", "en")):
    stanza.download('en', model_dir=os.path.join(os.getcwd(), "data"))

if not os.path.isdir(os.path.join("data", "fr")):
    stanza.download('fr', model_dir=os.path.join(os.getcwd(), "data"))

if not os.path.isdir(os.path.join("data", "de")):
    stanza.download('de', model_dir=os.path.join(os.getcwd(), "data"))


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
    all_args.add_argument("--file", help=hel)

    hel: str = """Entrez le dossier à traiter. Le dossier contient des fichiers texte d'extension quelconque.""" \
               """Attention, les sous-dossiers ne sont pas traités.""" \
               """Un mail est défini comme une """ \
               """suite de phrases dont la première phrase est "de:" ou "De:" """

    all_args.add_argument("--dir", help=hel)

    hel: str = """Lire récursivement un dossier. A utiliser avec --dir."""
    all_args.add_argument("--rec", help=hel, action="store_true")

    hel: str = """TOUS les fichiers traités doivent être en csv."""
    all_args.add_argument("--csv", help=hel, action="store_true")

    hel: str = """Entrez un chemin vers un fichier ou un dossier de sortie. Si le chemin est celui d'un dossier,""" \
               """ le script va scinder les mails en plusieurs fichiers.""" \
               """ par défault, la sortie est un seul fichier appelé output"""
    all_args.add_argument("--out", help=hel)

    hel: str = """Entrez un entier entre 1 et 2 """ \
               """Choisir le niveau d'anonymisation des mails."""
    all_args.add_argument("--level", help=hel, type=int)

    hel: str = """Choisir l'encodage de lecture des fichiers contenant les mails. Encodage par défaut : cp1252."""
    all_args.add_argument("--readenc", help=hel, default="cp1252")

    hel: str = """Séléctionner ce mode pour afficher les mots anonymisés par le script pour chaque mail"""
    all_args.add_argument("--verbose", help=hel, action="store_true")

    args = all_args.parse_args()
    return args


def hash_user(user: str):
    """
    :param user: It is a string to hash.
    :return: The hash of user in hexadecimal. The algorithm chosen is blake2
    """
    user_h = hashlib.blake2b(digest_size=32)
    user_encode = user.encode(encoding=ENCODE_WRITE)
    user_h.update(user_encode)
    return user_h.hexdigest()


def stanza_label(depth_analysis_str: str, nlp, verbose_on, depth=3, min_misc_token_len=2):
    if depth == 0:
        return

    doc = nlp(depth_analysis_str)

    for token in doc.ents:
        if token.text in analysed_words or [token.text, token.type] in anonymized_words:
            continue

        if verbose_on:
            print("> Depth=", 3 - depth)
            print (token)

        if token.type == "PER" or token.type == "PERSON":
            anonymized_words.append([token.text, "ANONYME_PERSONNE"])

        if token.type == "LOC":
            anonymized_words.append([token.text, "ANONYME_LOC"])

        analysed_words.append(token.text)
        stanza_label(token.text, nlp, depth - 1)


def process_mail(mail: str, fd: TextIO, hash_link: dict, verbose_on):
    """
    This function take a string, split it in sentences and remove from each sentences all confidential data. Finally,
    sentences are written in fd file after removing sensible information.

    :param mail: An entire string mail to process. A mail start with "de:Machin" and end with EOF or with another
    "de:autre_Machin".

    :param fd: It is the file where mails without confidential data are written.
    hash_link : A dictionary that makes correspondences between hash_string and string.

    :param hash_link:
    :return:  A dictionary that makes correspondences between hash_string and string.
    """

    if mail.strip() == "":
        return hash_link

    langue = detect(mail)
    if langue != 'en' and langue != 'fr' and langue != "de":
        print("Un mail contient une langue inconnue et ne sera donc pas traité. La langue est {}".format(langue))
        return hash_link

    if langue == "en":
        stanza_label(mail, NLP_EN, verbose_on)
    if langue == "fr":
        stanza_label(mail, NLP_FR, verbose_on)
    if langue == "de":
        stanza_label(mail, NLP_DE, verbose_on)

    if verbose_on:
        print("Les mots suivant ont été anonymisés:")
        print(20*'=')
        for word in anonymized_words:
            print("\"" + word[0] + "\"", end=" ")
            mail = re.sub(word[0], word[1], mail)
        print("\n")
        print(20*'=')
    else:
        for word in anonymized_words:
            mail = re.sub(word[0], word[1], mail)

    anonymized_words.clear()
    analysed_words.clear()

    # Delete all number in mail
    results = re.findall(NUMERO, mail, re.IGNORECASE)
    for result in results:
        mail = re.sub("{}".format(result), RANDOM_NUMBER, mail)
    """
    # Catch special cases (lines that starts with 'de:','à:'...)
    result = re.search(FROM_RE, mail, re.IGNORECASE)
    if result:
        # on récupère le deuxième groupe
        # on strip pour ne pas hasher les espaces !
        user_from: str = result.group(2).strip()
        if user_from != "":
            hash_link[user_from] = hash_user(user_from)
            mail = re.sub("{}".format(user_from), hash_link[user_from], mail)

    # The receiver have to be hide too. Since  there can be several receivers, we should use findall.
    results = re.findall(TO_RE, mail, re.IGNORECASE)
    for result in results:
        user_to = result[1].strip()
        if user_to != "":
            hash_link[user_to] = hash_user(user_to)
            mail = re.sub("{}".format(user_to), hash_link[user_to], mail)

    # all people in CC are replaced with ANONYME string
    result = re.search(CC_RE, mail, re.IGNORECASE)
    if result:
        cc = result.group(2).strip()
        if cc != "":
            mail = re.sub("{}".format(cc), ANONYME, mail)
    """
    # replace all mail by anonymous string. Mail in metadata have already been processed.
    mail = re.sub(REGEX_MAIL, ANONYME_MAIL, mail)

    # Enfin, on affiche les derniers dont on n'est pas sûr
    result = re.findall(NAMES_RE, mail)

    if result:
        print("Les mots suivants n'ont pas été anonymisés et pourtant ce sont peut-être des prénoms :")
        for maybe_is_name in result:
            print(re.sub(r'\s', " ", maybe_is_name))
        print("\n")
    fd.write(mail)

    return hash_link


def process_file_csv(file_input: str, output: str, hash_dict: dict, file_cnt, verbose_on):
    titles = []

    with open(file_input, encoding=ENCODE_READ) as csv_f:
        csv_reader = csv.reader(csv_f)
        first_line = next(csv_reader)

        for title in first_line:
            if re.search(r"\s*de", title, re.IGNORECASE):
                titles.append("de: ")
            elif re.search(r"\s*cc", title, re.IGNORECASE):
                titles.append("cc: ")
            elif re.search(r"\s*cci", title, re.IGNORECASE):
                titles.append("cci: ")
            elif re.match(r"\s*a", title, re.IGNORECASE):
                titles.append("A: ")
            elif re.search(r"\s*objet", title, re.IGNORECASE):
                titles.append("objet: ")
            elif re.search(r"\s*corps", title, re.IGNORECASE):
                titles.append("corps: ")
            else:
                titles.append("unknown: ")

        mail_cnt = 0
        for row in csv_reader:
            mail = ""
            file_output = open(
                os.path.join(output, "mail_" + str(file_cnt) + "_" + str(mail_cnt)), mode='w',
                encoding=ENCODE_WRITE)
            file_output.write(file_input + "\r\n")

            for i in range(len(row)):
                mail += titles[i] + row[i] + "\r\n"

            hash_dict = process_mail(mail, file_output, hash_dict, verbose_on)

            file_output.close()
            mail_cnt += 1

        return hash_dict, file_cnt + 1


def process_file(file_input: str, output: str, hash_dict: dict, file_cnt, is_csv, verbose_on):
    if is_csv:
        hash_dict, file_cnt = process_file_csv(
            file_input, output, hash_dict, file_cnt, verbose_on)
        return hash_dict, file_cnt

    else:
        hash_dict, file_cnt = process_file_txt(
            file_input, output, hash_dict, file_cnt, verbose_on)
        return hash_dict, file_cnt


def process_file_txt(file_input: str, output: str, hash_dict: dict, file_cnt, verbose_on):
    """
    This function take a file_input fd descriptor, open it, parse mails in, and process each mail by calling
    process_mail. A mail is a text starting by FROM where FROM is a global variable defined at start at this code.
    Parameters
    ----------
    file_input The file that contains mail.
    output Can be either a file descriptor or a folder path (cf. description of the main function)
    file_secret A file that links hashed sensible data and the non hashed one.
    hash_dict A structure that contains links betweeen hashed sensible data and the non hashed one.

    Returns A dict that contains links betweeen hashed sensible data and the non hashed one.
    The data returned contains the new links and old links !
    -------

    """
    with open(file_input, encoding=ENCODE_READ) as f:
        mail = ""

        lines = f.readlines()
        mail_cnt = 0

        for line in lines:
            if re.search(r'de\s*:', line.strip(), re.IGNORECASE):
                if mail_cnt > 0:
                    # on traite le mail précédent
                    file_output = open(
                        os.path.join(output, "mail_" + str(file_cnt) + "_" + str(mail_cnt)), mode='w',
                        encoding=ENCODE_WRITE)
                    file_output.write(file_input + "\r\n")
                    hash_dict = process_mail(
                        mail, file_output, hash_dict, verbose_on)
                    mail = ""
                    file_output.close()
                mail_cnt += 1

            mail = mail + line

        # On traite le dernier mail
        file_output = open(
            os.path.join(output, "mail_" + str(file_cnt) + "_" + str(mail_cnt)), mode='w', encoding=ENCODE_WRITE)
        file_output.write(file_input + "\r\n")
        hash_dict = process_mail(mail, file_output, hash_dict, verbose_on)
        file_output.close()

        file_cnt = file_cnt + 1
        return hash_dict, file_cnt


def main(fd_secret: TextIO):
    """
    This is the main function. It calls parse function that parses user arguments, check the legality of them and
    anonymize mails contained in file or directory given by user.
    Parameters
    ----------
    output : Usualy a file descriptor where all mails without sensible data will be written.
    [!] In case of the --out option; output can be a path to a folder; meaning it will not
    be a file descriptor but a string. This will be tested in process_file
    fd_secret : File where correspondences between string/hash_string will be written

    Returns
    -------

    """
    # print(locale.getpreferredencoding(do_setlocale=True))

    my_args = parse()
    check_dependency(my_args)

    hash_dict = dict()
    file_cnt = 0
    output: str = ""

    if my_args.readenc:
        ENCODE_READ = my_args.readenc

    if my_args.out:
        output = str(my_args.out)
        if not os.path.isdir(output):
            os.mkdir(output)

    if not my_args.out:
        output = "output"
        if not os.path.isdir("output"):
            os.mkdir("output")

    if my_args.file:
        hash_dict, file_cnt = process_file(
            my_args.file, output, hash_dict, file_cnt, my_args.csv, my_args.verbose)

    elif my_args.dir and my_args.rec:
        result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(
            my_args.dir) for f in filenames]
        for file in result:
            hash_dict, file_cnt = process_file(
                file, output, hash_dict, file_cnt, my_args.csv, my_args.verbose)

    elif my_args.dir:
        with os.scandir(my_args.dir) as files:
            for file in files:
                hash_dict, file_cnt = process_file(
                    os.path.join(file), output, hash_dict, file_cnt, my_args.csv, my_args.verbose)

    for key, value in hash_dict.items():
        fd_secret.write('{}:{}\n'.format(key, value))


def check_dependency(my_args):
    if not my_args.file and not my_args.dir:
        print("L'option --dir ou --file doit etre précisé")
        exit(1)

    if my_args.file and my_args.dir:
        print("L'option --dir et --file ne peuvent pas etre utilisé en meme temps")
        exit(1)

    if my_args.file and my_args.rec:
        print("L'option --rec est réservé au répertoire et ne peut pas être utilisé avec un fichier")
        exit(1)

    if my_args.out:
        if os.path.islink(my_args.out) or os.path.isfile(my_args.out):
            print("error: Please provide a directory for --out")
            exit(1)
        elif os.path.isdir(my_args.out):
            print(f"Les mails seront écrits dans {str(my_args.out)}")
        else:
            print("Path error with --out option. Does the directory exist ?")
            exit(1)


if __name__ == "__main__":
    fid_secret = open("secret", mode='w', encoding=ENCODE_WRITE)

    main(fid_secret)
    fid_secret.close()