import re
import pickle
import numpy as np
import pandas as pd
from datetime import date

import nltk
nltk.download('stopwords')
nltk.download('punkt')

from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

#stop downloading after this threshold
LOAD = 5

class Brain:
    def __init__(self):
        self.MODELPATH = "./resources/model/brain.pkl"
        self.VECTORIZERPATH = "./resources/model/vectorizer.pkl"
        self.DATAPATH = "./resources/data/dataset.csv"
        self.slovakSW_PATH = "./resources/data/slovakSW.txt"

        self.stemmerEng = SnowballStemmer('english')
        self.engWords = stopwords.words('english')
        self.svkWords = open(self.slovakSW_PATH, "r", encoding='ISO-8859-2')

        self.vectorizer = TfidfVectorizer()
        self.model = self.get_model()
        self.labels = None

    def get_dataset(self):
        return pd.read_csv(self.DATAPATH, index_col=[0])

    def set_labels(self, labels):
        self.labels = labels

    def get_wrong(self, emails):
        to_drop = []
        for idx, mail in enumerate(emails):
            if(type(mail) == float or mail == "no text version avail" or len(mail) == 0):
                to_drop.append(idx)
        return to_drop

    def get_model(self):
        return GaussianNB()

    def save_model(self, model):
        with open(self.MODELPATH, 'wb') as fid:
            pickle.dump(model, fid)

    def load_model(self):
        with open(self.MODELPATH, 'rb') as f:
            self.model = pickle.load(f)

        return self.model

    def label2categorical(self, y, labels):
        for i in range(len(labels)):
            for j in range(len(y)):
                if labels[i] == y[j]:
                    y[j] = i+1
        df = pd.DataFrame(data=y.flatten())
        return df

    def categorical2label(self, prediction):
        return self.labels[prediction[0]-1]

    def clean_dataset(self):
        data = self.get_dataset()
        drop_indexes = self.get_wrong(data["body"])

        for i, sample in enumerate(data["body"]):
            wrong = [True for idx in drop_indexes if i == idx]
            if wrong:
                continue

            sample = re.sub(r'http\S+', '', sample)
            sample = re.compile(r'<[^>]+>').sub("", sample)
            sample = re.sub('[!|()<>;?$=:+/*,-]|[0-9]|&nbsp', '', sample)
            sample = sample.replace(".", "")
            sample = " ".join(sample.split())

            tokens = word_tokenize(sample)
            tokenWords = [w for w in tokens if w.isalpha()]
            afterStopwords = [w for w in tokenWords if w not in self.engWords or w not in self.svkWords]
            stemmedWords = [self.stemmerEng.stem(w) for w in afterStopwords]
            output = " ".join(stemmedWords)
            data["body"][i] = output

        drop_indexes = self.get_wrong(data["body"])
        data = data.drop(data.index[drop_indexes])
        data = data.reset_index(drop=True)
        data.to_csv(self.DATAPATH);

    def preprocessing(self):
        data = self.get_dataset()

        X = data.iloc[:, 3].values
        X = self.vectorizer.fit_transform(X).toarray()
        y = self.label2categorical(np.array(data.iloc[:, 0]), self.labels).astype('int')
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
        return X_train, X_test, y_train, y_test

    def pred_preprocessing(self, mail):
        data = self.get_dataset()

        mail = re.sub(r'http\S+', '', mail)
        mail = re.compile(r'<[^>]+>').sub("", mail)
        mail = re.sub('[!|()<>;?$=:+/*,-]|[0-9]|&nbsp|r^\s*$', '', mail)
        mail = filter(lambda x: not re.match(r'^\s*$', x), mail)
        mail = mail.replace(".", "")
        mail = " ".join(mail.split())

        tokens = word_tokenize(mail)
        tokenWords = [w for w in tokens if w.isalpha()]
        afterStopwords = [w for w in tokenWords if w not in self.engWords or w not in self.svkWords]
        stemmedWords = [self.stemmerEng.stem(w) for w in afterStopwords]
        mail = " ".join(stemmedWords)

        X = data.iloc[:, 3].values
        X = self.vectorizer.fit_transform(X).toarray()

        return self.vectorizer.transform([mail]).toarray()

    def train(self):
        X_train, X_test, y_train, y_test = self.preprocessing()
        y_pred = self.model.fit(X_train, y_train).predict(X_test)
        self.save_model(self.model)

    def predict(self, mail):
        if(type(mail) == float or mail == "no text version avail" or len(mail) == 0):
            return -1

        try:
            prediction = self.model.predict(self.pred_preprocessing(mail))
            return self.categorical2label(prediction)
        except:
            return -1


