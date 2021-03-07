"""
Ce script permet d'anonymiser les mails pour le projet ingénieur.
Il s'appelle comme suit : python3 mail_anonyme.py --file f
Il lit alors le fichier f, extrait les mails et les anonymise (remplace par exemple les prénoms,
numéro de téléphone...). Il écrit les mails anonymisés dans un fichier output. Le destinataire et l'émetteur du mail
sont hashés. La correspondance strinh/hash_string est écrite dans un fichier 'secret'.

Pour un directory : python3 mail_anonyme.py --dir d --rec
"""

import hashlib
import os
import re
from typing import TextIO
import argparse

# ajouter un mot de civilité si non pris en compte. Attention Madame et madame ne sont pas équivalents.
CIVILITE = r"(?:madame|Madame|monsieur|Monsieur|mr|Mr|mme|Mme|melle|Mlle|M|m)\s*.\s*"

# ajouter une formule si manquante. Insensible à la casse (Cordialement et cordialement sont équivalents)
END_OF_MAIL = r"(cordialement|cdt|amicalement|sincèrement|sincère salutation|bien cordialement|bien " \
              r"sincèrement|cordialement " \
              r"vôtre|bien à vous|avec mes salutations)[,.;]?\s*[,.;]?\s*"
# Cette chaine définit par quoi sera remplacé les prénoms-noms. Attentions, les nombres et l'expéditeur ne sont
# pas concernés.
ANONYME = ' anonyme-anonyme '
ANONYME_NUMBER = "anonyme_number"
ENCODE_READ = 'cp1252'
ENCODE_WRITE = 'utf8'

# Don't edit bellow
# ---------------------------------------------------------------------------------- #
REGEX_MAIL = r'[^\s]*@[^\s]*'
NAME_RE = r"[A-Z][A-Za-zéàè]+"
NAMES_RE = r"(?:" + NAME_RE + r"[ ]+){1,3}(?:" + NAME_RE + r")"
FROM_RE = r"(de\s*:\s*)([^\n]*)"
PHONE_NUMBER_RE = r"[+]?[(]?[0-9]{2}[)]?[-\s.]?[0-9]?[-\s.]?(?:[0-9][-\s.]?){6,10}[0-9]"
TO_RE = r"(à\s*:)([^\n]*)"
CC_RE = r"(cc\s*:)([^\n]*)"


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

    hel: str = """Sélectionner ce mode pour avoir des informations supplémentaires.NON IMPLEMENTER"""
    all_args.add_argument("--verbose", help=hel, action="store_true")

    args = all_args.parse_args()
    return args


def check_dependency(my_args):
    if not my_args.file and not my_args.dir:
        print("L'option --dir ou --file doit etre précisé")
        exit(0)

    if my_args.file and my_args.dir:
        print("L'option --dir et --file ne peuvent pas etre utilisé en meme temps")
        exit(0)


def hash_user(user: str):
    """
    :param user: It is a string to hash.
    :return: The hash of user in hexadecimal. The algorithm chosen is blake2
    """
    user_h = hashlib.blake2b(digest_size=32)
    user_utf8 = user.encode(encoding=ENCODE_WRITE)
    user_h.update(user_utf8)
    return user_h.hexdigest()


