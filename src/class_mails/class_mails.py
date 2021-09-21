from abc import ABC, abstractmethod
import os.path
import csv

import pandas as pd
from pandas import DataFrame


class Data(ABC):
    """
    Return a mails.
    """

    @abstractmethod
    def get(self):
        pass

    """
    Set your mails from a stream (file, tcp connexion, other object...)
    """

    @abstractmethod
    def set(self, encoding, header, stream=None):
        pass

class Mails(Data):
    def __init__(self):
        # list of Mails
        self._mails = []
        # Names of the rows in the CSV format
        self._row_names = [
                "de",
                "cc",
                "cci",
                "A",
                "objet",
                "corps"
            ]

    def __str__(self):
        r = ""
        for mail in self.mails:
            r += "\n\n" + mail.__str__()
        return r

    def get(self):
        return self._mails

    """
    Reads a csv file of path 'stream'. Each column should represent the types
    defined in self._row_names.
    """

    def set(self, stream, encoding, header):
        if not os.path.exists(stream):
            raise Exception("Missing or invalid path to data.")

        if not os.path.isfile(stream):
            raise Exception("Path to data is not a regular file.")

        with open(stream, encoding=encoding, newline='') as file:
            csv_reader = csv.reader(file)

            if header:
                next(csv_reader)

            row_cnt = 0
            for mail_cnt, row in enumerate(csv_reader):
                temp_dict = {}

                col_idx = 0
                for col in row:
                    if col_idx < len(self._row_names):
                        temp_dict[self._row_names[col_idx]] = col
                    else:
                        print("[W] Ignored column %d in mail %d of %s (extra column)"
                              % (col_idx, mail_cnt, stream))
                    col_idx += 1

                if col_idx < len(self._row_names):
                    raise Exception("Missing data in mail %d (bad CSV format?)"
                                    % (mail_cnt))

                self._mails.append(Mail(temp_dict))
                row_cnt += 1

    @property
    def mails(self) -> list:
        return self._mails

    """ 
    Read mails from path and put them in a dict (self.mails).
    """

    @mails.setter
    def mails(self, path: str):
        read_mails = []
        self._mails = read_mails


class Mail:

    # A Mail is internally a dictionary.

    def __init__(self, fields_mail: dict):
        self.fields_mail = fields_mail

    def __str__(self):
        return self.fields_mail.__str__()

    """ 
    Set a label to a particular mail. This function should never been used. It
    is only needed when we want to write mails with label on disk. The
    PipelinesManager should never called set_label. 
    """

    def set_label(self, label: list):
        self.fields_mail["label"] = label

    """
        Return an iterator over labels of a mail. For example [0,1,0...]  
    """

    def label(self) -> list:
        return self.fields_mail["label"]

    """
        Split labels in multiple lists. For example [1,0,1,0] become
        ([1,0,0,0], [0,0,1,0]). 
    """

    def labels(self) -> list:
        pass

    """
    Return the position of the first label. [0,0,0,1,1] gives 3. 
    """

    def get_first_label(self) -> int:
        pass

    """ 
    Return the message of the mail as a string.
    """

    def message(self) -> str:
        return self.fields_mail["message"]

    """ 
        Return the object of the mail as a string.
    """

    def object(self) -> str:
        return self.fields_mail["object"]

    """
    Transform a mail to a dict where value are array. It's only useful for the to_dataframe method. 
    """

    def _to_dict_array(self):
        for key, value in self.fields_mail.items():
            self.fields_mail[key] = [value]
        return self.fields_mail

    """
    Return a mail as a pandas dataframe. For example : 
       de   cc   cci   A   objet                  corps
    0  Na   Na   Naa   N   Na            un mail random
    1  Na   Na   Naa   N   Na      Un autre mail random
    """

    def to_dataframe(self) -> DataFrame:
        return pd.DataFrame.from_dict(self._to_dict_array())

