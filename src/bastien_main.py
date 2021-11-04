import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.model_selection import train_test_split
from tensorflow.python.keras import Sequential, Input
from tensorflow.python.keras.layers import Dense, Dropout, LSTM, Embedding
from tensorflow.python.keras.optimizer_v1 import SGD
from tensorflow.python.keras.utils.np_utils import to_categorical

from src.pipelines import PipelinesManager

if __name__ == "__main__":
    #manager = PipelinesManager(path="../all_mails.csv")
    mails = pd.read_csv("../all_mails.csv")

    x = mails['Corps']
    y = list(mails['Catégorie'])

    # Transformation en vecteur
    tfidf = TfidfVectorizer(lowercase=True)  # Give your pipeline
    # tfidf =  CountVectorizer(lowercase=True)
    out = tfidf.fit_transform(x)
    #x = my_pipeline.transform(x)
    tfid_tokens = tfidf.get_feature_names()
    df_tfidf = pd.DataFrame(data=out.toarray(), columns=tfid_tokens)

    X_train, X_test, y_train, y_test = train_test_split(df_tfidf, y, test_size=0.2)


    # x = list(x)
    y_train = to_categorical(y_train)
    y_test = to_categorical(y_test)
    #print(y)
    #print(x)

    model = Sequential()
    model.add(Embedding(input_dim=1000, output_dim=64))
    #model.add(Input(shape=(X_train.shape[1],)))
    model.add(LSTM(100))
    model.add(Dense(512, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(len(y_train[0]), activation='softmax'))

    sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(loss='categorical_crossentropy',  metrics=['accuracy'])

    # fitting and saving the model
    hist = model.fit(X_train, y_train, epochs=20, batch_size=5, verbose=1)

    # Print accuracy
    red_train = model.predict(X_train)
    scores = model.evaluate(X_train, y_train, verbose=0)
    print('Accuracy on training data: {}% \n Error on training data: {}'.format(scores[1], 1 - scores[1]))

    pred_test = model.predict(X_test)
    scores2 = model.evaluate(X_test, y_test, verbose=0)
    print('Accuracy on test data: {}% \n Error on test data: {}'.format(scores2[1], 1 - scores2[1]))

    # my_pipeline = EmptyPipeline()
    # my_pipeline.pipeline = [Lemme(), TfidfVectorizer(), SVC()]  # Give your pipeline
    # x_train, x_test, y_train, y_test = train_test_split(manager.data.mails_df()['corps'], manager.data.labels_ls())
    # out = my_pipeline.fit(x_train, y_train)
    # my_pipeline.show_confusion_matrix(x_test, y_test)
