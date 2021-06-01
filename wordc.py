from collections import Counter
from os import symlink
from collections import Counter
import numpy as np
from PIL import Image
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd



wordcloud = pd.read_csv('./csv/wordcloud.csv')
wordc_list = wordcloud.values.tolist()


major = pd.read_csv('/Users/kimjungwoo/Downloads/major.csv')
kyo = pd.read_csv('/Users/kimjungwoo/Downloads/kyo1.csv')

major = major.values.tolist()
kyo = kyo.values.tolist()

major.extend(kyo)

str_list = []

oslist = "[운영체제, 원리, 개념, 이해, 운영체제, 제공, 서비스, 이해, 운영체제, 설계, 구현, 이슈]"

wordc_list.append([22695,oslist])

def get_cloud(subjectcode):
 #   index = 0
    str_list = ""
    for item in wordc_list:
        if(subjectcode==int(item[0])):
            if(len(item[1])==2):
                return 0
            str = item[1][1:-1]
            str_list = str.split(',')
            break
    
    if(str_list==""):
        return 0
    
    for i in range(len(str_list)):
        str_list[i] = str_list[i].strip(' ')
        


    cnt =  Counter(str_list)

    TopWords= 10
    TotalWordsCount=sum(cnt.values())
    WordsCount=len(Counter(str_list))
                
    print(WordsCount,"개의 단어가")
    print(TotalWordsCount,"번 나온다")
    print("상위",TopWords,"개 단어 ")

    words = cnt.most_common(TopWords)
    word_list  = []
    for i in words:
        temp = [i[0].strip(' '),i[1]]
        word_list.append(temp)
    
    '''
    img_path="./cloud.png"
    cloud_mask = np.array(Image.open(img_path))
    wordcloud = WordCloud(
        font_path = "./Arial Unicode.ttf",
        width = 1000, height = 1000, background_color = "white" , mask=cloud_mask
    )
    
    cloud = wordcloud.generate_from_frequencies(cnt)
    cloud.to_file(f'./static/img/cloud{subjectcode}.png')
    '''
    
    return word_list

    
