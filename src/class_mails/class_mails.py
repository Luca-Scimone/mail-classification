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
        """
        An abstract method for the getter of the class Data
        """
        pass

    @abstractmethod
    def set(self, stream, encoding, header):
        """
        An abstract method for the setter of the class Data
        """
        pass


class Mails(Data):
    """
    A class Mails containing all methods to extract information from a csv file
    where mails are stored.
    """

    def __init__(self):
        # list of Mails
        self._mails = []
        # Names of the rows in the CSV format
        self._row_names = [
                "objet",
                "corps",
                "de_nom",
                "de_adr",
                "de_type",
                "A_nom",
                "A_adr",
                "A_type",
                "CC_nom",
                "CC_adr",
                "CC_type",
                "CCi_nom",
                "CCi_adr",
                "CCi_type",
                "label",
                "diffusion",
                "importance",
                "info_fact",
                "kilometrage"
            ]

    def __str__(self):
        """
        Overload of str in order to print mails more clearly
        """

        res = ""
        for mail in self.mails:
            res += "\n\n" + mail.__str__()
        return res

    def get(self):
        return self._mails

    def set(self, stream, encoding, header):
        """
        Reads a csv file of path 'stream'. Each column should represent the
        types defined in self._row_names.
        """

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
                        print("""[W] Ignored column %d in mail %d of %s
                              (extra column)""" % (col_idx, mail_cnt, stream))
                    col_idx += 1

                if col_idx < len(self._row_names):
                    raise Exception("Missing data in mail %d (bad CSV format?)"
                                    % (mail_cnt))

                self._mails.append(Mail(temp_dict))
                row_cnt += 1

    @property
    def mails(self) -> list:
        return self._mails

    @mails.setter
    def mails(self, path: str):
        """
        Read mails from path and put them in a dict (self.mails).
        """
        read_mails = []
        self._mails = read_mails


class Mail:
    """
    A class Mail representing a dictionary where each section of the mail is
    given (CC, CCi ect..)
    """

    def __init__(self, fields_mail: dict):
        self.fields_mail = fields_mail

    def __str__(self):
        return self.fields_mail.__str__()

    def set_label(self, label: list):
        """
        Set a label to a particular mail. This function should never been used.
        It is only needed when we want to write mails with label on disk. The
        PipelinesManager should never called set_label.
        """
        self.fields_mail["label"] = label

    def label(self) -> list:
        """
        Return an iterator over labels of a mail. For example [0,1,0...]
        """
        return self.fields_mail["label"]

    def labels(self) -> list:
        """
        Split labels in multiple lists. For example [1,0,1,0] become
        ([1,0,0,0], [0,0,1,0]).
        """
        pass

    def get_first_label(self) -> int:
        """
        Return the position of the first label. [0,0,0,1,1] gives 3.
        """
        pass

    def message(self) -> str:
        """
        Return the message of the mail as a string.
        """
        return self.fields_mail["message"]

    def object(self) -> str:
        """
        Return the object of the mail as a string.
        """
        return self.fields_mail["object"]

    def _to_dict_array(self):
        """
        Transform a mail to a dict where value are array. It's only useful for
        the to_dataframe method.
        """
        for key, value in self.fields_mail.items():
            self.fields_mail[key] = [value]
        return self.fields_mail

    def to_dataframe(self) -> DataFrame:
        """
        Return a mail as a pandas dataframe. For example :
        de   cc   cci   A   objet                  corps
        0  Na   Na   Naa   N   Na            un mail random
        1  Na   Na   Naa   N   Na      Un autre mail random
        """
        return pd.DataFrame.from_dict(self._to_dict_array())
