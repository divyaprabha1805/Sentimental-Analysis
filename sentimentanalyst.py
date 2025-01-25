# -*- coding: utf-8 -*-
"""SentimentAnalyst.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1LbCT1_Q0SOHJ0z7LTFAKYtsSl2COCH7U

Importing the libraries
"""

##IMPORTING THE LIBRARIES
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random
from wordcloud import WordCloud
from wordcloud import STOPWORDS

"""Reading the csv file from google drive"""

#MOUNTING THE DRIVE
from google.colab import drive
drive.mount('/content/drive')

#READING THE CSV FILE
DF = pd.read_csv('/content/drive/MyDrive/ML/Sentiment Analysis.csv')
DF

"""Data preprocessing"""

# Check for missing values
missing_values = DF.isnull().sum()
print(missing_values)

#AS THE LAST FIVE COLUMNS ARE NULL WE ARE DROPPING THE LAST FIVE COLUMNS
DF=DF.iloc[:,:-5]
DF

#DESCRIBING THE DATA
print(DF.describe())

#CHECKING FOR DUPLICATES
DF.duplicated().value_counts()

#REMOVING ALL THE DUPLICATES
DF = DF.drop_duplicates()
DF.duplicated().value_counts()

"""Preprocessing using NLTK"""

#IMPORTING THE NLTK PACKAGE
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.sentiment import SentimentIntensityAnalyzer

#DOWLOADING THE NLTK RESOURCES
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('vader_lexicon')

"""Finding sentiment score using NLTK"""

#INITIALIZING THE SENTIMENT INTENSITY ANALYSER
sia = SentimentIntensityAnalyzer()

#FUNCTION TO APPLY SENTIMENT ANALYSIS FOR SINGLE TEXT
def analyze_sentiment(text):
    sentiment_scores = sia.polarity_scores(text)
    return sentiment_scores['compound']

#APPLYING THE SENTIMENT ANALYSIS SCORE FOR THE TEXT DATA
# Instead of directly assigning to DF['sentiment_score'], use .loc to avoid the warning.
DF.loc[:, 'sentiment_score'] = DF['review'].apply(analyze_sentiment)
#DF['sentiment_score'] = DF['review'].apply(analyze_sentiment)
DF

def predict_class(score):
  if score < 0:
    return 0;
  else:
    return 1;
# Use .loc to avoid the SettingWithCopyWarning
DF.loc[:, 'Predicted_sentiment_score'] = DF['sentiment_score'].apply(predict_class)

#DF['Predicted_sentiment_score'] = DF['sentiment_score'].apply(predict_class)
#COUNTING THE NUMBER OF MISMATCHES
count=0
for index,row in DF.iterrows():
  if row['Predicted_sentiment_score']!=row['Sentiment']:
    count+=1
print("The percentage of predicted value that is wrong ",count*100/len(DF))

"""NLTK preprocessing to make the data fit for modelling"""

#DEFINING FUCNTIONS TO PERFORM THE NLTK PREPROCESSING STEPS

#1.USED TO TOKENIZE THE TEXT DATA                                               - EX : I AM ASH =>['I','AM','ASH']
def tokenize_text(text):
    tokens = word_tokenize(text)
    return tokens
#Tokenization is the process of splitting a text into individual words or units.

#2.USED TO REMOVE COMMON ENGLISH STOPWORDS FROM TOKENISED DATA
def remove_stopwords(tokens):
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word.lower() not in stop_words]
    return filtered_tokens
#Stopwords are words that are considered to be of little value in text analysis because they are very common and don't carry much meaningful information (e.g., "the," "and," "in").
#We use the NLTK library's list of English stopwords to identify and remove them from the list of tokens.

# 3.USED TO NORMALIZE THE TOKEN                                                 - EX : ["loving", "cats"]  => ["love", "cat"]
def lemmatize_text(tokens):
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return lemmatized_tokens
#Lemmatization is the process of reducing words to their base or root form. It aims to normalize words so that different inflections or forms of the same word are represented by a common base form.
#It uses the WordNetLemmatizer from the NLTK library to perform lemmatization.

#4.MAIN FUNCTION TO PERFORM ALL NLTK PREPROCESSING
def preprocess_text(text):
    tokens = tokenize_text(text)
    tokens = remove_stopwords(tokens)
    tokens = lemmatize_text(tokens)
    return ' '.join(tokens)  # Join the tokens back into a single string

