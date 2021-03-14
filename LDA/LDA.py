from LDA_word_cloud import word_cloud
import os
import gensim
from gensim import corpora

import importlib.util
spec = importlib.util.spec_from_file_location(
    "treatement", os.path.abspath(os.getcwd()) + "/pretreatment/treatment.py")
pretreatement = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pretreatement)
data = pretreatement.mails_data()


directory = "./data/mails/"

# The mails
mails = data.vector_of_mails()
bow_per_mail = data.bag_of_words_per_mail()

# number of topics
num_topics = 4

# The dictionary
id2word = corpora.Dictionary(bow_per_mail)

# Vectorized corpus
vectorized_corpus = id2word.doc2bow(mails)

# Build LDA model
lda_model = gensim.models.ldamodel.LdaModel(corpus=vectorized_corpus,
                                            id2word=id2word,
                                            num_topics=num_topics,
                                            random_state=100,
                                            update_every=1,
                                            chunksize=400,
                                            passes=10,
                                            alpha='auto',
                                            per_word_topics=True)

word_cloud(lda_model)
