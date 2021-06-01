import pandas as pd
import numpy as np
import konlpy
from sklearn.feature_extraction.text import CountVectorizer   # tf-idf 방식을 사용하려면 대신 TfidfVectorizer를 import
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

review = pd.read_csv('/Users/kimjungwoo/Downloads/lecture_review.csv')
review_list = review.values.tolist()
print(len(review_list))
print(review_list[4061])

#훈련셋과 테스트셋을 나눈다

from sklearn.model_selection import train_test_split

data = review['수강후기']

target = review['평점']
print(data)

for i in range(len(target)):
    if(target[i]>3):
        target[i] = 1
    else:
        target[i] = 0
print(target)

x_train, x_test, y_train, y_test = train_test_split(data, target, test_size=0.2, shuffle=True, stratify=target, random_state=13)

tf_vectorizer = CountVectorizer(min_df=1, ngram_range=(1,1))
X_train_tf = tf_vectorizer.fit_transform(x_train)  # training data에 맞게 fit & training data를 transform
X_test_tf = tf_vectorizer.transform(x_test) # test data를 transform



vocablist = [word for word, number in sorted(tf_vectorizer.vocabulary_.items(), key=lambda x:x[1])]  # 단어들을 번호 기준 내림차순으로 저장


## 확인해보기
print(X_train_tf[:1], '\n')
print(X_test_tf[:1], '\n')
print(vocablist[:10])

model = LogisticRegression(C=0.1, penalty='l2', random_state=13)
model.fit(X_train_tf, y_train)  # 학습


LogisticRegression(C=0.1, class_weight=None, dual=False, fit_intercept=True,
                   intercept_scaling=1, l1_ratio=None, max_iter=100,
                   multi_class='auto', n_jobs=None, penalty='l2',
                   random_state=0, solver='lbfgs', tol=0.0001, verbose=0,
                   warm_start=False)


y_test_pred = model.predict(X_test_tf)

print('Misclassified samples: {} out of {}'.format((y_test_pred != y_test).sum(), len(y_test)))
print('Accuracy: {:.2f}'.format(accuracy_score(y_test, y_test_pred)))  # model.score(X_test_tf, y_test)로 계산해도 됨


coefficients = model.coef_.tolist()

sorted_coefficients = sorted(enumerate(coefficients[0]), key=lambda x:x[1], reverse=True)
# coefficients(계수)가 큰 값부터 내림차순으로 정렬

print('긍정적인 단어 Top 10 (높은 평점과 상관관계가 강한 단어들)')
for word_num, coef in sorted_coefficients[:100]:
  print('{0:}({1:.3f})'.format(vocablist[word_num], coef))

print('\n부정적인 단어 Top 10 (낮은 평점과 상관관계가 강한 단어들)')
for word_num, coef in sorted_coefficients[-100:]: 
  print('{0:}({1:.3f})'.format(vocablist[word_num], coef))
  
ret_list = []
for word_num, coef in sorted_coefficients:
    rate = '{0:.3f}'.format(coef)
    temp = [vocablist[word_num],rate]
    ret_list.append(ret_list)


df1 = pd.DataFrame(data = np.array(ret_list),columns=["단어","상관관계"])
df1.to_csv("/Users/kimjungwoo/Downloads/word_dict.csv")
  
  