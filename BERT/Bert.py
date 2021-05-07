import os
import json
import codecs
import numpy as np
import pandas as pd
import torch
import warnings
import seaborn as sns
from tqdm import tqdm
import transformers as ppb
from transformers import CamembertModel, CamembertTokenizer, CamembertConfig
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score

warnings.filterwarnings('ignore')


def load_data (data_path, encoding, quiet) :
    """
    Goes through the directory of path 'data_path' and reads each json file;
    extracting the mail as well as the label it has.

    Parameters:
    data_path: the path to the directory containing all the json files 

    encoding: the encoding that should be used to read each file

    quiet: boolean. If true, this function will print out a progress bar
    increasing every time a file is read.
    """
    def parse_file (f, mails) :
        file_path = os.path.join(data_path, f)
            
        with codecs.open(file_path, 'r', encoding=encoding) as json_f:
            data_json = json.load(json_f)

        for msg in data_json['Mail']:
            corps = msg['Corps']
            obj   = msg['Objet']
            cat   = msg['Catégorie']

        label = [i for i, label in enumerate(list(cat[0].values())) if label == 1][0]
        mails.append([obj + corps, label])

        return mails

    mails = []

    if not os.path.exists(data_path):
        raise ValueError("path to the directory containing the emails not found.")

    if quiet:
        for _, _, files in os.walk(data_path):
            for f in files[:]:
                mails = parse_file (f, mails)
    else:
        print ("Loading the emails dataset...")
        for _, _, files in os.walk(data_path):
            for f in tqdm(files[:]):
                mails = parse_file (f, mails)
        print ("done.")

    return pd.DataFrame(mails,columns=['mail','label']).transpose()


