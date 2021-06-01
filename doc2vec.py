#!/usr/bin/env python
# coding: utf-8

# In[9]:


import pandas as pd

raw_corpus = pd.read_csv('전공_d2v_0524.csv', encoding = 'UTF8')

# raw 데이터 정보 확인
print(raw_corpus.info())
print(raw_corpus.shape)

raw_corpus.to_csv('전공_d2v_0524.csv', columns = ['text'], index = False)


# In[10]:


print(raw_corpus)


# In[11]:


import csv

sample_corpus=[]
with open("전공_d2v_0524.csv",'r', newline='') as f:
    rdr=csv.reader(f)
    for row in rdr:
        sample_corpus.append(row)
f.close()

sample_corpus = sample_corpus[1:]
print(sample_corpus)
corpus_col=[]
for row in zip(*sample_corpus):
    corpus_col.append(row)

title = corpus_col[0]
#print(title[0:10])


# In[6]:


pip install konlpy


# In[12]:


pip install mecab-python3


# In[13]:


from konlpy.tag import Mecab

m = Mecab()


# In[14]:



title_h=[]
for to in title:
    title_h.append(m.nouns(to))
    print(title_h[-1])
    
print('end')


# In[18]:


title_1 = []
title_1 = title_1 + title_h
for txt in title_1:
    for i in txt:
        if len(i) < 2:
            txt.remove(i)
    #print(txt)
print(title_1)


# In[19]:


stopwords = ['수업','과목','전공','학습','기본','언제','코로나','성적','전공','감염병','상황','관리','온라인','강의','시청','수행','과제물','수업','원격','유형','평가','진도','제출','퀴즈','출결','반영','다음','관련','안내','출석',
'병결','증빙','사유','경우','포함','지각','처리','감점','자세','학습','참여','녹화',
'형태','기말고사','시험','학기','슬리퍼','샌들','휴대폰','사용',
'금지','결석','마음','오리엔테이션','총점','미제출','중간','목표','대학원생','교과목','학년','공백']

title_ = [] 

for l in title_1:
    for words in l:
        if words in stopwords:
            l.remove(words)
    title_.append(l)

print(title_)


# In[32]:


'''column = ['1','2']


df = pd.DataFrame({'1':title_h,'2':title_})
df.index = df.index

df.to_csv(f'전공_d2v_0524.csv', mode = 'w', encoding='utf-8-sig', header= True,index=True)
print(df)'''


# In[20]:


import nltk


# In[21]:


import re
list_par = []
# 텍스트를 가지고 있는 리스트
for i in title:
    # 영어,숫자 및 공백 제거.
    text = re.sub('[^a-zA-Z0-9]',' ',i).strip()

    list_par.append(text)


# In[22]:



all_nouns = []
for i in list_par:
    all_ = []
    for word in nltk.tag.pos_tag(nltk.tokenize.word_tokenize(i)): #명사
        if word[1] in ['NN', 'NNS', 'NNP', 'NNPS']:
            #print(word[0])
            all_.append(word[0])
            #print(all_)
    #print(all_)
    all_nouns.append(all_)
            
print(all_nouns)


# In[24]:


all_ = []
a = []
for i in range(0,201):
    a = title_[i] + all_nouns[i]
    all_.append(a)
print(all_)


# In[25]:


column = ['text']


df = pd.DataFrame({'text':all_})
df.index = df.index

df.to_csv(f'교양전처리_영어포함_0525.csv', mode = 'w', encoding='utf-8-sig', header= True,index=True)
print(df)


# In[ ]:




