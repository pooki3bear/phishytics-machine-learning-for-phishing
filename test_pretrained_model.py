# Basic libraries
import os
import io
import sys
import math
import time
import random
import requests
import collections
import numpy as np
from os import walk
import pandas as pd
import matplotlib.pyplot as plt
from joblib import dump, load
plt.style.use('seaborn-white')
plt.rc('grid', linestyle="dotted", color='#a0a0a0')
plt.rcParams['axes.edgecolor'] = "#04383F"

from tokenizers import ByteLevelBPETokenizer
from langdetect import detect

"""
How to run:
python3 test_pretrained_model.py --tokenizer_folder pretrained-models --threshold 0.5 --model_dir pretrained-models --website_to_test https://www.google.com
"""

# Parsing arguments
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--tokenizer_folder", type=str, default = "pretrained-models", help="Folder where tokenizer files have been placed")
parser.add_argument("--threshold", type=float, default = 0.5, help="Which threshold to use for testing")
parser.add_argument("--model_dir", type=str, default = "pretrained-models", help="Directory of trained models.")
parser.add_argument("--website_to_test", type=str, default = "https://www.google.com", help="Website to test")

args = parser.parse_args()
tokenizerFolder = args.tokenizer_folder
savedModelDirectory = args.model_dir
websiteToTest = args.website_to_test
threshold = args.threshold

# Loading files
# Load tokenization files
tokenizer = ByteLevelBPETokenizer(
    tokenizerFolder + "/pretrained_Tokenizer-10000.tok-vocab.json",
    tokenizerFolder + "/pretrained_Tokenizer-10000.tok-merges.txt",
)
tokenizerVocabSize = tokenizer.get_vocab_size()
print("Tokenizer files have been loaded and the vocab size is %d..." % tokenizerVocabSize)

# Load saved model
model = load(savedModelDirectory + "/pretrained-phishytics-model.joblib")
print("Model loaded...")

# Load document frequency dictionary
docDict = np.load(savedModelDirectory + "/document-frequency-dictionary.npy", allow_pickle=True).item()
print("Document frequency dictionary loaded...")

# Testing
print("Loading webpage...")
try:
	request = requests.get(websiteToTest)
	webpageHtml = str(request.text)
	webpageHtml = webpageHtml.replace("\n", " ")

	# Convert text into feature vector
	output = tokenizer.encode(webpageHtml)
	outputDict = collections.Counter(output.ids)
except:
	print("**** Error loading the website ****")

# Apply tfidf weighting
totalFilesUnderConsideration = 18500 # total number of documents/html files in our training data
array = [0] * tokenizerVocabSize
for item in outputDict:
	if len(docDict[item]) > 0:
		array[item] = (outputDict[item]) * (math.log10( totalFilesUnderConsideration / len(docDict[item] )))

# Getting predictions
predictionProbability = model.predict_proba([array])[0][1]
print("\n****************************\n--> Probability that the website is phishing: %.2f" % (predictionProbability * 100))

prediction = "NOT PHISHING"
if predictionProbability > threshold:
	prediction = "PHISHING"
print("--> Based on your threshold of %.2f, this website is +++'%s'+++" % (threshold, prediction))
print("****************************")