def process_mail(mail: str, fd: TextIO, hash_link: dict):
    """

    This function take a string, split it in sentences and remove from each sentences all confidential data. Finally,
    sentences are written in fd file after removing sensible information.

    Parameters
    ----------
    mail : An entire string mail to process. A mail start with "de:Machin" and end with EOF or with another
    "de:autre_Machin".
    fd :It is the file where mails without confidential data are written.
    hash_link : A dictionary that makes correspondences between hash_string and string.

    Returns A dictionary that makes correspondences between hash_string and string.
    -------

    """
    # catch phone number
    # Since hash can contain a suite of characteres very similar to phone number, it's better to start with phone_number
    results = re.findall(PHONE_NUMBER_RE, mail, re.IGNORECASE)
    for result in results:
        mail = re.sub("{}".format(result), ANONYME_NUMBER, mail)

    # Catch special cases (lines that starts with 'de:','à:'...)
    result = re.search(FROM_RE, mail, re.IGNORECASE)
    if result:
        # on récupère le deuxième groupe
        # on strip pour ne pas hasher les espaces !
        user_from: str = result.group(2).strip()
        hash_link[user_from] = hash_user(user_from)
        mail = re.sub("{}".format(user_from), hash_link[user_from], mail)

    # The receiver have to be hide too. Since  there can be several receivers, we should use findall.
    results = re.findall(TO_RE, mail, re.IGNORECASE)
    for result in results:
        user_to = result[1].strip()
        hash_link[user_to] = hash_user(user_to)
        mail = re.sub("{}".format(user_to), hash_link[user_to], mail)

    # all people in CC are replaced with ANONYME string
    result = re.search(CC_RE, mail, re.IGNORECASE)
    if result:
        cc = result.group(2).strip()
        mail = re.sub("{}".format(cc), ANONYME, mail)

    # replace all mail by anonymous string. Mail in metadata have already been processed.
    mail = re.sub(REGEX_MAIL, ANONYME, mail)

    # Match sensible data in corpus mail
    # match data as monsieur Machin Bidule or Mme. Machine or...
    mail = re.sub(r'\s+{}{}'.format(CIVILITE, NAMES_RE), ANONYME, mail)

    # an email often finishes with "cordialement, best regards..." and then the name of the sender.
    result = re.search(END_OF_MAIL, mail, re.IGNORECASE)
    if result:
        mail = re.sub(r"{}{}".format(result.group(), NAMES_RE),
                      result.group() + ANONYME + "\n", mail)

    # Enfin, on affiche les derniers dont on n'est pas sûr
    result = re.findall(NAMES_RE, mail)
    if result:
        print("Les mots suivants n'ont pas été anonymisés et pourtant ce sont peut-être des prénoms :")
        for maybe_is_name in result:
            print(re.sub(r'\s', " ", maybe_is_name))
    print("\n")
    fd.write(mail)
    return hash_link


def process_file(file_input: str, file_output: TextIO, hash_dict: dict):
    """
    This function take a file_input fd descriptor, open it, parse mails in, and process each mail by calling
    process_mail. A mail is a text starting by FROM where FROM is a global variable defined at start at this code.
    Parameters
    ----------
    file_input The file that contains mail.
    file_output File to write mail without sensible data.
    file_secret A file that links hashed sensible data and the non hashed one.
    hash_dict A structure that contains links betweeen hashed sensible data and the non hashed one.

    Returns A dict that contains links betweeen hashed sensible data and the non hashed one.
    The data returned contains the new links and old links !
    -------

    """
    with open(file_input, encoding=ENCODE_READ) as f:
        mail = ""
        lines = f.readlines()
        for line in lines:
            if re.search(r'de\s*:', line.strip(), re.IGNORECASE):
                # on traite le mail précédent
                hash_dict = process_mail(mail, file_output, hash_dict)
                mail = ""
            mail = mail + line

        # On traite le dernier mail
        hash_dict = process_mail(mail, file_output, hash_dict)

        return hash_dict


def main(fd_output: TextIO, fd_secret: TextIO):
    """
    This is the main function. It calls parse function that parses user arguments, check the legality of them and
    anonymize mails contained in file or directory given by user.
    Parameters
    ----------
    fd_output : File where all mails without sensible data will be written.
    fd_secret : File where correspondences between string/hash_string will be written

    Returns
    -------

    """
    # print(locale.getpreferredencoding(do_setlocale=True))

    my_args = parse()
    check_dependency(my_args)

    hash_dict = dict()

    if my_args.file:
        hash_dict = process_file(my_args.file, fd_output, hash_dict)

    elif my_args.dir and my_args.rec:
        result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(my_args.dir) for f in filenames]
        for file in result:
            hash_dict = process_file(file, fd_output, hash_dict)

    elif my_args.dir:
        files = os.listdir(my_args.dir)
        for file in files:
            hash_dict = process_file(file, fd_output, hash_dict)

    for key, value in hash_dict.items():
        fd_secret.write('{}:{}\n'.format(key, value))


if __name__ == "__main__":
    fid_output = open("output", mode='w', encoding=ENCODE_WRITE)
    fid_secret = open("secret", mode='w', encoding=ENCODE_WRITE)
    # execute only if run as a script
    main(fid_output, fid_secret)
    fid_secret.close()
    fid_output.close()
