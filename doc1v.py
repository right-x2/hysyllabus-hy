
# -*- coding: utf-8 -*-



from gensim.models.doc2vec import TaggedDocument
from gensim.models import Doc2Vec

import pandas as pd 
import csv






sample_corpus=[]
with open('./doc2v/전공_불용어처리+수업코드+내용_0526_1.csv','r', newline='') as f:
    rdr=csv.reader(f)
    for row in rdr:
        sample_corpus.append(row)
        
f.close()

sample_corpus = sample_corpus[1:]




import pandas as pd
import ast

raw_corpus = pd.read_csv('./doc2v/전공_불용어처리+수업코드+내용_0526_1.csv', encoding = 'UTF8')


raw_corpus.to_csv('./doc2v/전공_불용어처리+수업코드+내용_0526_1.csv', columns = ['1','수업코드','text','교과목명'], index = False)

corpus_col=[]
for row in zip(*sample_corpus):
    corpus_col.append(row)
    #print(row)

class_num = list(corpus_col[1])
class_name = list(corpus_col[3])
class_text = list(corpus_col[2])


title = corpus_col[0]
class_number = corpus_col

title_l = []
for to in title:
    l = ast.literal_eval(to)
    title_l.append(l)
    

    

    



document = tuple(title_l)
            

tagged_data = [TaggedDocument(words=d, tags=[str(i)]) for i,d in enumerate(document)]






max_epochs = 5
vec_size = 20
alpha = 0.025

model = Doc2Vec(vector_size = 100,
                alpha = 0.025, 
                min_alpha=0.00025,
                min_count=1,
                dm =1)

model.build_vocab(tagged_data)

for epoch in range(max_epochs):
    #print('iteration {0}'.format(epoch))
    model.train(tagged_data,
                total_examples=model.corpus_count,
                epochs=model.epochs)

    model.alpha -= 0.0002

    model.min_alpha = model.alpha

model.save("d2v_major.model")
#print("Model Saved")



import csv

mydict = {}

with open('./doc2v/전공_인덱스.csv', mode='r',encoding='utf-8-sig') as inp:
    reader = csv.reader(inp)
    dict_from_csv = {rows[1]:rows[0] for rows in reader}


from gensim.models.doc2vec import Doc2Vec

def major_doc_sim(lec_num):
    
    model= Doc2Vec.load("doc2v/d2v_major.model")

    number = lec_num

    n = dict_from_csv[str(number)]

    a = int(n)

    v1 = model.infer_vector(tagged_data[a][0])

    n_list = []

    vv = model.docvecs.most_similar(positive = [v1], topn=20)

    per_list = []
    cnt = 0
    
    for to in vv :
        pcnt = round(to[1]*100,2)
        inum = int(to[0])
        if pcnt > 20 and cnt < 10 and class_num[a] != class_num[inum] :
            per_list.append(pcnt)
            n_list.append(to[0])
            cnt += 1 

        else:
            pass
        
    print(" ")
    

    cln_list = []
 
    for n in n_list:    
        cln_list.append(int(n))

    ret_list = []
    for n in range(0,len(per_list)):
        temp = [cln_list[int(n)],per_list[int(n)]]
        ret_list.append(temp)
        print(cln_list[int(n)],per_list[int(n)])
    return ret_list
        





