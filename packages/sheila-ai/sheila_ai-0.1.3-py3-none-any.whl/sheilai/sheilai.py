#import libs

import json
import random

import torch
import torch.nn as nn

import numpy as np
import nltk
from nltk.stem.porter import PorterStemmer

# make instances

stemmer = PorterStemmer()

#model

class eureka_intent_model(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(eureka_intent_model, self).__init__()
        self.l1 = nn.Linear(input_size, hidden_size)
        self.l2 = nn.Linear(hidden_size, hidden_size)
        self.l3 = nn.Linear(hidden_size, num_classes)
        self.relu = nn.ReLU()
    
    def forward(self, x):
        out = self.l1(x)
        out = self.relu(out)
        out = self.l2(out)
        out = self.relu(out)
        out = self.l3(out)
        return out

# get tokenizers, stems, etc

def word_stem(word):
    return stemmer.stem(word.lower())

def tokenize(sentence):
    return nltk.word_tokenize(sentence)

def bag_of_words(tokenized_sentence, words):
    sentence_words = []
    for word in tokenized_sentence:
        stemmed_word = word_stem(word)
        sentence_words.append(stemmed_word)
    
    bag = np.zeros(len(words), dtype=np.float32)
    for idx, w in enumerate(words):
        if w in sentence_words:
            bag[idx] = 1
    return bag

def load_data(datafile):
    data = torch.load(datafile)

    return data["input_size"], data["hidden_size"], data["output_size"], data['all_words'], data['tags'], data['model_state']

def get_device():
    if torch.cuda.is_available():
        device = torch.device('cuda')
        print("Cuda.")
    else:
        print("CPU.")
        device = torch.device('cpu')
    
    return device

def get_intents(path):
    with open(path, "r") as file:
        return json.load(file)

class sheil_ai:
    def __init__(self, datapath):
        self.input_size, self.hidden_size, self.output_size, self.all_words, self.tags, self.model_state = load_data(datapath)
        self.device = get_device()
        self.intents, self.threshold = None, None
        self.model = eureka_intent_model(self.input_size, self.hidden_size, self.output_size).to(self.device)
        self.model.load_state_dict(self.model_state)
        self.model.eval()

    def set_intents(self, path):
        self.intents = get_intents(path)
    
    def set_data(self, path):
        self.datafile = load_data(path)
    
    def set_threshold(self, value):
        self.threshold = value
    
    def word_stem(self, word):
        return stemmer.stem(word.lower())

    def tokenize(self, sentence):
        return nltk.word_tokenize(sentence)
    
    def bag_of_words(self, tokenized_sentence, words):
        sentence_words = []
        for word in tokenized_sentence:
            stemmed_word = self.word_stem(word)
            sentence_words.append(stemmed_word)
        
        bag = np.zeros(len(words), dtype=np.float32)
        for idx, w in enumerate(words):
            if w in sentence_words:
                bag[idx] = 1
        return bag
    
    def classify(self, sentence):
        # check if self.data and self.intents exist. raise error if not.
        InputTokens = self.tokenize(sentence)
        X = self.bag_of_words(sentence, self.all_words)
        X = X.reshape(1, X.shape[0])
        X = torch.from_numpy(X).to(self.device)

        output = self.model(X)

        ph, predicted = torch.max(output, dim=1)

        tag = self.tags[predicted.item()]

        probabilities = torch.softmax(output, dim=1)
        probability = probabilities[0][predicted.item()]

        for intent in self.intents['intents']:
            if tag == intent["tag"]:
                return intent

if __name__ == "__main__":
    Sheila = sheil_ai("./data.pth")
    Sheila.set_intents("./intents.json")
    Sheila.set_threshold(0.75)

    UserInput = input("You: ")
    intent_class = Sheila.classify(UserInput)
    print(intent_class)