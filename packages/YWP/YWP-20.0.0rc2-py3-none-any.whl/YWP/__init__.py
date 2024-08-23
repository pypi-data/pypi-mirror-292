r"""
Created By Your Wanted Products (YWP)

Email: pbstzidr@ywp.freewebhostmost.com

Phone Number: +201096730619

WhatsApp Number: +201096730619

website: https://ywp.freewebhostmost.com
























"""

# import numpy as np
# import json
# import pickle
# import nltk
# from nltk.stem.lancaster import LancasterStemmer
# import tensorflow as tf
# from tensorflow.keras.layers import Dense
# from tensorflow.keras.models import Sequential
# from vosk import Model, KaldiRecognizer
# import random
# import string

# class AI:

#     class Builder:

#         def __init__(self):
#             self.intents = []

#         def json_creator(self, jsonfile: str = "intents.json", tag: str = "", patterns: list = [], responses: list = []) -> None:
#             """
#             Creates or appends intents to a JSON file.

#             Args:
#             - jsonfile (str): Path to the JSON file.
#             - tag (str): Tag name for the intent.
#             - patterns (list): List of patterns or queries.
#             - responses (list): List of responses corresponding to the patterns.

#             Returns:
#             - None
#             """
#             intents = self.intents

#             intents.append({
#                 "tag": tag,
#                 "patterns": patterns,
#                 "responses": responses
#             })

#             with open(jsonfile, 'w', encoding='utf-8') as f:
#                 json.dump({"intents": intents}, f, indent=4, ensure_ascii=False)

#         def train(self, jsonfile: str = "intents.json", picklefile: str = "data.pickle", h5file: str = "model.h5") -> str:
#             """
#             Trains an AI model using intents JSON file and saves the model.

#             Args:
#             - jsonfile (str): Path to the intents JSON file.
#             - picklefile (str): Path to save/load the pickle data.
#             - h5file (str): Path to save/load the trained model weights.

#             Returns:
#             - str: Message indicating the training status.
#             """
#             nltk.download('punkt')
#             stemmer = LancasterStemmer()

#             try:
#                 with open(jsonfile, encoding='utf-8') as file:
#                     data = json.load(file)
#             except:
#                 return 'error:jsonnotfound'

#             try:
#                 with open(picklefile, "rb") as f:
#                     words, labels, training, output = pickle.load(f)
#             except:
#                 words = []
#                 labels = []
#                 docs_x = []
#                 docs_y = []
#                 for intent in data["intents"]:
#                     for pattern in intent["patterns"]:
#                         wrds = nltk.word_tokenize(pattern)
#                         words.extend(wrds)
#                         docs_x.append(wrds)
#                         docs_y.append(intent["tag"])

#                     if intent["tag"] not in labels:
#                         labels.append(intent["tag"])

#                 words = [stemmer.stem(w.lower()) for w in words if w != "?"]
#                 words = sorted(list(set(words)))

#                 labels = sorted(labels)

#                 training = []
#                 output = []

#                 out_empty = [0 for _ in range(len(labels))]

#                 for x, doc in enumerate(docs_x):
#                     bag = []

#                     wrds = [stemmer.stem(w) for w in doc]

#                     for w in words:
#                         if w in wrds:
#                             bag.append(1)
#                         else:
#                             bag.append(0)

#                     output_row = out_empty[:]
#                     output_row[labels.index(docs_y[x])] = 1

#                     training.append(bag)
#                     output.append(output_row)

#                 training = np.array(training)
#                 output = np.array(output)

#                 with open(picklefile, "wb") as f:
#                     pickle.dump((words, labels, training, output), f)

#             model = Sequential()
#             model.add(Dense(8, input_shape=(len(training[0]),), activation='relu'))
#             model.add(Dense(8, activation='relu'))
#             model.add(Dense(len(output[0]), activation='softmax'))

#             model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

#             try:
#                 model.load_weights(h5file)
#             except:
#                 model.fit(training, output, epochs=1000, batch_size=8, verbose=1)
#                 model.save(h5file)

#             return 'done'

#         @staticmethod
#         def bag_of_words(s: str, words: list) -> np.ndarray:
#             """
#             Converts a sentence into a bag of words format.

#             Args:
#             - s (str): Sentence or message to convert.
#             - words (list): List of words to match against.

#             Returns:
#             - np.ndarray: Bag of words representation of the sentence.
#             """
#             stemmer = LancasterStemmer()

#             bag = [0 for _ in range(len(words))]

#             s_words = nltk.word_tokenize(s)
#             s_words = [stemmer.stem(word.lower()) for word in s_words]

#             for se in s_words:
#                 for i, w in enumerate(words):
#                     if w == se:
#                         bag[i] = 1

#             return np.array(bag)

#         def process(self, message: str = "", picklefile: str = "data.pickle", h5file: str = "model.h5", jsonfile: str = "intents.json", sleeptime: int = 0) -> str:
#             """
#             Processes a message using the trained AI model and returns a response.

#             Args:
#             - message (str): Input message to process.
#             - picklefile (str): Path to the pickle file containing training data.
#             - h5file (str): Path to the trained model weights.
#             - jsonfile (str): Path to the intents JSON file.
#             - sleeptime (int): Optional sleep time before returning a response.

#             Returns:
#             - str: AI response based on the input message.
#             """
#             nltk.download('punkt')
#             stemmer = LancasterStemmer()

#             try:
#                 with open(jsonfile, encoding='utf-8') as file:
#                     data = json.load(file)
#             except:
#                 return 'error:jsonnotfound'

#             try:
#                 with open(picklefile, "rb") as f:
#                     words, labels, training, output = pickle.load(f)
#             except:
#                 return 'error:picklenotfound'

#             model = Sequential()
#             model.add(Dense(8, input_shape=(len(training[0]),), activation='relu'))
#             model.add(Dense(8, activation='relu'))
#             model.add(Dense(len(output[0]), activation='softmax'))

#             model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

#             try:
#                 model.load_weights(h5file)
#             except:
#                 return 'h5notfound'

#             bag = self.bag_of_words(message, words)
#             results = model.predict(np.array([bag]))[0]
#             results_index = np.argmax(results)
#             tag = labels[results_index]
#             if results[results_index] > 0.8:
#                 for tg in data["intents"]:
#                     if tg['tag'] == tag:
#                         responses = tg['responses']
#                 sleep(sleeptime)
#                 Bot = random.choice(responses)
#                 return Bot
#             else:
#                 return "I don't understand!"

def help():
    """This is YWP.help Command in Command Line"""
    print("""Avalable Commands:
1- YWP.install_packages
2- YWP.install_libraries
3- YWP.upgrade_libraries
4- YWP.upgrade_library
5- YWP
6- YWP.help""")

# import inspect

# def get_function_code(function_name):
#     # الحصول على كائن الوظيفة من خلال الاسم
#     func = globals().get(function_name)
#     if func is None:
#         return f"No function named {function_name} found."
    
#     # الحصول على كود الوظيفة
#     source_code = inspect.getsource(func)
#     return source_code


# def get_class_code(class_name):
#     # الحصول على كائن الكلاس من خلال الاسم
#     cls = globals().get(class_name)
#     if cls is None:
#         return f"No class named {class_name} found."
    
#     # الحصول على كود الكلاس
#     source_code = inspect.getsource(cls)
#     return source_code
