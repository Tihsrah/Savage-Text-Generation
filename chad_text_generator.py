# -*- coding: utf-8 -*-
"""chad_text_generator.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1HGGTYOBBAH4fRIe7anqkmuh2mWzUjznX
"""

# import tensorflow as tf
# import pandas as pd
# import numpy as np

# df=pd.read_csv('/content/chad.csv')
# df.head()

# df.describe()

# df=df[df['comment']!='[deleted]']
# df.describe()

# df

# import re
# from bs4 import BeautifulSoup

# def clean_tweet(tweet):
#     # Remove @mentions
#     text = re.sub(r'@[A-Za-z0-9\']+', '', tweet)
#     # Remove HTML tags
#     text = BeautifulSoup(text, 'lxml').get_text()
#     # Remove URLs
#     text = re.sub(r'https?://[A-Za-z0-9. ]+(/[A-Za-z0-9]+)*', '', text)
#     # Remove non-alphabetic characters
#     text = re.sub("[^a-zA-Z]", " ", text)
#     # Remove 'RT' (retweet) tag
#     text = re.sub(r'\bRT\b', '', text)
#     # Replace 'nan' with a space
#     text = re.sub(r'\bnan\b', ' ', text)
#     # Replace newlines with spaces
#     text = text.replace('\n', ' ')
#     # Remove extra whitespace
#     text = re.sub(r'\s+', ' ', text).strip()
#     return text
# df['comment']=df['comment'].apply(clean_tweet)
# df['reply']=df['reply'].apply(clean_tweet)

# df

# clean_tweet(df.iloc[0,0])

# data=pd.DataFrame()
# data.head()

# data['data'] = df['comment'] + ' -> ' + df['reply']
# data.head()

# data.to_csv('data.csv',index=False)

# def clean_text(text):
#   text = re.sub(r',', '', text)
#   text = re.sub(r'\'', '',  text)
#   text = re.sub(r'\"', '', text)
#   text = re.sub(r'\(', '', text)
#   text = re.sub(r'\)', '', text)
#   text = re.sub(r'\n', '', text)
#   text = re.sub(r'“', '', text)
#   text = re.sub(r'”', '', text)
#   text = re.sub(r'’', '', text)
#   text = re.sub(r'\.', '', text)
#   text = re.sub(r';', '', text)
#   text = re.sub(r':', '', text)
#   text = re.sub(r'\-', '', text)

#   return text

import tensorflow as tf
import pandas as pd
import numpy as np

with open('/content/datac.txt') as story:
  story_data = story.read()

# print(story_data)

lower_data = story_data.lower()           # Converting the string to lower case to get uniformity

split_data = lower_data.splitlines()      # Splitting the data to get every line seperately but this will give the list of uncleaned data

# print(split_data)

split_data.pop(0)

# split_data

final = ''                                # initiating a argument with blank string to hold the values of final cleaned data

for line in split_data:
  final += '\n' + line

# print(final)

final_data = final.split('\n')       # splitting again to get list of cleaned and splitted data ready to be processed
# print(final_data)

final_data = [x for x in final_data if x != '']
# print(final_data)

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Instantiating the Tokenizer
max_vocab = 1000000
tokenizer = Tokenizer(num_words=max_vocab)
tokenizer.fit_on_texts(final_data)

# Getting the total number of words of the data.
word2idx = tokenizer.word_index
print(len(word2idx))
print(word2idx)
vocab_size = len(word2idx) + 1        # Adding 1 to the vocab_size because the index starts from 1 not 0. This will make it uniform when using it further
# print(vocab_size)

input_seq = []

for line in final_data:
  token_list = tokenizer.texts_to_sequences([line])[0]
  for i in range(1, len(token_list)):
    n_gram_seq = token_list[:i+1]
    input_seq.append(n_gram_seq)

# print(input_seq)

# Getting the maximum length of sequence for padding purpose
max_seq_length = max(len(x) for x in input_seq)
print(max_seq_length)

# Padding the sequences and converting them to array
input_seq = np.array(pad_sequences(input_seq, maxlen=max_seq_length, padding='pre'))
print(input_seq)

# Taking xs and labels to train the model.

xs = input_seq[:, :-1]        # xs contains every word in sentence except the last one because we are using this value to predict the y value
labels = input_seq[:, -1]     # labels contains only the last word of the sentence which will help in hot encoding the y value in next step
print("xs: ",xs)
print("labels:",labels)

from tensorflow.keras.utils import to_categorical

# one-hot encoding the labels according to the vocab size

# The matrix is square matrix of the size of vocab_size. Each row will denote a label and it will have 
# a single +ve value(i.e 1) for that label and other values will be zero. 

ys = to_categorical(labels, num_classes=vocab_size)
print(ys)

from tensorflow.keras.layers import Input, Dense, Embedding, LSTM, Dropout, Bidirectional, GlobalMaxPooling1D
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import Sequential

# using the functional APIs of keras to define the model

i = Input(shape=(max_seq_length - 1, ))                           # using 1 less value becasuse we are preserving the last value for predicted word 
x = Embedding(vocab_size, 124)(i)
x = Dropout(0.2)(x)
x = LSTM(520, return_sequences=True)(x)
x = Bidirectional(layer=LSTM(340, return_sequences=True))(x)
x = GlobalMaxPooling1D()(x)
x = Dense(1024, activation='relu')(x)
x = Dense(vocab_size, activation='softmax')(x)

model = Model(i,x)

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
r = model.fit(xs, ys, batch_size=32, epochs=100, use_multiprocessing=True, workers=-1)

# Evaluating the model on accuracy
import matplotlib.pyplot as plt
plt.plot(r.history['accuracy'])

def predict_words(seed, no_words):
  for i in range(no_words):
    token_list = tokenizer.texts_to_sequences([seed])[0]
    token_list = pad_sequences([token_list], maxlen=max_seq_length-1, padding='pre')
    predicted = np.argmax(model.predict(token_list), axis=1)

    new_word = ''

    for word, index in tokenizer.word_index.items():
      if predicted == index:
        new_word = word
        break
    seed += " " + new_word
  print(seed)

seed_text = 'I wish i could kill someone right now '
next_words = 10

predict_words(seed_text, next_words)

seed_text = 'what do you know about computers? '
next_words = 20

predict_words(seed_text, next_words)

seed_text = 'you know what? you dont make sense most of the time '
next_words = 20

predict_words(seed_text, next_words)

seed_text = 'so what should i do about it? Its useless to talk to you '
next_words = 20

predict_words(seed_text, next_words)

seed_text = ' you are such a piece of shit'
next_words = 20

predict_words(seed_text, next_words)

# model.save('chad_generator.h5')

