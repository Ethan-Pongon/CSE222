import nltk
from nltk.stem.lancaster import LancasterStemmer
import numpy as np
import tflearn
import tensorflow as tf
import random
import json
import string
import unicodedata
import sys


# a table structure that holds the different punctuations used
table = dict.fromkeys(i for i in range(sys.maxunicode) if unicodedata.category(chr(i)).startswith('P'))

# this method removes the punctuation from sentences
def remove_punctuation(text):
    return text.translate(table)

stemmer = LancasterStemmer()
# variable for holding json data
data = None

# read the json file and load the training data into 'data'
with open('TrainingData.json') as json_data:
    data = json.load(json_data)
    # print(data)

# create a list of the types of sentences TF is being trained on
category = list(data.keys())
words = []
# 'docs' is a list of tuples with words in a sentence and the sentence type
docs = []

for each_category in data.keys():
    for each_sentence in data[each_category]:
        # first remove the punctuation from the sentence
        each_sentence = remove_punctuation(each_sentence)
        # print(each_sentence)
        # take the words from each sentence and add them to the word list
        w = nltk.word_tokenize(each_sentence)
        # print("tokenized words: ", w)
        words.extend(w)
        docs.append((w, each_category))

# stem and lower each word and remove duplicate words
words = [stemmer.stem(w.lower()) for w in words]
words = sorted(list(set(words)))

#print(words)
#print(docs)

# training data
training = []
output = []
# make an empty array for output
output_empty = [0] * len(category)

for doc in docs:
    # initialize bag of words (bow) for each document in the list
    bow = []
    # list of tokenized words
    token_words = doc[0]
    # stem and lower the words
    token_words = [stemmer.stem(word.lower()) for word in token_words]
    # make a bag of words (bow) array
    for w in words:
        bow.append(1) if w in token_words else bow.append(0)
    output_row = list(output_empty)
    output_row[category.index(doc[1])] = 1

    # the training set contains a bag of words model and the output row that tells which category that bow belongs to
    training.append([bow, output_row])

random.shuffle(training)
training =  np.array(training)

# trainx contains the bow and trainy contains the category
train_x = list(training[:, 0])
train_y = list(training[:, 1])

tf.reset_default_graph()
# build the neral network
net = tflearn.input_data(shape=[None, len(train_x[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
net = tflearn.regression(net)

model = tflearn.DNN(net, tensorboard_dir='tflearn_logs')
# start training (apply gradient descent algorithm)
model.fit(train_x, train_y, n_epoch=710, batch_size=8, show_metric=True)
model.save('model.tflearn')

def evaluate_sentence(sentence):
    global words
    # tokenize the argument sentence
    sentence_words = nltk.word_tokenize(sentence)
    # stem the words
    sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
    # make a bag of words
    bow = [0]*len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bow[i] = 1
    return(np.array(bow))

sent_1 = "Very happy with my haircut today!"
sent_2 = "I'm happy today"
sent_3 = "You are stupid and don't know how"
sent_4 = "Your stupid 522 drivers don't know how to stop for their passengers."
print(category[np.argmax(model.predict([evaluate_sentence(sent_1)]))])
print(category[np.argmax(model.predict([evaluate_sentence(sent_2)]))])
print(category[np.argmax(model.predict([evaluate_sentence(sent_3)]))])
print(category[np.argmax(model.predict([evaluate_sentence(sent_4)]))])