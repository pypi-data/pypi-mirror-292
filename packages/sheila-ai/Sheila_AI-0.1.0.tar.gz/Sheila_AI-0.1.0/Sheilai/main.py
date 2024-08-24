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

def load_data():
    datafile = "data.pth"
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

if __name__ == "__main__":
    device = get_device()

    intents = get_intents("intents.json")
    
    input_size, hidden_size, output_size, all_words, tags, model_state = load_data()

    model = eureka_intent_model(input_size, hidden_size, output_size).to(device)
    model.load_state_dict(model_state)
    model.eval()

    sentence = input("You: ")

    InputTokens = tokenize(sentence)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)

    ph, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probabilities = torch.softmax(output, dim=1)
    probability = probabilities[0][predicted.item()]
    if probability.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                print(random.choice(intent['responses']))
    else:
        print("No probability above threshold for input.")
