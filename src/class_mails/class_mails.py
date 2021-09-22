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

    @abstractmethod
    def set(self, stream, encoding, header):
        """
        An abstract method for the setter of the class Data
        """


class Mails(Data):
    """
    A class Mails containing all methods to extract information from a csv file
    where mails are stored.
    """

    def __init__(self):
        # list of Mails
        self._mails = []
        self._mails_df = None
        # List of label names
        self._labels = []
        self._label_names = []
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
                        if self._row_names[col_idx] == "label":
                            if col in self._label_names:
                                label = self._label_names.index(col)
                            else:
                                label = len(self._label_names)
                                self._label_names.append(col)
                        else:
                            temp_dict[self._row_names[col_idx]] = col
                    else:
                        print("""[W] Ignored column %d in mail %d of %s
                              (extra column)""" % (col_idx, mail_cnt, stream))
                    col_idx += 1

                if col_idx < len(self._row_names):
                    raise Exception("Missing data in mail %d (bad CSV format?)"
                                    % (mail_cnt))

                self._mails.append(Mail(temp_dict, label))
                self._labels.append(label)
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

    def mails_df(self):
        """
        Read mails from path and put them in a dict (self.mails).
        """
        if self._mails_df is None:
            df = pd.DataFrame()
            for mail in self._mails:
                df = df.append(mail.to_dataframe(), ignore_index=True)
            self._mails_df
        else:
            return self._mails_df

    def labels_ls(self) -> list:
        """
        Return the label as a list
        """
        return self._labels


class Mail:
    """
    A class Mail representing a dictionary where each section of the mail is
    given (CC, CCi ect..)
    """

    def __init__(self, mail_components: dict, label):
        self.mail_components = mail_components
        self._label = label
        self._mail = None

    def __str__(self):
        return self.mail_components.__str__()

    def set_label(self, label: list):
        pass

    def label(self) -> int:
        """
        Return an iterator over labels of a mail. For example [0,1,0...]
        """
        return self._label

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
        return self.mail_components["message"]

    def object(self) -> str:
        """
        Return the object of the mail as a string.
        """
        return self.mail_components["object"]

    def _to_dict_array(self):
        """
        Transform a mail to a dict where value are array. It's only useful for
        the to_dataframe method.
        """
        for key, value in self.mail_components.items():
            self.mail_components[key] = [value]
        return self.mail_components

    def to_dataframe(self) -> DataFrame:
        """
        Return a mail as a pandas dataframe. For example :
        de   cc   cci   A   objet                  corps
        0  Na   Na   Naa   N   Na            un mail random
        1  Na   Na   Naa   N   Na      Un autre mail random
        """
        if self._mail is None:
            self._mail = pd.DataFrame.from_dict(self._to_dict_array())
            return self._mail
        return self._mail

