# number of topics
num_topics = 4

# The dictionary
id2word = corpora.Dictionary(bagOfWords_per_mail)

# Vectorized corpus
vectorized_corpus = id2word.doc2bow(cleared_mails )

#Build LDA model
lda_model = gensim.models.ldamodel.LdaModel(corpus=vectorized_corpus,
                                           id2word=id2word, 
                                           num_topics=num_topics,  
                                           random_state=100, 
                                           update_every=1, 
                                           chunksize=400,
                                           passes=10, 
                                           alpha='auto', 
                                           per_word_topics=True)