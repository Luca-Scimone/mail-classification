import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from tensorflow.python.keras import Sequential, Input
from tensorflow.python.keras.layers import Dense, Dropout
from tensorflow.python.keras.optimizer_v1 import SGD
from tensorflow.python.keras.utils.np_utils import to_categorical

from src.pipelines import PipelinesManager

if __name__ == "__main__":
    manager = PipelinesManager(path="../mails.csv")

    x = manager.data.mails_df()['corps']
    y = manager.data.labels_ls()

    tfidf = TfidfVectorizer()  # Give your pipeline
    out = tfidf.fit_transform(x)
    #x = my_pipeline.transform(x)
    tfid_tokens = tfidf.get_feature_names()
    df_tfidf = pd.DataFrame(data=out.toarray(), columns=tfid_tokens)
    x = df_tfidf
    # x = list(x)
    y = to_categorical(y)
    print(x)

    model = Sequential()
    model.add(Input(shape=(548,)))
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(len(y[0]), activation='softmax'))

    sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(loss='categorical_crossentropy', metrics=['accuracy'])

    # fitting and saving the model
    hist = model.fit(x, y, epochs=20, batch_size=5, verbose=1)

    # my_pipeline = EmptyPipeline()
    # my_pipeline.pipeline = [Lemme(), TfidfVectorizer(), SVC()]  # Give your pipeline
    # x_train, x_test, y_train, y_test = train_test_split(manager.data.mails_df()['corps'], manager.data.labels_ls())
    # out = my_pipeline.fit(x_train, y_train)
    # my_pipeline.show_confusion_matrix(x_test, y_test)
