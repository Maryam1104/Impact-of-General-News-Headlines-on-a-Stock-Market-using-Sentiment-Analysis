# -*- coding: utf-8 -*-
"""SentimentAnalysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1enZTgRyLyti9TcssobgNHv1Ehpz0x7mx

## Raw data
After Manual Cleaning
"""

from google.colab import files
uploaded = files.upload()

"""Train Dataset"""

import pandas as pd
import io

data = pd.read_csv(io.BytesIO(uploaded['Training_dataset_News_Headlines.csv']))
data.head(3)

"""Test Dataset"""

test_data = pd.read_csv(io.BytesIO(uploaded['Test_dataset_News_Headlines.csv']))
test_data.head(3)

print("Original train data file dimensions >>> shape: " , data.shape, " ,  size: ", data.size)
print("Original test  data file dimensions >>> shape: " , test_data.shape, " ,  size: ", test_data.size)

"""### Train-Validation Data Preperation (with split)"""

from sklearn.model_selection import train_test_split
X_train, X_val, y_train, y_val = train_test_split(data[['News']], data[['Situation']], test_size=0.25, shuffle=False)

"""train-data"""

X_train.shape
y_train.shape

"""validation-data"""

# X_val.shape
# y_val.shape
X_val

"""### Test Data Preparation"""

X_test = test_data[['News']]
X_test.shape

"""## Data Preprocessing"""

import re
import nltk
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

from nltk.corpus import stopwords
stop_words = stopwords.words('english')
from nltk.stem import PorterStemmer
stemmer = PorterStemmer()
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

def data_preprocessing(data):
  cleaned_data = []
  for index,row in data.iterrows():
      filter_sentence = []
      sentence = row['News']
      sentence = sentence.lower() #conversion to lowercase
      sentence = re.sub(r'[^\w\s]','',str(sentence))    #punctuation removal
      words = nltk.word_tokenize(sentence)  #tokenization
      words = [w for w in words if not w in stop_words] #stopwords removal
      for word in words:
          filter_sentence.append(lemmatizer.lemmatize(word))
      # print(filter_sentence)
      cleaned_text = " ".join(filter_sentence)
      # print(cleaned_text)
      cleaned_data.append(cleaned_text)
  return cleaned_data

"""Train data preprocessing


"""

# data_preprocessing(data)
X_clean = data_preprocessing(X_train)
print(X_clean)

"""Validation data preprocessing"""

Xv_clean = data_preprocessing(X_val)
print(Xv_clean)

"""**Test data preprocessing**"""

Xt_clean = data_preprocessing(X_test)
print(Xt_clean)

"""## Feature Extraction

Here we **scale the training data** and also **learn the scaling parameters** of that data i.e. mean and variance of the features of the training set are learned and will be used later for test data: `fit_transform`
"""

#vectorization
from sklearn.feature_extraction.text import CountVectorizer

cv = CountVectorizer(ngram_range=(1,2))
X_vec = cv.fit_transform(X_clean).toarray()
X_vec.shape

cv

X_vec

print(cv.get_feature_names()) #Bag-of-Words Model

"""Now, we can use the same mean and variance calculated from our training data to **transform our test data**:
`transform`

Validation Data Transformation
"""

xv_vec = cv.transform(Xv_clean).toarray()
xv_vec.shape
print(cv.get_feature_names())

"""**Test Data Transformation**"""

xt_vec = cv.transform(Xt_clean).toarray()
xt_vec.shape
print(cv.get_feature_names())

"""# (1) Sentiment Analysis

**Model 1 - Naive Bayes Classifier**
"""

from sklearn.naive_bayes import MultinomialNB

mn = MultinomialNB()
mn.fit(X_vec, y_train)
yv_pred = mn.predict(xv_vec)
# y_pred = mn.predict(xt_vec)
# print(y_pred)

from sklearn.metrics import accuracy_score
accuracy_score(y_val, yv_pred) * 100

"""**Model 2  - SVM Classifier**


"""

