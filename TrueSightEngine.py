from transformers import BertTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import nltk
import string
import numpy as np
import pandas as pd
import tensorflow as tf
from datetime import datetime
import pickle
import cloudstorage as gcs


nltk.download('stopwords')
stop_words = stopwords.words('indonesian')   # Get indonesian stopwords


class Logger:
    """Logs are error, info adn warning"""

    def __init__(self, displayOutput: bool = True, logFile=None, debugMode=True) -> None:
        self.displayOutput = displayOutput
        self.logFile = logFile
        self.debugMode = debugMode

    def logFileWrite(self, message):
        message = str(message)
        try:
            with open(self.logFile, 'a') as log:
                log.write(message)
        except:
            pass

    def error(self, source, message):
        message = str(message)
        source = str(source)
        if self.displayOutput:
            print('[ERROR] ' + message)
        if not self.logFile is None:
            date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            self.logFileWrite(f"[{date}] Error from {source}: {message}\n")

    def info(self, source, message):
        message = str(message)
        source = str(source)
        if self.displayOutput:
            print('[INFO] ' + message)
        if not self.logFile is None:
            date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            self.logFileWrite(f"[{date}] Info from {source}: {message}\n")

    def debug(self, message):
        message = str(message)
        source = str(source)
        if self.debugMode:
            print('[DEBUG] ' + message)

    def warn(self, source, message):
        message = str(message)
        source = str(source)
        if self.displayOutput:
            print('[WARN] ' + message)
        if not self.logFile is None:
            date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            self.logFileWrite(f"[{date}] Warning from {source}: {message}\n")


class TimeExecution:
    """Calculate time between init and end"""

    def init(self):
        """Set initial time"""
        # Get current timestamp
        self.timestamp = datetime.now().timestamp()

    def end(self):
        # Displays the time required for execution
        print(int((datetime.now().timestamp() - self.timestamp) * 1000), 'ms')


class SearchEngine:
    """Engine for search"""
    def addDataToDictionary(new_data: dict, dictionary: dict):
        """Build dict header with array from single dict, usage for data search"""
        # For all header in input dict
        for header in list(new_data.keys()):
            total_data = 0
            if header in dictionary:
                # Count all header in input dict
                total_data = len(dictionary[header])
            else:
                # If doesn't exists, create new one
                dictionary[header] = {}
            # Set value to last/current item
            dictionary[header][total_data] = new_data[header]
        return dictionary

    def RemoveStopWords(words: list, stop_words=stop_words) -> list:
        """Remove puchtuation and preposisi words"""
        return [s.strip(string.punctuation) for s in words if s.lower().strip(string.punctuation) not in stop_words]

    def search(keywords: str, data, search_accuracy: float = 0.5, use_stopwords=True) -> list:
        """
        Search keywords in data of string

        Returns:
        Returning array of tuple (float accuracy, str text)
        """
        data = list(data)
        # Remove stopwords
        search_words = SearchEngine.RemoveStopWords(
            keywords.split()) if use_stopwords else keywords.split()
        filtered_keywords = ' '.join(
            search_words) if use_stopwords else keywords

        # Vectorization
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(data)
        X = X.T.toarray()
        data_frame = pd.DataFrame(X, index=vectorizer.get_feature_names_out())

        # Transform
        word_vect = vectorizer.transform(
            [filtered_keywords]).toarray().reshape(data_frame.shape[0],)

        # Calculate rate for each data
        search_rate = {}
        for i in range(len(data)):
            search_rate[i] = np.dot(data_frame.loc[:, i].values, word_vect) / np.linalg.norm(
                data_frame.loc[:, i]) * np.linalg.norm(word_vect)

        # Sorted all data by rate from biggest
        rate_sorted = sorted(
            search_rate.items(), key=lambda x: x[1], reverse=True)
        result = []

        # Return all data with given percentage of total keywords found in data
        for k, v in rate_sorted:
            word_found = 0
            if v != 0.0:
                for word in search_words:
                    if word in data[k]:
                        word_found += 1

                if (word_found / len(search_words) > search_accuracy):
                    result.append((v, data[k]))

        return result

    def search_from_dict(keywords: str, data, lookupHeader, search_accuracy: float = 0.5, use_stopwords=True) -> list:
        """
        Search keywords in dict

        lookupHeader: Array of header name to lookup

        Returns:
        Returning array of tuple (float accuracy, dict item)
        """
        datalist = list()
        result = []

        # Combine all data to single string for given header
        for header in list(lookupHeader):
            for i, (_, item) in enumerate(data[header].items()):
                if len(datalist) <= i:
                    datalist.append(item)
                else:
                    datalist[i] += " " + item

        # Remove all stopwords
        search_words = SearchEngine.RemoveStopWords(
            keywords.split()) if use_stopwords else keywords.split()
        filtered_keywords = ' '.join(
            search_words) if use_stopwords else keywords

        # Vectorization
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(datalist)
        X = X.T.toarray()
        data_frame = pd.DataFrame(X, index=vectorizer.get_feature_names_out())

        # Transform
        word_vect = vectorizer.transform(
            [filtered_keywords]).toarray().reshape(data_frame.shape[0],)

        # Calculate rate for each data
        search_rate = {}
        norm_vector = np.linalg.norm(word_vect)
        for i in range(len(datalist)):
            search_rate[i] = np.dot(data_frame.loc[:, i].values, word_vect) / np.linalg.norm(
                data_frame.loc[:, i]) * norm_vector

        # Sorted all data by rate from biggest
        rate_sorted = sorted(
            search_rate.items(), key=lambda x: x[1], reverse=True)
        result = []

        # Return all data with given percentage of total keywords found in data
        for k, v in rate_sorted:
            word_found = 0
            if v != 0.0:
                for word in search_words:
                    if word in datalist[k]:
                        word_found += 1

                if (word_found / len(search_words) > search_accuracy):
                    data_row = {}
                    for header in list(data.keys()):
                        data_row[header] = data[header][k]
                    result.append({'rate': v, 'row': data_row})

        return result


