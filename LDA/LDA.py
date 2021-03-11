import os
import json
import gensim
from gensim import corpora
from gensim.models import LsiModel

import numpy as np
import matplotlib.pyplot as plt

from pprint import pprint
from collections import defaultdict

from matplotlib import pyplot as plt
from wordcloud import WordCloud
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle

import sys
sys.path.append('/home/goncalo/TPS_2A/pi/pretreatment/')
from treatment import pretreatement


directory = "./data/mails/"

def word_cloud (lda_model):
    cols = [color for name, color in mcolors.TABLEAU_COLORS.items()]  # more colors: 'mcolors.XKCD_COLORS'

    cloud = WordCloud( background_color='white',
                    width=2500,
                    height=1800,
                    max_words=10,
                    colormap='tab10',
                    color_func=lambda *args, **kwargs: cols[i],
                    prefer_horizontal=1.0)

    topics = lda_model.show_topics(formatted=False)

    fig, axes = plt.subplots(2, 2, figsize=(10,10), sharex=True, sharey=True)

    for i, ax in enumerate(axes.flatten()):
        fig.add_subplot(ax)
        topic_words = dict(topics[i][1])
        cloud.generate_from_frequencies(topic_words, max_font_size=300)
        plt.gca().imshow(cloud)
        plt.gca().set_title('Topic ' + str(i), fontdict=dict(size=16))
        plt.gca().axis('off')


    plt.subplots_adjust(wspace=0, hspace=0)
    plt.axis('off')
    plt.margins(x=0, y=0)
    plt.tight_layout()
    plt.show()

    def sentences_chart(lda_model=lda_model, corpus=vectorized_corpus, start = 0, end = 4):
        corp = corpus[start:end]
        mycolors = [color for name, color in mcolors.TABLEAU_COLORS.items()]

        fig, axes = plt.subplots(end-start, 1, figsize=(20, (end-start)*0.95), dpi=160)       
        axes[0].axis('off')
        for i, ax in enumerate(axes):
            if i > 0:
                corp_cur = corp[i-1] 
                topic_percs, wordid_topics, wordid_phivalues = lda_model[corp_cur]
                word_dominanttopic = [(lda_model.id2word[wd], topic[0]) for wd, topic in wordid_topics]    
                ax.text(0.01, 0.5, "Doc " + str(i-1) + ": ", verticalalignment='center',
                        fontsize=16, color='black', transform=ax.transAxes, fontweight=700)

                # Draw Rectange
                topic_percs_sorted = sorted(topic_percs, key=lambda x: (x[1]), reverse=True)
                ax.add_patch(Rectangle((0.0, 0.05), 0.99, 0.90, fill=None, alpha=1, 
                                    color=mycolors[topic_percs_sorted[0][0]], linewidth=2))

                word_pos = 0.06
                for j, (word, topics) in enumerate(word_dominanttopic):
                    if j < 14:
                        ax.text(word_pos, 0.5, word,
                                horizontalalignment='left',
                                verticalalignment='center',
                                fontsize=16, color=mycolors[topics],
                                transform=ax.transAxes, fontweight=700)
                        word_pos += .009 * len(word)  # to move the word for the next iter
                        ax.axis('off')
                ax.text(word_pos, 0.5, '. . .',
                        horizontalalignment='left',
                        verticalalignment='center',
                        fontsize=16, color='black',
                        transform=ax.transAxes)       

        plt.subplots_adjust(wspace=0, hspace=0)
        plt.suptitle('Sentence Topic Coloring for Documents: ' + str(start) + ' to ' + str(end-2), fontsize=22, y=0.95, fontweight=700)
        plt.tight_layout()
        plt.show()




# The mails
mails = pretreatement()

#Bag of words
bow_per_mail_tmp = []
for mail in mails:
    bow = []
    for word in mail:
        bow.append(word)
    bow_per_mail_tmp.append(bow)

# Remove duplicates
bow_per_mail = []
for el in bow_per_mail_tmp:
    list(set(el))
    bow_per_mail.append(el)

# Printing one mail
print(mails[1])

# number of topics
num_topics = 4

# The dictionary
id2word = corpora.Dictionary(bow_per_mail)

print(mails[0])

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

word_cloud (lda_model)