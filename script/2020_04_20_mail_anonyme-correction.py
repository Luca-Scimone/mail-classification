"""
Ce script permet d'anonymiser les mails pour le projet ingénieur.
Il s'appelle comme suit : python3 mail_anonyme.py --file f
Il lit alors le fichier f, extrait les mails et les anonymise (remplace par exemple les prénoms,
numéro de téléphone...). Il écrit les mails anonymisés dans un fichier output. Le destinataire et l'émetteur du mail
sont hashés. La correspondance strinh/hash_string est écrite dans un fichier 'secret'.

Pour un directory : python3 mail_anonyme.py --dir d --rec
"""
from tqdm.auto import tqdm
import string
import csv
import hashlib
import os
import re
from typing import TextIO
import argparse
from random import *
from warnings import formatwarning
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


names_dataset = []

forbiden_names = ["avis", "sans", "sera", "mars", "aura"]

print("Reading the french names data set ...")

if not os.path.exists("Prenoms.csv"):
    print ("Error: Prenoms.csv was not found.")
    exit (1)
else:
    regex = re.compile('[^a-zA-Z]')
    with open("Prenoms.csv", encoding=ENCODE_READ, errors="ignore") as csv_f:
        for row in csv_f:
            name = row.split(';')[0]
            name = regex.sub('', name)
            if len(name) < 4 or name in names_dataset or name in forbiden_names:
                continue
            names_dataset.append(name)

print ("Done reading the french names data set ... ")


delimiters = [' ', '\r', '\t', '\n']


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

    hel: str = """Séléctionner ce mode pour afficher toutes les analyses faites par stanza"""
    all_args.add_argument("--debug", help=hel, action="store_true")

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




def get_name_range (begining, end, mail) :
    """
    This function receives an input of a starting position of a name and
    an ending position of a name. With this information, this function needs
    to remove all WORDS that are before the starting position and after (see
    the example in the description of the function brute_remove_names)

    There are some special cases:
        If the begining position is already a word (example: bonjourjean) and the
        endining position is already a word (example: jeanbon) then nothing is done
        because some names are contained in some words which does not correspond
        to something worth anonimizing.

        If the word is isolated ([SPACE]Jean[SPACE]) we go left and right. While we
        are reading spaces, we do nothing, when a character that is not a space is read
        we enter the state 'reading_word'. In this state, if a space is read, then we
        have found the word before or after the name. 
        Example for Jean Dupont
            - Reading the space between Jean and Dupont -> continue
            - Reading 'D' -> reading_word = True
            - Reading 'u' -> reading_word = True
            - Reading 'p' -> reading_word = True
            - Reading 'o' -> reading_word = True
            - Reading 'n' -> reading_word = True
            - Reading 't' -> reading_word = True
            - Reading ' ' -> reading_word is True and we read a space -> break.

        Note: A special case is the character ':', because we don't want this script to
        modify the structure of the mail (ie. we don't want to change the cc:, De: ect...)
        The character ':' therefore means the search should stop immediately.
        This means that :jean dupond: is likely to fail.
    """
    left_idx, right_idx = begining - 1, end + 1

    reading_word = False

    if left_idx < 0:
        Left_Test = True
    else:
        Left_Test = mail[left_idx] in string.ascii_lowercase or mail[left_idx] in string.ascii_uppercase 
        
    if right_idx >= len(mail):
        Right_Test = True
    else:
        Right_Test = mail[right_idx] in string.ascii_lowercase or mail[right_idx] in string.ascii_uppercase

    if Left_Test or Right_Test :
        return 0,0

    while Left_Test == False and left_idx >= 0:
        if mail[left_idx] == ':':
            left_idx -= 1
            break
        if mail[left_idx] in delimiters and reading_word == False:
            left_idx -= 1
        elif mail[left_idx] not in delimiters:
            reading_word = True
            left_idx -= 1
        elif mail[left_idx] in delimiters and reading_word == True:
            left_idx -= 1
            break
    
    reading_word = False

    while Right_Test == False and right_idx < len(mail):
        if mail[right_idx] == ':':
            right_idx += 1
            break
        if mail[right_idx] in delimiters and reading_word == False:
            right_idx += 1
        elif mail[right_idx] not in delimiters:
            reading_word = True
            right_idx += 1
        elif mail[right_idx] in delimiters and reading_word == True:
            right_idx += 1
            break
    
    return left_idx + 1, right_idx - 1
        