class TensorHelper:
    """Helper for tensor"""

    def __init__(self, threshold, gpu=True) -> None:
        self.THRESHOLD = threshold

        # Configuration to use CPU or GPU
        if not gpu:
            configuration = tf.compat.v1.ConfigProto(device_count={"GPU": 0})
            session = tf.compat.v1.Session(config=configuration)

        # Load default tokenizer
        self.bert_tokenizer = BertTokenizer.from_pretrained(
            "indobenchmark/indobert-base-p1")

        self.is_model_loaded = False

    def loadTokenizer(self, filename: str):
        """Load bert tokenizer from file"""
        if filename.startswith('gc://'):
            # Load from Google Cloud Storage
            with gcs.open(filename, 'rb') as handle:
                self.bert_tokenizer = pickle.load(handle)
        else:
            # Load from local
            with open(filename, 'rb') as handle:
                self.bert_tokenizer = pickle.load(handle)

    def openModel(self, path):
        """Load model from trained model"""
        self.model = tf.keras.models.load_model(path)
        self.is_model_loaded = True

    def predict_claim(self, claimtext: str, predict_text_length):
        """Predict claim

        return dict of claim:str, val_prediction:float32, prediction: "FAKE" or "FACT
        """
        result = self.model.predict(
            self._bert_encode([claimtext], predict_text_length))
        return {
            'claim': claimtext,
            'val_prediction': result[0][0],
            'prediction': 'FAKE' if result[0] > self.THRESHOLD else 'FACT'
        }

    def saveModel(self, path):
        """Save model to path"""
        self.model.save(path)

    def _bert_encode(self, data, max_len):
        """Bert Encode"""
        input_ids = []
        attention_masks = []

        for i in range(len(data)):
            encoded = self.bert_tokenizer.encode_plus(data[i],
                                                      add_special_tokens=True,
                                                      max_length=max_len,
                                                      pad_to_max_length=True,
                                                      return_attention_mask=True)

            input_ids.append(encoded['input_ids'])
            attention_masks.append(encoded['attention_mask'])

        return np.array(input_ids), np.array(attention_masks)
