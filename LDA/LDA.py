from LDA_word_cloud import word_cloud
import os
import gensim
from gensim import corpora
from pprint import pprint

import pyLDAvis.gensim
from gensim.models import CoherenceModel

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

# Print the Keyword in the 10 topics
pprint(lda_model.print_topics())
doc_lda = lda_model[vectorized_corpus]


texts = getattr(data,'cleaned_mails')

# Compute Coherence Score
coherence_model_lda = CoherenceModel(model=lda_model, texts=texts, dictionary=id2word, coherence='c_v')
coherence_lda = coherence_model_lda.get_coherence()
print('\nCoherence Score: ', coherence_lda)

doc_complete = getattr(data,'mails')

doc_complete.append(lda_model.id2word[len(lda_model.id2word)-1]) #last corpus word is "jawbone"

doc_clean = [str(doc).split() for doc in doc_complete]
doc_term_matrix = [lda_model.id2word.doc2bow(doc) for doc in doc_clean]
vis_data = pyLDAvis.gensim.prepare(lda_model, doc_term_matrix, lda_model.id2word)

pyLDAvis.save_html(vis_data, './LDA/LDA_Visualization.html')