def brute_remove_names (mail, verbose_on):
    """
    This function goes through the names dataset and tries to find a name in the mail.
    If a mail is found, the initial char and the last char that should be remove are
    given by the function get_name_range. We want to remove any word that is before
    the name that was found, and after:

                    -suis-    [Jean] -Dupont-
                    removed   found  removed
                         and also removed

    :param mail: The string that will be analyzed (ie. the mail).

    :param verbose_on: An integer stating the level of information the user wants.
    """
    # Removing capital letters to match the dataset
    cleared_mail = " " + mail.lower() + " "

    for name in names_dataset:
        # Testing if a name of the dataset is in the mail
        for m in re.finditer(name, cleared_mail):
            starting_pos = m.start()
        
            left, right = get_name_range (starting_pos, starting_pos + len(name) - 1, cleared_mail)

            if left == right:
                continue

            if mail[left:right].find("ANONYME_PER") == -1 and mail[left:right].find("ANONYME_LOC") == -1: 
                if verbose_on:
                    print (79*'=')
                    print ("\n\033[1mCet ensemble de mots a été anonymisé puisqu'il contient le prénom\033[91m", name , "\033[0m\n")
                    print ('\033[95m', end="")
                    print (mail[left:right])
                    print ('\033[0m\n')
                anonymized_words.append([mail[left:right], " ANONYME_PER ", 0])
                # mail = mail.replace(mail[left:right], "ANONYME_PER")
                
    return mail


def stanza_label(depth_analysis_str: str, nlp, verbose_on, depth=3):
    """
    This function passes the mail through the NER neural network. If the result is 
    MISC; the string is recursivly given to this function again, in order to capture
    other possibles names or locations nested in the MISC result.

    For optimization, all words that need to be removed or that were tested are inserted
    in arrays and so: 1) the recursion stops when it is looping on the same word 2) the
    removal of the words in the mail is only done one time 

    :param depth_analysis_str: The string that will be analyzed by the NER network.

    :param nlp: The neural network per say 

    :param verbose_on: An integer stating the level of information the user wants.

    :param depth: The maximum number of recussions allowed in this function
    """
    if depth == 0:
        return

    doc = nlp(depth_analysis_str)

    for token in doc.ents:
        if verbose_on == 2:
            print("> Depth=", 3 - depth)
            print (token)

        if token.type == "PER" or token.type == "PERSON":
            anonymized_words.append([token.text, " ANONYME_PER ", 1])

        elif token.type == "LOC":
            anonymized_words.append([token.text, " ANONYME_LOC ", 1])

        elif token.text not in analysed_words:
            analysed_words.append(token.text)
            stanza_label(token.text, nlp, verbose_on, depth - 1)


def treatement_of_anonymized_words (list1):
    """
    This function removes any redundant anonymized string from the array
    list1 (for optimization purposes). It also tests if the string that needs
    to be remove is alphabetical, do prevent the anonymization of every spaces
    in the mail for example

    :param list1: A list of lists organized in tuple of 3 elements:
    ["String that needs to be anonymized", 
    "The replacement", 
    An integer marking where the string was anonymized]

    The first element is simply the string that will be removed, then we have
    the string that will replace the removed string (most of the time ANONYM_PER).
    Finaly the integer is used for the verbose option: if it is at 0, the string
    was anonymized by the brute force tehcnique using the Prenoms.csv dataset;
    if it is at 1, it was anonymized by NER (therefore, we can print how the string
    was anonymized when --verbose is on)

    :return:  Returns the final list of strings that need to be anonymized
    """
    unique_list = []

    for x in list1:
        # First test verifies that the string that needs to be removed is alphabetical
        if x[0].lower().islower() and x not in unique_list:
            unique_list.append(x)

    return  unique_list


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
        print("Attention: un mail contient une langue inconnue et ne sera donc pas traité par NER. La langue est {}".format(langue))
    else:
        if langue == "en":
            stanza_label(mail, NLP_EN, verbose_on)
        if langue == "fr":
            stanza_label(mail, NLP_FR, verbose_on)
        if langue == "de":
            stanza_label(mail, NLP_DE, verbose_on)
        
    # New brute force technique to remove names
    mail = brute_remove_names (mail, verbose_on)

    if verbose_on:
        if len(anonymized_words):
            print (79*'=')
            print("\n\033[1mLes mots suivant ont été anonymisés par le réseau de neurones NER:\033[0m\n")
        print ('\033[95m', end="")
        for word in treatement_of_anonymized_words (anonymized_words):
            if word[2] == 1: # Brute Force results don't need to be printed
                print("\"" + word[0] + "\"", end=" ")
            mail = mail.replace(word[0], word[1])
        print ('\033[0m\n')
    else:
        for word in treatement_of_anonymized_words (anonymized_words):
            mail = mail.replace(word[0], word[1])  


    anonymized_words.clear()
    analysed_words.clear()

    # Delete all number in mail
    results = re.findall(NUMERO, mail, re.IGNORECASE)
    for result in results:
        mail = re.sub("{}".format(result), RANDOM_NUMBER, mail)
    
    # replace all mail by anonymous string. Mail in metadata have already been processed.
    mail = re.sub(REGEX_MAIL, ANONYME_MAIL, mail)

    fd.write(mail)

    return hash_link