from sklearn.svm import SVC

clf = SVC()
clf.fit(X_vec, y_train)
# y_pred = clf.predict(xt_vec)
# print(y_pred)

yv_pred = clf.predict(xv_vec)
from sklearn.metrics import accuracy_score
accuracy_score(y_val, yv_pred) * 100

"""**Model 3  - Logistic Regression Classifier**


"""

from sklearn.linear_model import LogisticRegression

clf = LogisticRegression(random_state=0).fit(X_vec, y_train)

# y_pred = clf.predict(xt_vec)
# print(y_pred)

yv_pred = clf.predict(xv_vec)
from sklearn.metrics import accuracy_score
accuracy_score(y_val, yv_pred) * 100

"""**Model 4  - Random Forest Classifier**


"""

# from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

# clf = DecisionTreeClassifier(random_state=0)
# clf.fit(X_vec, y_train)

clf = RandomForestClassifier(n_estimators=50, random_state=1).fit(X_vec, y_train)
# y_pred = clf.predict(xt_vec)
# print(y_pred)

yv_pred = clf.predict(xv_vec)
from sklearn.metrics import accuracy_score
accuracy_score(y_val, yv_pred) * 100

"""**Model 4  - MLP Classifier**"""

from sklearn.neural_network import MLPClassifier

clf = MLPClassifier(random_state=1, max_iter=300).fit(X_vec, y_train)
# y_pred = clf.predict(xt_vec)
# print(y_pred)

yv_pred = clf.predict(xv_vec)
from sklearn.metrics import accuracy_score
accuracy_score(y_val, yv_pred) * 100

"""## Final - Ensemble Approach (Majority Voting)"""

from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier, VotingClassifier

mn = MultinomialNB()
svc = SVC()
lr = LogisticRegression(random_state=0)
rf = RandomForestClassifier(n_estimators=50, random_state=1)
mlp = MLPClassifier(random_state=1, max_iter=300)

eclf = VotingClassifier(estimators=[('mn', mn), ('svc', svc), ('lr', lr), ('rf', rf), ('mlp', mlp)], voting='hard')
eclf.fit(X_vec, y_train)

"""**Predictions on Validation Data**"""

yv_pred = eclf.predict(xv_vec)
# print(yv_pred)

X_validation = X_val
X_validation['Situation(Actual)'] = y_val
X_validation['Situation(Predicted)'] = yv_pred

X_validation = X_validation.reset_index(drop=True)
X_validation #.head(5)

"""**Predictions on Test Data**"""

y_pred = eclf.predict(xt_vec)
# print(y_pred)

X_test['Situation_Predicted'] = y_pred
X_test.head(5)

"""Save this data to a file"""

# file_name = "Predicted-Situation.csv"
# X_test.to_csv(file_name)
# files.download(file_name)

"""### Results for Sentiment Analysis Model(s)

Accuracy
"""

from sklearn.metrics import accuracy_score

accuracy_score(y_val, yv_pred) * 100

"""Precision - Recall - Fscore"""

from sklearn.metrics import precision_recall_fscore_support

precision_recall_fscore_support(y_val, yv_pred, average='macro')

"""# (2)Correlation Analysis

### Data Preparation

Stock Exchange Data
"""

stocks_data = pd.read_csv(io.BytesIO(uploaded['stock_exchange_data _jan_feb.csv']))
stocks_data.head(5)

print("Stocks data file dimensions >>> shape: " , stocks_data.shape, " ,  size: ", stocks_data.size)

X_stocks = stocks_data[['Date', 'Open']]
print(X_stocks.shape)
X_stocks.head(5)

#@title Default title text
##** Code to Get stocks 'Open' value only for Jan-Feb ?????** ##

# X_stocks = pd.DataFrame(columns=['Date', 'Open'])

# date = (stocks_data['Date']) == '%Jan%'
# X_stocks[date]

