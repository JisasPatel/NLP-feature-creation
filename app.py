#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 20 22:45:03 2023

@author: jisaspatel
"""

import requests
import pandas as pd
import os
from bs4 import BeautifulSoup
import re
import string
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize, sent_tokenize 
import textstat



def from_txt(path, encoding='utf-8'):
  l = []
  with open(path,'r',encoding=encoding) as file:
    for line in file:
      row_data = line.strip()
      l.append(row_data)
  return l

def get_stop_word(path, encoding='utf-8'):
    
  words = from_txt(path,encoding)
  p1 = r'^\s*([^\s|]+)'
  cleaned_words = [re.match(p1, word).group(1) if re.match(p1, word) else word for word in words]

  return cleaned_words






pos_file = "pos-neg/positive-words.txt"
pos_words = []

neg_file = "pos-neg/negative-words.txt"
neg_words = []

pos_words = from_txt(pos_file,'latin-1')
neg_words = from_txt(neg_file,'latin-1')


auditor    = "stopword/StopWords_Auditor.txt"
currencies = "stopword/StopWords_Currencies.txt"
dates      = "stopword/StopWords_DatesandNumbers.txt"
generic    = "stopword/StopWords_Generic.txt"
genericLong = "stopword/StopWords_GenericLong.txt"
geographic = "stopword/StopWords_Geographic.txt"
names      = "stopword/StopWords_Names.txt"


auditor_list      = get_stop_word(auditor,'latin-1')
currencies_list   = get_stop_word(currencies,'latin-1')
dates_list        = get_stop_word(dates,'latin-1')
generic_list      = get_stop_word(generic,'latin-1') 
genericLong_list  = get_stop_word(genericLong,'latin-1')
geographic_list   = get_stop_word(geographic,'latin-1')
names_list        = get_stop_word(names,'latin-1')

stop_data = {
    'auditor_list' : auditor_list,
    'currencies_list' : currencies_list,
    'dates_list' : dates_list,
    'generic_list' : generic_list,
    'geographic_list' : geographic_list,
    'names_list' : names_list
}

stop_words = auditor_list + currencies_list + dates_list + generic_list + geographic_list + names_list

"""--------------------------------------------------------------------------------------"""


def remove_stop_word(text):
  if(text == "NAN"):
    return "NAN"
  pattern = r'\b(?:' + '|'.join(stop_words) + r')\b'

  return re.sub(pattern, '', text, flags=re.IGNORECASE)


def remove_punctuations(text):
    if(text == "NAN"):
        return "NAN"
    pancs = string.punctuation
    return text.translate(str.maketrans('','',pancs))

def word_char_cout(text):
  if(text == "NAN"):
    return 0
  words = word_tokenize(text)
  return len(words)

def avg_word_length(text):
  if(text == "NAN"):
    return 0
  words = word_tokenize(text)
  chars = sum(len (word) for word in words)
  if len(words) > 0:
    return chars/len(words)
  else:
    return 0

def pos_neg_score(text):
  if(text == "NAN"):
    return 0,0
  pos_score = 0
  neg_score = 0
  text = text.lower()
  words = word_tokenize(text)
  for i in words:
    if i in pos_words:
      pos_score += 1
    if i in neg_words:
      neg_score += 1
  return pos_score, neg_score


def polarity_subjectivity(df):
  pos = df['Positive_Score']
  neg = df['Negative_score']
  words = df['Word_count']

  
  polarity = ( pos - neg ) / (( pos + neg) + (0.000001))
  subjectivity = (pos + neg ) / (( words ) + 0.000001)

  return polarity, subjectivity


def avg_len_sentence(text):
  if (text == "NAN"):
    return 0
  sent = sent_tokenize(text)
  number = len(sent)
  total_sum = sum(len(i) for i in sent)
  return total_sum/number
   

def avg_no_words(text):
    if (text == "NAN"):
      return 0
    sent = sent_tokenize(text)
    number = len(sent)
    temp = map(remove_punctuations,sent)
    sent_cleaned = list(temp)
    total_words = sum(len(word_tokenize(i)) for i in sent_cleaned)
    return total_words/number

def calculate_syllable_and_complex_counts(text):
    if (text == "NAN"):
      return 0,0
    syllable_count_per_word = textstat.syllable_count(text) / len(word_tokenize(text))
    complex_word_count = sum(1 for word in word_tokenize(text) if textstat.syllable_count(word) > 2)
    return syllable_count_per_word, complex_word_count

def percentage_complex_words_and_Fog_index(df):
  complex_word_count = df['complex_word_count']
  word_count = df['Word_count']
  avg_sent_length = df['Avg_Sentence_Length']
  percentage = complex_word_count / word_count
  fog_idx = 0.4 * (avg_sent_length + percentage)
  return percentage, fog_idx

def Personal_Pronouns_count(text):
    if(text == "NAN"):
      return 0
    p3 = r'\b(?:I|we|We|ours|Ours|our|Our|my|My|us)\b'
    matches = re.findall(p3, text)
    return len(matches)

def save_article(Final_DF):
    path = "scrapped_text_files"
    os.makedirs(path, exist_ok=True)

    for index, row in Final_DF.iterrows():
        url_id = row['URL_ID']
        article_text = row['Article']

        # Create the filename using the URL ID
        filename = f'{url_id}.txt'

        # Create the full path for saving
        file_path = os.path.join(path, filename)

        # Save the article text to the text file
        with open(file_path, 'w') as file:
            file.write(article_text)


def from_Df(df):
    Final = {'URL_ID':[],'URL':[],'Title':[],'Article':[]}
    for index, row in df.iterrows():
        url_id = row['URL_ID']
        url = row['URL']
        web = requests.get(url).text
        soup = BeautifulSoup(web,'lxml')
        title_element = soup.find('h1',class_='entry-title') 
        article_element = soup.find('div', class_='td-post-content')
        
        if title_element is not None:
            title = title_element.text
        else:
            title = 'NAN'

        if article_element is not None:
            article = article_element.text.replace('\n','')
        else:
            article = 'NAN'

        Final['URL_ID'].append(url_id)
        Final['URL'].append(url)
        Final['Title'].append(title)
        Final['Article'].append(article)
        
        Final_DF = pd.DataFrame(Final)
    
    final_copy = Final_DF.copy()
    save_article(Final_DF)
    print("-")
    
    final_copy['Article'] = final_copy['Article'].apply(remove_stop_word)
    
    final_copy['After_Punctuation_Article'] = final_copy['Article'].apply(remove_punctuations)
    
    final_copy['Word_count'] = final_copy['After_Punctuation_Article'].apply(word_char_cout)
    
    final_copy['Avg_word_length'] = final_copy['After_Punctuation_Article'].apply(avg_word_length)
    
    final_copy[['Positive_Score','Negative_score']] = final_copy['After_Punctuation_Article'].apply(pos_neg_score).apply(pd.Series)
    
    final_copy['Polarity_Score'],final_copy['Subjectivity_Score'] = polarity_subjectivity(final_copy)
    
    final_copy['Avg_Sentence_Length'] = final_copy['Article'].apply(avg_len_sentence)
    
    final_copy['Avg_No._Words/Sentence'] = final_copy['Article'].apply(avg_no_words)
    
    final_copy[['syllable_count_per_word','complex_word_count']] = final_copy['After_Punctuation_Article'].apply(calculate_syllable_and_complex_counts).apply(pd.Series)
    
    final_copy['Percentage_Of_Complex_word'],final_copy['Fog_index'] = polarity_subjectivity(final_copy)
    
    final_copy['Personal_Pronouns'] = final_copy['After_Punctuation_Article'].apply(Personal_Pronouns_count)
    
    columns = ['URL_ID', 'URL', 'Title', 'Article','Positive_Score','Negative_score', 'Polarity_Score', 'Subjectivity_Score', 'Avg_Sentence_Length','Percentage_Of_Complex_word', 'Fog_index', 'Avg_No._Words/Sentence', 'complex_word_count','Word_count', 'syllable_count_per_word', 'Personal_Pronouns', 'Avg_word_length'] 
    final_copy = final_copy[columns]
    final_copy = final_copy.rename(columns = {'complex_word_count':'Complex_word_count', 'syllable_count_per_word' : 'Syllable_count_per_word',  })
    
    return final_copy
    


def from_path(path):
    inputXL = path
    df = pd.read_excel(inputXL)
    print("-")
    final = from_Df(df)
    return final
        
        



if __name__ == "__main__":
    print(from_path('Input.xlsx'))
