def process_file_csv(file_input: str, output: str, hash_dict: dict, file_cnt, verbose_on):
    titles = []
    print ("Starting anonymization... (this might take a while)")

    with open(file_input, encoding=ENCODE_READ, errors="ignore") as csv_f:
        row_count = sum(1 for _ in csv.reader(csv_f))
        csv_f.close()

    with open(file_input, encoding=ENCODE_READ, errors="ignore") as csv_f:
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

        for mail_cnt in tqdm(range(row_count - 1)):
            row = next(csv_reader)
            mail = ""
            file_output = open(
                os.path.join(output, "mail_" + str(file_cnt) + "_" + str(mail_cnt)), mode='w',
                encoding=ENCODE_WRITE, errors="ignore")
            file_output.write(file_input + "\r\n")

            for i in range(len(row)):
                mail += titles[i] + row[i] + "\r\n"

            hash_dict = process_mail(mail, file_output, hash_dict, verbose_on)

            file_output.close()

        csv_f.close()

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
    with open(file_input, encoding=ENCODE_READ, errors="ignore") as f:
        mail = ""

        lines = f.readlines()
        mail_cnt = 0

        for line in lines:
            if re.search(r'de\s*:', line.strip(), re.IGNORECASE):
                if mail_cnt > 0:
                    # on traite le mail précédent
                    file_output = open(
                        os.path.join(output, "mail_" + str(file_cnt) + "_" + str(mail_cnt)), mode='w',
                        encoding=ENCODE_WRITE, errors="ignore")
                    file_output.write(file_input + "\r\n")
                    hash_dict = process_mail(
                        mail, file_output, hash_dict, verbose_on)
                    mail = ""
                    file_output.close()
                mail_cnt += 1

            mail = mail + line

        # On traite le dernier mail
        file_output = open(
            os.path.join(output, "mail_" + str(file_cnt) + "_" + str(mail_cnt)), mode='w', encoding=ENCODE_WRITE,
            errors="ignore")
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
    if my_args.debug:
        verbose = 2
    elif my_args.verbose:
        verbose = 1
    else:
        verbose = 0

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
            my_args.file, output, hash_dict, file_cnt, my_args.csv, verbose)

    elif my_args.dir and my_args.rec:
        result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(
            my_args.dir) for f in filenames]
        for file in result:
            hash_dict, file_cnt = process_file(
                file, output, hash_dict, file_cnt, my_args.csv, verbose)

    elif my_args.dir:
        with os.scandir(my_args.dir) as files:
            for file in files:
                hash_dict, file_cnt = process_file(
                    os.path.join(file), output, hash_dict, file_cnt, my_args.csv, verbose)

    for key, value in hash_dict.items():
        fd_secret.write('{}:{}\n'.format(key, value))

    print("done.")


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
    fid_secret = open("secret", mode='w', encoding=ENCODE_WRITE, errors="ignore")

    main(fid_secret)
    fid_secret.close()