# # for index, row in stocks_data.iterrows():
# #   splitted = str(row['Date']).split('-')
# #   if(splitted[1] == 'Feb' or splitted[1] == 'Jan'):
# #     # X_stocks.loc[index]['Date'] = row['Date']

# X_stocks
# # X_stocks = stocks_data[['Open']]

"""News Headlines Data


> We are using train data for analysis - because it is more carefully tagged and hence would allow us to perform better correlation analysis using that data.


"""

data['Situation_Numeric'] = 0
for index,row in data.iterrows():
  if(row['Situation'] == "Positive"):
    data.loc[index, 'Situation_Numeric'] = 1

news_data = data.copy()

"""Lets read data in backwards (as per the requirement)"""

news_data = news_data.sort_index(axis=1 ,ascending=True)
news_data = news_data.iloc[::-1]
news_data = news_data.reset_index(drop=True)
news_data

X_news = news_data[['Date', 'Situation_Numeric']]
print(X_news.shape)
X_news.head(10)

"""### Combining News and Stocks data

We need to perform correlation analysis of **current day's news** *on* **next day's opening stock prices**

So we need to prepare our data to run for such situation
"""

def get_date_month(date, dtype):
  dm = ""
  if(dtype == 'news'):
    split = date.split(",")
    dm = split[0]

  if(dtype == 'stocks'):
    split = date.split("-")
    dm = " ".join((split[0], split[1]))

  date_month = dm
  return date_month

"""Our **News data** has many values against a single date(day) e.g.
`3 news headlines for 28 Feb.`

We seperate only the *`DD MM`* part from the date column and create a new column.
"""

X_news['DM']  = 'null'
for i, r in X_news.iterrows():
    news_dm = get_date_month(str(r['Date']), 'news')
    X_news.loc[i, 'DM'] = news_dm
X_news

#@title Get all unique date values in an array to use it for referencing purpose later..

# file_name = "Training_dataset_News_Headlines_numeric_labels.csv"
# X_news[['Situation_Numeric', 'DM']].to_csv(file_name)
# # files.download(file_name)

# X_news_dm = X_news.DM.unique()
# X_news_dm

# X_stocks.Date.unique()

#@title Default title text
# for i, row in X_stocks.iterrows():
#   stocks_dm = get_date_month(str(row['Date']), 'stocks')

# for i, row in X_stocks.iterrows():
#   count = 0
#   for j, r in X_news.iterrows():
#     # if X_stocks_dm_uq has date 29 && X_news_dm_uq has date 28:

# x = []
# y = []

# for i, row in X_stocks.iterrows():
#   stocks_dm = get_date_month(str(row['Date']), 'stocks')
#   count = 0
#   for j, r in X_news.iterrows():
#     news_dm = get_date_month(str(r['Date']), 'news')
#     if(news_dm == stocks_dm):
#       print(news_dm, " ---- ", stocks_dm)
#       # x.append(r['Situation_Numeric'])
#       # count +=1

"""### Correlation Analysis using Pearson's Correlation



"""

stocksxnews_data = pd.read_excel(io.BytesIO(uploaded['stocksxnews_data_jan_feb.xlsx']))
stocksxnews_data[['Date', 'Stock_Price_Open', 'Previous_Day_Sentiment']]

from sklearn import preprocessing

# x_norm = preprocessing.normalize(x)
min_max_scaler = preprocessing.MinMaxScaler()
x_norm = min_max_scaler.fit_transform(stocksxnews_data[['Stock_Price_Open']])

import numpy as np

x = x_norm.reshape(-1)
y = np.array(stocksxnews_data['Previous_Day_Sentiment'])

print(x.shape)
print(y.shape)

print(y)

"""**Pearson's Correlation**"""

import scipy.stats

pr_value = scipy.stats.pearsonr(x, y)
print("correlation coeffienct:", pr_value[0], " ,   p-value:", pr_value[1])

"""Plot data for correlation understanding"""

import matplotlib.pyplot as plt

plt.scatter(x, y)
plt.show()