class Bert(object):
    def __init__ (self, data=None, data_path=None, batch_size=0, encoding="utf8", 
        max_length=25, quiet=False):
        """
        Initiates the class Bert which can be used to interact with the Transformer encoder 
        architecture of camemBert.

        Parameters:
        data: if the data containing the mails and their respective labels are already
        in a panda dataframe, they can directly be used instead of recreating them. 

        data_path: if the raw data (ie. json of mails) is a different path then the usual
        /data/mails, filling this argument will make so the given path is the one used to
        generate the model

        batch_size: if the amount of mails are too large, batch_size can be used to work with
        a smaller amount of data.

        encoding: the encoding format used to open the mails. Default is utf-8.

        max_length: the maximum length tokens can have. Default is 25.

        quiet: a boolean that can be set to True if the user does not want this class to output
        informative messages about the model
        """
        if data == None:
            if data_path != None:
                df = load_data (data_path, encoding, quiet)
            else:
                df = load_data (os.path.join(os.path.join(os.getcwd(), "data"), "mails"), encoding, quiet)
        elif isinstance(data, pd.DataFrame) == True:
            df = data
        else:
            raise ValueError("data must be a dataframe yet it's type is " + type(data))

        if batch_size < 0:
            raise ValueError('Batch size cannot be negative yet batch_size=' + str(batch_size))
        elif len(df.axes[1]) < batch_size:
            raise ValueError('Batch size is larger than the dataframe size; dataframe size=' + str(len(df.axes[1])))
        elif batch_size == 0:
            self.df = df
        else:
            if not quiet:
                print("Using a custom batch size of " + str(batch_size) + " emails.")
            self.df = df.iloc[: , :batch_size]

        self.quiet = quiet

        if max_length <= 0 or max_length >= 512:
            raise ValueError ("max_length must be inside the following range: ]0,512[.")
        self.max_length = max_length

        # Loading the necessary tools (tokenier & model)
        if not quiet:
            print ("Loading the tokenizer, configuration and model...")
        self.tokenizer = CamembertTokenizer.from_pretrained("camembert-base")
        self.config = CamembertConfig.from_pretrained("camembert-base", output_hidden_states=True)
        self.model = CamembertModel.from_pretrained("camembert-base", config=self.config)
        self.model.eval()
        if not quiet:
            print ("done.")

        self.tokenized = None
        self.padded = None
        self.attention_mask = None


    def __init_tokenizer__ (self) :
        """
        Initiates the tokenization of the data.
        """
        self.tokenized = self.df.iloc[0].apply((lambda x: 
            self.tokenizer.encode(x, truncation = True, max_length = self.max_length, 
                add_special_tokens=True)))


    def __init_padding__ (self) :
        """
        Initiates the padding of the data. Padding adds some tokens of id zero to each
        sentence that does not have the same length as the longest sentence in the
        dataset.

        This is necessary in order for the tokenized representation of our data to be
        given as input to the neural network.
        """
        if self.tokenized == None:
            self.__init_tokenizer__ ()

        max_len = 0
        for i in self.tokenized.values:
            if len(i) > max_len:
                max_len = len(i)

        self.padded = np.array([i + [0]*(max_len-len(i)) for i in self.tokenized.values])


    def __init_attention_mask__ (self) :
        """
        Initiates the attention mask after the tokenization and padding. 
        This mask marks the usefull information in the generated matrix of
        our data (ie. makes so the padding is not taken into consideration
        by the neural network when the tokenized representation will be fed to it)

        Check the function test_sentence_treatement for a visual example of
        how this function works.
        """
        self.attention_mask = np.where(self.padded != 0, 1, 0)


    def test_tokenizer_on_sentences (self, *test_texts) :
        """
        Applies the loaded BERT tokenier on a set of sentences the user can give
        to this function then prints the result.

        Usage: test_tokenizer_on_sentences ("Bonsoir", "Ceci est une phrase", "Aurevoir")

        NB: this function is solely for a visualization of how BERT works.
        """

        if self.tokenizer == None:
            __init_tokenizer__ ()

        tokenized = []

        for text in test_texts:
            print ('Encoding of sentence: "' + text + "'")
            tmp = self.tokenizer.encode(text, truncation = True, 
                max_length = self.max_length, add_special_tokens=True)
            print (tmp)
            tokenized.append (tmp)
        
        return tokenized
            

    def test_sentence_treatement (self, *test_texts) :
        """
        Applies the loaded BERT tokenier after padding and attention mask creation.
        This function should be used on a set of sentences the user can give
        to this function.

        Usage: test_sentence_treatement ("Bonsoir", "Ceci est une phrase", "Aurevoir")

        NB: this function is solely for a visualization of how BERT works.
        """
        tokenized = self.test_tokenizer_on_sentences (*test_texts)

        max_len = 0
        for i in tokenized:
            if len(i) > max_len:
                max_len = len(i)

        padded = np.array([i + [0]*(max_len-len(i)) for i in tokenized])
        print ("Result after padding :")
        print (padded)

        attention_mask = np.where(padded != 0, 1, 0)
        print ("Attention Mask :")
        print (attention_mask)


    def embedding (self, test_size=None, random_state=None) :
        """
        Creates a word embedding of the dataset.

        Paramters:
        test_size: If float, should be between 0.0 and 1.0 and represent the proportion 
        of the dataset to include in the test split. If int, represents the absolute number
        of test samples. If None, the value will be set to 0.25.

        random_state: Controls the shuffling applied to the data before applying the split.
        Pass an int for reproducible output across multiple function calls.


        This function outputs a ready to use word embedding of the dataset in
        the form of 4 elements that this function returns:
        - X_train: The embedded representation of the part of the dataset that should
            be used for training.
        - X_test: The embedded representation of the part of the dataset that should
            be used for testing.
        - y_train: The ground truth labels associated with X_train
        - y_test: The ground truth labels associated with X_test
        """
        if self.tokenizer == None:
            self.__init_tokenizer__ ()
        if self.padded == None:
            self.__init_padding__ ()
        if self.attention_mask == None:
            self.__init_attention_mask__ ()
            
        # Creating tensors from the padded matrix and the mask
        input_ids = torch.tensor(self.padded)  
        attention_mask = torch.tensor(self.attention_mask)

        if not self.quiet:
            print ("Embedding the dataset... (this might take a while)")

        # Fetching the features
        with torch.no_grad():
            last_hidden_states = self.model(input_ids, attention_mask=attention_mask)
        features = last_hidden_states[0][:,0,:].numpy()

        if not self.quiet:
            print ("done.")

        # The labels
        labels = self.df.iloc[1]

        X_train, X_test, y_train, y_test = train_test_split(features, labels, 
            test_size=test_size, random_state=random_state)

        if not self.quiet:
            print("Size of the 'train' dataset: " + str(len(X_train)))
            print("Size of the 'test' dataset: " + str(len(X_test)))

        # Ensuring the labels are integers
        y_train = y_train.astype('int')
        y_test  = y_test.astype('int')

        return X_train, X_test, y_train, y_test