#5.SIMILAR TO LEMATIZATION
def stem_text(tokens):
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(word) for word in tokens]
    return stemmed_tokens

import nltk
nltk.download('punkt')
# Download the required NLTK resource
#nltk.download('punkt')

# Proceed with your DataFrame operations
DF['review'] = DF['review'].apply(preprocess_text)

!pip uninstall nltk
!pip install nltk

#STORING THE PREPROCESSED DATA INTO A SEPERATE CSV FILE
DF.to_csv('Preprocessed_DataFrame.csv',index=False)
DF2=pd.read_csv('/content/Preprocessed_DataFrame.csv')
DF2

"""Bag of Words(BoW)"""

from sklearn.feature_extraction.text import CountVectorizer
# Create a CountVectorizer instance
vectorizer = CountVectorizer()

#FIT AND TRANFORM THE PREPROCESSED DATA
bow_matrix = vectorizer.fit_transform(DF['review'])
#The result is a sparse matrix where each row corresponds to a document (review), and each column corresponds to a unique word in your dataset.

bow_array = bow_matrix.toarray()
# The vocabulary (unique words) can be accessed as follows:
vocabulary = vectorizer.get_feature_names_out()
bow_df = pd.DataFrame(bow_array, columns=vocabulary)
bow_df

"""Calculating TF-IDF for BoW"""

from sklearn.feature_extraction.text import TfidfVectorizer
# Create a TfidfVectorizer instance
tfidf_vectorizer = TfidfVectorizer()

# Fit and transform the BoW DataFrame to obtain TF-IDF values
tfidf_matrix = tfidf_vectorizer.fit_transform(bow_df)

# Convert the tfidf_matrix to a DataFrame for better visualization (optional)
import pandas as pd
tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=tfidf_vectorizer.get_feature_names_out())

# Print the TF-IDF DataFrame
tfidf_df

"""Visulaization

Pie chart for positive and negative reviews
"""

#PLOTTING THE PIE CHART FOR THE COLUMN SENTIMENT
CLASS_COUNT=[]
CLASS_COUNT.append(DF['Sentiment'].value_counts()[1])
CLASS_COUNT.append(DF['Sentiment'].value_counts()[0])
print(CLASS_COUNT)

# Creating plot
fig,ax = plt.subplots()
Class=['1','0']
explode=[0,0.1]
ax.pie(CLASS_COUNT,labels=Class,explode=explode,autopct='%1.1f%%')
plt.legend(Class)
plt.title("THE SENTIMENT DATA CLASS")
plt.show()

"""Word cloud for drug names"""

#CONCATENATING ALL THE DRUG NAMES FROM THE COLUMN 'drugName' INTO A SINGLE STRING
text_data = ' '.join(DF['drugName'].astype(str))
#CREWATING WORD CLOUD OBJECT
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_data)

plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')  # Hide the axis
plt.show()

"""Top 10 drug names"""

plt.figure(figsize=(12,6))
conditions = DF['drugName'].value_counts(ascending = False).head(10)

plt.bar(conditions.index,conditions.values)
plt.title('Top 10 Drug Names',fontsize = 20)
plt.xticks(rotation=90)
plt.ylabel('count')
plt.show()

"""Bottom 10 drug names"""

plt.figure(figsize=(12,6))
conditions = DF['drugName'].value_counts(ascending = False).tail(10)

plt.bar(conditions.index,conditions.values)
plt.title('Bottom- 10 Drug Names',fontsize = 20)
plt.xticks(rotation=90)
plt.ylabel('count')
plt.show()

"""Word cloud for all conditions"""

#CONCATENATING ALL THE CONDITIONS FROM THE COLUMN 'condition' INTO A SINGLE STRING
text_data = ' '.join(DF['condition'].astype(str))
#CREWATING WORD CLOUD OBJECT
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_data)

plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')  # Hide the axis
plt.show()

"""Top 5 conditions"""

plt.figure(figsize=(12,6))
conditions = DF['condition'].value_counts(ascending = False).head(5)

plt.bar(conditions.index,conditions.values)
plt.title('Top 05 Conditions',fontsize = 20)
plt.xticks(rotation=90)
plt.ylabel('count')
plt.show()

"""Bottom 5 conditions"""

plt.figure(figsize=(12,6))
conditions = DF['condition'].value_counts(ascending = False).tail(5)

plt.bar(conditions.index,conditions.values)
plt.title('Bottom 05 Conditions',fontsize = 20)
plt.xticks(rotation=90)
plt.ylabel('count')
plt.show()

