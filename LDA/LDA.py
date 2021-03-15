from LDA_word_cloud import word_cloud
import os
import gensim
from gensim import corpora
from pprint import pprint

import pyLDAvis.gensim

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

# The dictionary
dictionary = corpora.Dictionary(bow_per_mail)

# The corpus
corpus = [dictionary.doc2bow(text) for text in bow_per_mail]

print('Number of unique tokens: %d' % len(dictionary))
print('Number of documents: %d' % len(corpus))

# Build LDA model
# Set training parameters.
num_topics = 4
chunksize = 2000
passes = 20
iterations = 400
eval_every = None  # Don't evaluate model perplexity, takes too much time.

# Make a index to word dictionary.
temp = dictionary[0]  # This is only to "load" the dictionary.
id2word = dictionary.id2token

lda_model = gensim.models.ldamodel.LdaModel(
    corpus=corpus,
    id2word=id2word,
    chunksize=chunksize,
    alpha='auto',
    eta='auto',
    iterations=iterations,
    num_topics=num_topics,
    passes=passes,
    eval_every=eval_every
)

# Print the Keyword in the last topic
pprint(lda_model.print_topics())
doc_lda = lda_model[corpus]

# Compute Coherence Score
top_topics = lda_model.top_topics(corpus)  # , num_words=20)

# Average topic coherence is the sum of topic coherences of all topics, divided by the number of topics.
avg_topic_coherence = sum([t[1] for t in top_topics]) / num_topics
print('Average topic coherence: %.4f.' % avg_topic_coherence)

pprint(top_topics)

vis = pyLDAvis.gensim.prepare(lda_model, corpus, dictionary=dictionary)

print("Data can now be visualized under ./LDA/LDA_Visualization.html")
pyLDAvis.save_html(vis, './LDA/LDA_Visualization.html')

print()
print()
print("Document topis:")
print(100*'=')

for name, el in zip(data.get_mails_nom(), corpus):
    print("--> mail", name, "is inside cluster(s):", end=' ')
    for topic in lda_model.get_document_topics(el):
        print(topic[0], end=' ')
    print('\n', 100*'=')

word_cloud(lda_model)

# Topic 0:
# bonjour origine merci nom www envoye msg a email si
#
# Topic 1:
# cordialement demande envoye origine msg rue email a bonjour
#
# Topic 2:
# fwd www msg origine email sans destinataire a toute
#
# Topic 3:
# bien email re espass bonjour a origine msg conseiller cordialement
