from abc import ABC, abstractmethod


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
    def set(self, stream=None):
        pass


class Mails(Data):
    def __init__(self):
        # list of Mails
        self._mails = []

    def __str__(self):
        r = ""
        for mail in self.mails:
            r += "," + mail.__str__()
        return r

    def fake_mails(self):
        fake_mail1 = Mail({"message": "Bonjour Monsieur Dupond."})
        fake_mail2 = Mail({"message": "Bonjour."})
        self._mails.append(fake_mail1)
        self._mails.append(fake_mail2)

    def get(self):
        return self._mails

    def set(self, stream=None):
        print("Set data from your stream. ", stream)
        # TODO self_mails must contain all mails as list of Mail (see bellow)
        # self.mails = stream
        self.fake_mails()

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
    Set a label to a particular mail. This function should never been used. It is only needed when 
    we want to write mails with label on disk. The PipelinesManager should never called set_label. 
    """

    def set_label(self, label: list):
        self.fields_mail["label"] = label

    """
        Return an iterator over labels of a mail. For example [0,1,0...]  
    """

    def label(self) -> list:
        return self.fields_mail["label"]

    """
        Split labels in multiple lists. For example [1,0,1,0] become ([1,0,0,0], [0,0,1,0]). 
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