"""Number of drugs per condition"""

#lets check the number of drugs/condition
result = DF.groupby('condition')['drugName'].nunique().sort_values(ascending=False).head(20)

# Create a bar chart
plt.figure(figsize=(12, 6))
result.plot(kind='bar', color='skyblue')
plt.title('Top 20 Conditions with the Most Unique Drugs')
plt.xlabel('Condition')
plt.ylabel('Number of Unique Drugs')
plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability

# Display the plot
plt.tight_layout()
plt.show()

"""Top 20 number of conditions per drug"""

#lets check the number of drugs present in our dataset condition wise
conditions_gp = DF.groupby('drugName')['condition'].nunique().sort_values(ascending=False)

#plot the top 20
# Setting the Parameter
condition_gp_top_20 = conditions_gp.head(20)
sns.set(font_scale = 1.2, style = 'darkgrid')
plt.rcParams['figure.figsize'] = [12, 6]
sns.barplot(x = condition_gp_top_20.index, y = condition_gp_top_20.values)
plt.title('Top-20 Number of condition per drugs',fontsize=20)
plt.xticks(rotation=90)
plt.ylabel('count',fontsize=10)
plt.show()

"""Word cloud for positive reviews"""

text_data=" "
for index,row in DF.iterrows():
  if row['Sentiment']==1:
    text_data += str(row['review'])

#CREATING WORD CLOUD OBJECT
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_data)

plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')  # Hide the axis
plt.show()

"""Word cloud for negative reviews"""

text_data=" "
for index,row in DF.iterrows():
  if row['Sentiment']==0:
    text_data += str(row['review'])

#CREATING WORD CLOUD OBJECT
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_data)

plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')  # Hide the axis
plt.show()

"""Model training and evaluation

KNN
"""

from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
#Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(DF2['review'], DF2['Sentiment'], test_size=0.2, random_state=42)

tfidf_vectorizer = TfidfVectorizer()
X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)
X_test_tfidf = tfidf_vectorizer.transform(X_test)

#Create and train a KNN classifier
knn_classifier = KNeighborsClassifier(n_neighbors=5)  # You can adjust the number of neighbors (k)
knn_classifier.fit(X_train_tfidf, y_train)
# Make predictions on the test data
y_pred = knn_classifier.predict(X_test_tfidf)
print(classification_report(y_test, y_pred))

"""Naive bayes"""

from sklearn.naive_bayes import MultinomialNB
# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(DF2['review'], DF2['Sentiment'], test_size=0.2, random_state=42)

# Create a TfidfVectorizer to convert text data to TF-IDF features
tfidf_vectorizer = TfidfVectorizer()
X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)
X_test_tfidf = tfidf_vectorizer.transform(X_test)

# Create and train a Multinomial Naive Bayes classifier
nb_classifier = MultinomialNB()
nb_classifier.fit(X_train_tfidf, y_train)
# Make predictions on the test data
y_pred = nb_classifier.predict(X_test_tfidf)
# Evaluate the model
print(classification_report(y_test, y_pred))

"""Random forest"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(DF2['review'], DF2['Sentiment'], test_size=0.2, random_state=42)

# Create a TfidfVectorizer to convert text data to TF-IDF features
tfidf_vectorizer = TfidfVectorizer()
X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)
X_test_tfidf = tfidf_vectorizer.transform(X_test)

# Create and train a Random Forest classifier
rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
rf_classifier.fit(X_train_tfidf, y_train)

# Make predictions on the test data
y_pred = rf_classifier.predict(X_test_tfidf)

# Evaluate the model
print(classification_report(y_test, y_pred))

"""SVM with different kernel functions"""

from sklearn.svm import SVC
# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(DF2['review'], DF2['Sentiment'], test_size=0.2, random_state=42)

# Create a TfidfVectorizer to convert text data to TF-IDF features
tfidf_vectorizer = TfidfVectorizer()
X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)
X_test_tfidf = tfidf_vectorizer.transform(X_test)

"""Linear kernel function"""

# Create and train SVM classifiers with different kernels
svm_linear = SVC(kernel='linear', C=1.0)
# Train the SVM classifiers
svm_linear.fit(X_train_tfidf, y_train)
# Make predictions on the test data for each model
y_pred_linear = svm_linear.predict(X_test_tfidf)
# Evaluate each model
print("Linear Kernel SVM:")
print(classification_report(y_test, y_pred_linear))

"""Polynomial kernel function"""

# Create and train SVM classifiers with different kernels
svm_poly = SVC(kernel='poly', degree=3, C=1.0)
# Train the SVM classifiers
svm_poly.fit(X_train_tfidf, y_train)
# Make predictions on the test data for each model
y_pred_poly = svm_poly.predict(X_test_tfidf)
# Evaluate each model
print("Polynomial Kernel SVM:")
print(classification_report(y_test, y_pred_poly))

"""RBF kernel function"""

# Create and train SVM classifiers with different kernels
svm_rbf = SVC(kernel='rbf', C=1.0)
# Train the SVM classifiers
svm_rbf.fit(X_train_tfidf, y_train)
# Make predictions on the test data for each model
y_pred_rbf = svm_rbf.predict(X_test_tfidf)
# Evaluate each model
print("RBF Kernel SVM:")
print(classification_report(y_test, y_pred_rbf))

"""Logistic regression"""

from sklearn.linear_model import LogisticRegression
# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(DF2['review'], DF2['Sentiment'], test_size=0.2, random_state=42)

# Create a TfidfVectorizer to convert text data to TF-IDF features
tfidf_vectorizer = TfidfVectorizer()
X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)
X_test_tfidf = tfidf_vectorizer.transform(X_test)

# Create and train a Logistic Regression classifier
logistic_regression = LogisticRegression(max_iter=1000)  # You can adjust hyperparameters as needed
logistic_regression.fit(X_train_tfidf, y_train)
# Make predictions on the test data
y_pred = logistic_regression.predict(X_test_tfidf)
# Evaluate the model
print(classification_report(y_test, y_pred))

"""Explainable AI - LIME and SHAP"""

!pip install lime shap

import lime
import lime.lime_text
from lime.lime_text import LimeTextExplainer
import shap
from sklearn.pipeline import make_pipeline

"""LIME for KNN"""

# Create a LIME Explainer
explainer = lime.lime_text.LimeTextExplainer(class_names=['class_label_0', 'class_label_1'])

# Select a random test instance (you can choose any instance)
test_instance = X_test.iloc[0]

# Create a pipeline with your KNN classifier and TF-IDF vectorizer
pipeline = make_pipeline(tfidf_vectorizer, knn_classifier)

# Explain the model's prediction for the selected instance
explanation = explainer.explain_instance(test_instance, pipeline.predict_proba)

# Visualize the explanation
explanation.show_in_notebook()

"""LIME for Naive bayes"""

# Create a LIME Explainer
explainer = lime.lime_text.LimeTextExplainer(class_names=['class_label_0', 'class_label_1'])

# Select a random test instance (you can choose any instance)
test_instance = X_test.iloc[0]

# Create a pipeline with your Naive Bayes classifier and TF-IDF vectorizer
pipeline = make_pipeline(tfidf_vectorizer, nb_classifier)

# Explain the model's prediction for the selected instance
explanation = explainer.explain_instance(test_instance, pipeline.predict_proba)

# Visualize the explanation
explanation.show_in_notebook()

"""LIME for logistic regression"""

# Create a LIME Explainer
explainer = lime.lime_text.LimeTextExplainer(class_names=['class_label_0', 'class_label_1'])
# Select a random test instance
test_instance = X_test.iloc[0]
# Create a pipeline with your logistic regression model and TF-IDF vectorizer
pipeline = make_pipeline(tfidf_vectorizer, logistic_regression)
# Explain the model's prediction for the selected instance
explanation = explainer.explain_instance(test_instance, pipeline.predict_proba)

# Visualize the explanation
explanation.show_in_notebook()

"""SHAP for logistic regression"""

# Create a SHAP explainer for the logistic regression model
explainer = shap.Explainer(logistic_regression, X_train_tfidf)
# Calculate SHAP values for the test dataset
shap_values = explainer.shap_values(X_test_tfidf)

# Summary plot for feature importance
shap.summary_plot(shap_values, X_test_tfidf, feature_names=tfidf_vectorizer.get_feature_names_out())

"""UI interface"""

!pip install -q streamlit

!npm install localtunnel

# Commented out IPython magic to ensure Python compatibility.
# %%writefile app.py
# 
# ##IMPORTING THE LIBRARIES
# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# import random                       #FOR PSEUDO RANDOM NUMBER GENERATION
# from wordcloud import WordCloud     #TO VISUALIZE THE TEXT DATA
# from wordcloud import STOPWORDS
# 
# #IMPORTING THE NLTK PACKAGE
# import nltk
# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
# from nltk.stem import PorterStemmer
# from nltk.stem import WordNetLemmatizer
# from nltk.sentiment import SentimentIntensityAnalyzer
# 
# #DOWLOADING THE NLTK RESOURCES
# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('stopwords')
# nltk.download('vader_lexicon')
# 
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.neighbors import KNeighborsClassifier
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import classification_report
# from sklearn.linear_model import LogisticRegression
# 
# # Import the Streamlit library
# import streamlit as st
# 
# 
# #DEFINING FUCNTIONS TO PERFORM THE NLTK PREPROCESSING STEPS
# 
# #1.USED TO TOKENIZE THE TEXT DATA                                               - EX : I AM ASH =>['I','AM','ASH']
# def tokenize_text(text):
#     tokens = word_tokenize(text)
#     return tokens
# #Tokenization is the process of splitting a text into individual words or units.
# 
# #2.USED TO REMOVE COMMON ENGLISH STOPWORDS FROM TOKENISED DATA
# def remove_stopwords(tokens):
#     stop_words = set(stopwords.words('english'))
#     filtered_tokens = [word for word in tokens if word.lower() not in stop_words]
#     return filtered_tokens
# #Stopwords are words that are considered to be of little value in text analysis because they are very common and don't carry much meaningful information (e.g., "the," "and," "in").
# #We use the NLTK library's list of English stopwords to identify and remove them from the list of tokens.
# 
# # 3.USED TO NORMALIZE THE TOKEN                                                 - EX : ["loving", "cats"]  => ["love", "cat"]
# def lemmatize_text(tokens):
#     lemmatizer = WordNetLemmatizer()
#     lemmatized_tokens = [lemmatizer.lemmatize(word) for word in tokens]
#     return lemmatized_tokens
# #Lemmatization is the process of reducing words to their base or root form. It aims to normalize words so that different inflections or forms of the same word are represented by a common base form.
# #It uses the WordNetLemmatizer from the NLTK library to perform lemmatization.
# 
# #4.MAIN FUNCTION TO PERFORM ALL NLTK PREPROCESSING
# def preprocess_text(text):
#     tokens = tokenize_text(text)
#     tokens = remove_stopwords(tokens)
#     tokens = lemmatize_text(tokens)
#     return ' '.join(tokens)  # Join the tokens back into a single string
# 
# #5.SIMILAR TO LEMATIZATION
# def stem_text(tokens):
#     stemmer = PorterStemmer()
#     stemmed_tokens = [stemmer.stem(word) for word in tokens]
#     return stemmed_tokens
# 
# #READING THE CSV FILE
# DF2 = pd.read_csv('/content/Preprocessed_DataFrame.csv')
# print(DF2)
# 
# 
# #-------------------------------------------------
# #KNN
# #--------------------------------------------------
# #Split the data into training and testing sets
# X_train, X_test, y_train, y_test = train_test_split(DF2['review'], DF2['Sentiment'], test_size=0.2, random_state=42)
# 
# #Create a TfidfVectorizer to convert text data to TF-IDF features
# tfidf_vectorizer = TfidfVectorizer()
# X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)
# X_test_tfidf = tfidf_vectorizer.transform(X_test)
# 
# #Create and train a KNN classifier
# knn_classifier = KNeighborsClassifier(n_neighbors=5)  # You can adjust the number of neighbors (k)
# knn_classifier.fit(X_train_tfidf, y_train)
# 
# # Make predictions on the test data
# #y_pred = knn_classifier.predict(X_test_tfidf)
# 
# #----------------------------------
# #LOGISTIC REGRESSION
# #----------------------------------
# # Split the data into training and testing sets
# X_train, X_test, y_train, y_test = train_test_split(DF2['review'], DF2['Sentiment'], test_size=0.2, random_state=42)
# # Create a TfidfVectorizer to convert text data to TF-IDF features
# tfidf_vectorizer = TfidfVectorizer()
# X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)
# X_test_tfidf = tfidf_vectorizer.transform(X_test)
# 
# # Create and train a Logistic Regression classifier
# logistic_regression = LogisticRegression(max_iter=1000)  # You can adjust hyperparameters as needed
# logistic_regression.fit(X_train_tfidf, y_train)
# 
# 
# # Set the heading
# st.markdown("# DRUG REVIEW SENTIMENT ANALYSIS")
# 
# # Add a title for your app
# st.title("TEST DATA INPUT")
# 
# # Add a text input field where the user can enter the drug name
# drug_name = st.text_input("ENTER THE NAME OF THE DRUG : ", ' ')
# 
# # Add a text input field where the user can enter the condition name
# condition_name = st.text_input("ENTER THE CONDITION FOR WHICH THE DRUG IS USED : ", " ")
# 
# # Add a text input field where the user can enter the review
# review = str(st.text_input("ENTER THE REVIEW OF THE DRUG : ", " "))
# 
# # Create a dictionary to hold user inputs
# user_input = {'drugName': [drug_name], 'condition': [condition_name], 'review': [review]}
# 
# # Convert the dictionary to a DataFrame
# test_data = pd.DataFrame(user_input)
# 
# # Add a button to submit the user input
# if st.button("Submit"):
#     st.success(f"The Drug {drug_name} is used for the condition {condition_name}.\nREVIEW : {review}")
#     # Display the user input DataFrame
#     st.success("User Input DataFrame:")
#     st.write(test_data)
#     #PROCESSING THE TEST DATA
#     #CALLING THE preprocess_text FUNCTION
#     test_data['review'] = test_data['review'].apply(preprocess_text)
# 
#     # PREDICTION USING LOGARITHMIC REGRESSION ALGORITHM
#     st.markdown("PREDICTED SENTIMENT USING LOGISTIC REGRESSION ALGORITHM")
#     # Transform the user input using the same TF-IDF vectorizer
#     test_tfidf = tfidf_vectorizer.transform(test_data['review'])
#     # Make predictions on the test data
#     y_pred = logistic_regression.predict(test_tfidf)
#     y_pred = y_pred[0]
#     st.success(f"The predicted sentiment is: {y_pred}")
# 
#     st.markdown("PREDICTED SENTIMENT USING KNN ALGORITHM")
#     # Transform the user input using the same TF-IDF vectorizer
#     test_tfidf = tfidf_vectorizer.transform(test_data['review'])
#     # Make predictions on the test data
#     y_pred_knn = knn_classifier.predict(test_tfidf)
#     y_pred_knn = y_pred_knn[0]
#     st.success(f"The predicted sentiment using KNN is: {y_pred_knn}")
#

!streamlit run /content/app.py &>/content/logs.txt & curl ipv4.icanhazip.com

!npx localtunnel --port 8501

!pip freeze > requirements.txt

!pip install transformers torch pandas scikit-learn matplotlib seaborn

"""LLM model
Fine-tune a pre-trained BERT model with 2000 samples
"""

import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from transformers import pipeline

# Load the CSV file
file_path = '/content/Preprocessed_DataFrame.csv'  # Update with the actual file path
data = pd.read_csv(file_path)

# Sample 2,000 data points
sampled_data = data.sample(n=2000, random_state=42).reset_index(drop=True)

# Preprocess the reviews: convert to lowercase and remove special characters
sampled_data['review'] = sampled_data['review'].str.lower().str.replace('[^a-zA-Z ]', '', regex=True)

# Split the data into training and test sets (80% training, 20% testing)
train_texts, test_texts, train_labels, test_labels = train_test_split(
    sampled_data['review'], sampled_data['Sentiment'], test_size=0.2, random_state=42
)

# Load a pre-trained BERT tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Tokenize the text data
train_encodings = tokenizer(list(train_texts), truncation=True, padding=True, max_length=128)
test_encodings = tokenizer(list(test_texts), truncation=True, padding=True, max_length=128)

# Convert the data into PyTorch datasets
class DrugReviewDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

train_dataset = DrugReviewDataset(train_encodings, train_labels.tolist())
test_dataset = DrugReviewDataset(test_encodings, test_labels.tolist())

# Load a pre-trained BERT model for sequence classification
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)

# Set up training arguments
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
    evaluation_strategy="epoch"
)

# Define a Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset
)

# Train the model
trainer.train()

# Evaluate the model
predictions = trainer.predict(test_dataset)
preds = predictions.predictions.argmax(-1)

# Calculate accuracy
accuracy = accuracy_score(test_labels, preds)
print(f'Accuracy: {accuracy:.2f}')

# Display a classification report
print(classification_report(test_labels, preds, target_names=['Negative', 'Positive']))

# Optionally, use the model for prediction with a pipeline
sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
example_review = "This medication really helped me with my pain!"
result = sentiment_pipeline(example_review)
print(result)