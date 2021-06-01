from flask import Flask, render_template, request, url_for,session,redirect,escape
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import os
import config
import csv
import pandas as pd
import numpy as np
import math
import os
import sqlite3
from wordc import get_cloud
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import PasswordField
from wtforms.validators import DataRequired, EqualTo
import math
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from flask import flash

basedir = os.path.abspath(os.path.dirname(__file__))
dbfile = os.path.join(basedir, 'db.sqlite')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class LoginForm(FlaskForm):
    class UserPassword(object):
        def __init__(self, message=None):
            self.message = message
            
        def __call__(self, form, field):
            userid = form['userid'].data
            password = field.data
            
            usertable = User.query.filter_by(userid=userid).first()
            if usertable.password != password:
            	raise ValueError('비밀번호 틀림')
                
    userid = StringField('userid', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired(), UserPassword()])
    
class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(80),unique=True)
    user_id = db.Column(db.String(80))
    password = db.Column(db.String(80))
    grade_point = db.Column(db.Integer)
    major_point = db.Column(db.Integer)
    major_main_point = db.Column(db.Integer)
    elec_point = db.Column(db.Integer)
    vol_point = db.Column(db.Integer)
    coop_point = db.Column(db.Integer)
    pbl_point =  db.Column(db.Integer)
    def __init__(self, username,password):
        self.username=username
        self.password =password
    
class Lecture(db.Model):
    __tablename__ = 'lecture'
    
    id = db.Column(db.Integer,primary_key=True)
    lecture_code = db.Column(db.Integer,unique=True)
    userid = db.Column(db.String(80),unique=True)
    strat_time = db.Column(db.Integer,unique=True)
    end_time = db.Column(db.Integer,unique=True)
    day = db.Column(db.String(80),unique=True)
    def __init__(self,lecture_code,userid,strat_time,end_time,day):
        self.lecture_code=lecture_code
        self.userid=userid 
        self.strat_time=strat_time
        self.end_time=end_time
        self.day=day



db.create_all()


tfidf_vectorizer = TfidfVectorizer()
star_list = pd.read_csv('./csv/lecture_star.csv')
review_list = pd.read_csv('./csv/lecture_review.csv')
my_table = []
with open('./dict/my_dict.pickle', 'rb') as fr:
    my_dict = pickle.load(fr)
    
with open('./dict/doc2_dict.pickle', 'rb') as fr:
    doc2_dict = pickle.load(fr)

grade_name_list = ["출석","퀴즈","과제","중간고사","토론","기말고사","팀프로젝트","학습참여","기타","기타평가항목"]

major = pd.read_csv('./csv/major.csv')
kyo = pd.read_csv('./csv/kyo1.csv')


major = major.values.tolist()
kyo = kyo.values.tolist()
star_list = star_list.values.tolist()
review_list = review_list.values.tolist()

major_len = len(major)
cnt  = len(major)
for i in range(len(kyo)):
    kyo[i][0] = cnt + i
    major.append(kyo[i])

all_list = []

for lec in major:
    if(isinstance(lec[15], float)):
        lec[15]="비지정"
    
    if(isinstance(lec[17], float)):
        lec[17]="비지정"
    
    temp = [lec[0],lec[5],lec[4],lec[17],lec[6],lec[15],lec[6],float(lec[10])]
    all_list.append(temp)





@app.route("/")
def get_index():
    print("------aaa------")
    lecNum = -1
    select_list = []
    if 'user' in session:
        user_id = '%s' % escape(session['user'])
        conn = sqlite3.connect ('db.sqlite')
        c = conn.cursor()
        c.execute(f"SELECT * FROM Lecture where userid = '{user_id}';")
        for row in c.fetchall():
            select_list.append(row[1])
        print(select_list)
    my_list = []
    ret = []
    slen = 0
    lec_name = request.args.get('lecName')
    lec_unit = request.args.get('lecUnit')
    search_type = request.args.get('searchType')
    day_unit = request.args.get('dayUnit')
    my_page = request.args.get('my_page')

    
    if(my_page is None):
        slen = 0
    else:
        my_page = int(my_page)
        slen = (my_page-1)*10
    
    
    if lec_name is None:
        print("dfafasdf")
        for item in all_list:
            if(lec_unit is None):
                my_list.append(item)
            elif(lec_unit==item[4]):
                my_list.append(item)
    else:
        print("dksldi")
        for item in all_list:
            print(item[1])
            if(day_unit is None and lec_unit is None and search_type=="강의명" and lec_name in item[1]):
                
                my_list.append(item)     
            elif(search_type=="강의명" and isinstance(item[1], str)and lec_name in item[1] and day_unit in item[5] and lec_unit in item[4]):
                my_list.append(item)   
            elif(search_type=="교수명" and isinstance(item[3], str)and lec_name in item[3] and day_unit in item[5] and lec_unit in item[4]):
                my_list.append(item)
             
                
    for i in range(10):
        if(slen+i>=len(my_list)):
            break
        ret.append(my_list[slen+i])
    lecName ="선택없음"
    if 'lecNum' in session:
        lecNum = '%s' % escape(session['lecNum'])
        lecNum = int(lecNum)
        #print(lecNum)
        lecName = all_list[lecNum][1]
        #print(lecName)
    print("-----")
    return render_template("index.html",list=ret,lecName = lecName,my_page=my_page,select_list = select_list,lecNum = lecNum,)

@app.route("/search",methods = ['POST','GET'])
def get_search():
    lecName = request.args["search_name"]
    lecUnit = request.args["lec_unit"]
    searchType = request.args["search_type"]
    dayUnit = request.args["day_unit"] 
    print("dfsafa")
    if(dayUnit=="전체"):
        dayUnit = ""
    if(lecUnit=="전체"):
        lecUnit = ""   

    print(lecName+lecUnit+searchType+dayUnit)
    return redirect(url_for('get_index',lecName=lecName,lecUnit=lecUnit,searchType=searchType,dayUnit=dayUnit))

@app.route("/select/",methods = ['POST','GET'])
def set_lecture():
    lecNum = request.args["lecNum"]
    session['lecNum'] = lecNum
    return redirect("/")

@app.route("/add_lecture/",methods = ['POST','GET'])
def add_lecture():
    if 'user' not in session:
        return redirect('/login')
    else:
        lecNum = int(request.args["lecNum"])
        lecture = all_list[lecNum]
        user_id = '%s' % escape(session['user'])
        print(lecture[5])
        conn = sqlite3.connect ('db.sqlite')
        c = conn.cursor()
        if(lecture[5]=="비지정"):
            object = Lecture(lecture_code=request.args["lecNum"],userid=user_id,strat_time=-1,end_time=-1,day="비지정")
            db.session.add(object) 
        else:
            lec_time = lecture[5]
            time_list = lec_time.split(',')
            
            c.execute(f"SELECT * FROM Lecture where userid = '{user_id}';")
            lec_list = []
            for row in c.fetchall():
                lec_list.append([row[3],row[4],row[5]])
            flag = 0
            for time in time_list:
                day = time[0]
                time = time[2:]
                time = time[:time.find(' ')]
                temp_list = time.split('-')
                first_time = temp_list[0].split(':')
                start_time = int(first_time[0]+first_time[1])
                second_time = temp_list[1].split(':')
                end_time = int(second_time[0]+second_time[1])
                for item in lec_list:
                    print(start_time,item[0], end_time,item[1])
                    if(day!=item[2]):
                        continue
                    if(start_time<=item[0] and end_time>=item[0]):
                        flash("시간이 겹치는 강의가 있습니다.")
                        return redirect('/')
                    if(start_time>=item[0] and start_time<item[0]):
                        flash("시간이 겹치는 강의가 있습니다.")
                        return redirect('/')
            object = Lecture(lecture_code=request.args["lecNum"],userid=user_id,strat_time=start_time,end_time=end_time,day=day)
            db.session.add(object)
            conn.commit()
        
        if("전공핵심" in lecture[4]):
            c.execute(f"UPDATE user SET grade_point= grade_point+{int(lecture[7])} WHERE user_id = '{user_id}';")
            c.execute(f"UPDATE user SET major_point= major_point+{int(lecture[7])} WHERE user_id = '{user_id}';")
            c.execute(f"UPDATE user SET major_main_point = major_main_point+{int(lecture[7])} WHERE user_id = '{user_id}';")
            conn.commit()
        elif("전공심화" in lecture[4]):
            c.execute(f"UPDATE user SET grade_point= grade_point+{int(lecture[7])} WHERE user_id = '{user_id}';")
            c.execute(f"UPDATE user SET major_point= major_point+{int(lecture[7])} WHERE user_id = '{user_id}';")
            conn.commit()
        elif("전공기초" in lecture[4]):
            c.execute(f"UPDATE user SET grade_point= grade_point+{int(lecture[7])} WHERE user_id = '{user_id}';")
            c.execute(f"UPDATE user SET major_point= major_point+{int(lecture[7])} WHERE user_id = '{user_id}';")
            conn.commit()
        elif("교양필수" in lecture[4]):
            c.execute(f"UPDATE user SET grade_point= grade_point+{int(lecture[7])} WHERE user_id = '{user_id}';")
            conn.commit()
        elif("교양선택" in lecture[4]):
            c.execute(f"UPDATE user SET grade_point= grade_point+{int(lecture[7])} WHERE user_id = '{user_id}';")
            c.execute(f"UPDATE user SET elec_point= elec_point+{int(lecture[7])} WHERE user_id = '{user_id}';") 
            conn.commit()
        
        
        if('사회봉사' in lecture[1]):
            c.execute(f"UPDATE user SET vol_point= 1 WHERE user_id = '{user_id}';") 
            conn.commit()
            
 

        return redirect("/")

@app.route("/submit_login",methods=['POST','GET'])
def submit_login():
    if request.method == 'GET': 
        return render_template('login.html') 
    else: 
        id = request.form['user_id'] 
        pw = request.form['password']
        print(pw)
        print(id)
        conn = sqlite3.connect ('db.sqlite')
        co = conn.cursor()
        co.execute(f"SELECT * FROM User where user_id='{id}' and password='{pw}';")
        cnt = 0;
        for row in co.fetchall():
            cnt = cnt + 1
        print(cnt)
        if cnt>0:
            session['user'] = id 
            return redirect('/mypage')
        else:
            flash("아이디 또는 비밀번호가 일치하지 않습니다.")
            return redirect('/login')

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user', None)
    return redirect('/')
    
@app.route("/timetable")
def get_timetable():
    
    lecNum = '%s' % escape(session['lecNum'])
    lecNum = int(lecNum)
    str = all_list[lecNum][5]
    lec_name = all_list[lecNum][1]
    unit = all_list[lecNum][6]
    start_list = []
    end_list = []
    day_list = []
    lec_list = str.split(",")
    len_list = []
    bg_list = []
    print(all_list[lecNum])
    for item in lec_list:
        print(item)
        day_list.append(item[0])
        item = item[2:]
        item = item[:item.find(" ")]
        print(item)
        time_list = item.split("-")
        stime = time_list[0].split(":")
        etime = time_list[1].split(":")
        stime = stime[0]+stime[1]
        etime = etime[0]+etime[1]
        
    
        sum = int(etime) - int(stime)
        if(sum==30 or sum==70):
            len_list.append("half")
        elif(sum==100):
            len_list.append("one_hour")
        elif(sum==130 or sum==170):
            len_list.append("one_half")
        elif(sum==200):
            len_list.append("two_hour")
        
        start_list.append("b"+stime)
        end_list.append(etime)
        bg_list.append(bgcol)
    print(day_list)
    print(start_list)
    print(end_list)
    return render_template("timetable.html",day_list=day_list,start_list=start_list,end_list=end_list,list_len = len(day_list),len_list = len_list,lec_name = lec_name,bg_list=bg_list)

@app.route("/mypage")
def get_mypage():
    list = []
    if 'user' not in session:
        return redirect('/login')
    else:
        user_id = '%s' % escape(session['user'])
        conn = sqlite3.connect ('db.sqlite')
        c = conn.cursor()
        c.execute(f"SELECT * FROM User where user_id = '{user_id}';")
        for row in c.fetchall():
            username = row[1]
            grade_point = row[4]
            major_point = row[5]
            major_main_point = row[6]
            elec_point = row[7]
            vol_point = row[8]
            coop_point = row[9]
            pbl_point = row[10]
            print(row)
        return render_template("mypage.html",username = username,grade_point=grade_point,grade_rate = int(100*(grade_point/140)),major_point=major_point,major_rate = int(100*(major_point/45)),major_main_point=major_main_point,major_main_rate = int(100*(major_main_point/35)),elec_point=elec_point,elec_rate = int(100*(elec_point/6)),vol_point=vol_point,coop_point=coop_point,coop_rate = int(100*(coop_point/6)),pbl_point=pbl_point,pbl_rate = int(100*(pbl_point/3)))

@app.route("/mytable")
def get_mytable():
    if 'user' not in session:
        return redirect('/login')
    else:
        user_id = '%s' % escape(session['user'])
        lec_table = []
        all_lec = []
        conn = sqlite3.connect ('db.sqlite')
        c = conn.cursor()
        c.execute(f"SELECT * FROM Lecture where userid = '{user_id}';")
        for row in c.fetchall():
            print("---")
            lec_table.append(all_list[row[1]])
        lec_list = []
        ret = []
        print(lec_table)
        for item in lec_table:
            str = item[5]
            lec_name = item[1]
            lec_num = item[2]
            unit = item[4]
            if(str=="비지정"):
                continue
            print(item)
            start_list = []
            end_list = []
            day_list = []
            print(str)
            lec_list = str.split(",")
            len_list = []
            for my_item in lec_list:
                
                lec_day = my_item[0]
                my_item = my_item[2:]
                print("------")
                print(my_item)
                my_item = my_item[:my_item.find(" ")]
                time_list = my_item.split("-")
                stime = time_list[0].split(":")
                etime = time_list[1].split(":")
                stime = stime[0]+stime[1]
                etime = etime[0]+etime[1]
                
                if("전공핵심" in unit):
                    bgcol = "red"
                elif("전공심화" in unit):
                    bgcol = "blue"
                elif("전공기초" in unit):
                    bgcol = "yellow"
                elif("교양필수" in unit):
                    bgcol = "orange"
                elif("교양선택" in unit):
                    bgcol = "purple"   
                
                sum = int(etime) - int(stime)
                if(sum==30 or sum==70):
                    lec_size="half"
                elif(sum==100):
                    lec_size="one_hour"
                elif(sum==130 or sum==170):
                    lec_size="one_half"
                elif(sum==200):
                    lec_size="two_hour"
                    
                start_list.append("b"+stime)
                end_list.append(etime)
                lec_temp = [lec_day,lec_num,"b"+stime,etime,lec_size,lec_name,bgcol]
                ret.append(lec_temp)
        print(ret)
        return render_template("mytable.html",lec_list = ret,lec_table=lec_table)



@app.route("/review")
def get_keyword():

    print("-----")
    if 'lecNum' in session:
        lecNum = '%s' % escape(session['lecNum'])
        print(lecNum)
        lecName = all_list[int(lecNum)][1]
        lecNum = int(lecNum)
        lecture = major[lecNum]
        print(lecture)
        grade_name=[]
        grade_rate=[]
        lec_count = lecture[10]
        unit = lecture[6]
        lec_code = lecture[3]
        lec_major = lecture[14]
        lec_type = lecture[21]
        pre_lec = lecture[40]
        lec_name = lecture[5]
        prof_name = lecture[17]
        lec_aim = lecture[34]
        
        ret_list = []
        word_list = []
        review_rate = []
        all_review_list = [0,0,0,0,0,0]
        lec_star_rate = 0
        for item in star_list:
            if(item[1]==lecture[0]):
                lec_star_rate = item[5]
        content_list = []
        act_list = []
        for i in range(1,5):
            content_list.append(lecture[40+i])
        for i in range(1,5):
            act_list.append(lecture[44+i])
        for i in range(2,11):
            if(int(lecture[-i])>0):
                print(grade_name_list[-i])
                grade_name.append(grade_name_list[-i])
                grade_rate.append(int(lecture[-i]))
                
        for review in review_list:        
            if(review[1]==lec_name and review[2]==prof_name):
                ret_list.append(review[4])
                review_rate.append(review[5])
                all_review_list[int(review[5])] = all_review_list[int(review[5])]+1

        if(len(ret_list)>0):
            
            tfidf_vectorizer.fit(ret_list)
            a = tfidf_vectorizer.vocabulary_# 벡터라이저가 학습한 단어사전을 출력합니다
            
            for i in a:
                #print(i)
                if i in my_dict:
                    temp = [float(my_dict[i]),i]
                    word_list.append(temp)
            word_list.sort()
            #print(word_list)
            pos_list = []
            neg_list = []
            for i in range(10):
                if(len(word_list)<=i or word_list[i][0]>0.000):
                    break
                neg_list.append(word_list[i])
            for i in range(1,11):
                if(len(word_list)<i or word_list[-i][0]<=0.000):
                    break
                pos_list.append(word_list[-i])
            
            print(all_review_list)
            return render_template("review.html",grade_name=grade_name,grade_rate=grade_rate,grade_len = len(grade_name),lec_count = int(lec_count),
                    unit = unit, lec_code = lec_code,lec_major = lec_major, lec_type = lec_type,lec_star_rate = lec_star_rate,
                    content_list = content_list,act_list = act_list,
                    pre_lec = pre_lec, ret_list = ret_list,neg_list = neg_list,pos_list=pos_list,pos_len = len(pos_list),neg_len = len(neg_list),lec_aim = lec_aim,review_rate=review_rate,review_len=len(review_rate),lecName = lecName,all_review_list=all_review_list)
        else:
            print("----------------")
            print("sdafasfdsa")
            return render_template("review.html",lec_star_rate = 0,lec_name = lec_name)
    else:
        return redirect('/')

@app.route("/lecture")
def get_lecture():
    
    select_list = []
    if 'user' in session:
        user_id = '%s' % escape(session['user'])
        conn = sqlite3.connect ('db.sqlite')
        c = conn.cursor()
        c.execute(f"SELECT * FROM Lecture where userid = '{user_id}';")
        for row in c.fetchall():
            select_list.append(row[1])
        print(select_list)
    if 'lecNum' in session:
        rate_list = []
        name_list = []
        
        lecNum = '%s' % escape(session['lecNum'])
        lecNum = int(lecNum)
        lecture = major[lecNum]
        lecName = lecture[5]
        lec_num = int(lecture[4])
        doc_list = doc2_dict[lec_num]
        print(lec_num)
        ret_list = []
        for i in doc_list:
            print(i)
        
       
        for i in doc_list:
            for item in all_list:
                if(int(i[0])==item[2]):
                    ret_list.append([item,i[1]])
                    break
                    
        
        for item in ret_list:
            print(item)
        #print(ret_list)
        
        return render_template("lecture.html",ret_list = ret_list,select_list=select_list,lecName=lecName)
    else:
        return redirect(url_for('get_index'))

@app.route("/info")
def get_info():
    
    if 'lecNum' in session:
        lecNum = '%s' % escape(session['lecNum'])
        print(lecNum)
        lecNum = int(lecNum)
        lecture = major[lecNum]
        lecName = lecture[5]
        print(lecture)
        grade_name=[]
        grade_rate=[]
        lec_count = lecture[10]
        unit = lecture[6]
        lec_code = lecture[3]
        lec_major = lecture[14]
        lec_type = lecture[21]
        pre_lec = lecture[40]
        lec_name = lecture[5]
        prof_name = lecture[17]
        lec_aim = lecture[34]
        
        img_name = f"cloud{lecture[4]}.png"
        my_word_list = get_cloud(lecture[4])
        ret_list = []
        word_list = []
        review_rate = []
        
        lec_star_rate = star_list[lecture[0]][4]
        content_list = []
        act_list = []
   
                
        for review in review_list:        
            if(review[1]==lec_name and review[2]==prof_name):
                ret_list.append(review[4])
                review_rate.append(review[5])

  
        if(len(ret_list)>0):
            tfidf_vectorizer.fit(ret_list)
            a = tfidf_vectorizer.vocabulary_# 벡터라이저가 학습한 단어사전을 출력합니다
            
            for i in a:
                #print(i)
                if i in my_dict:
                    temp = [float(my_dict[i]),i]
                    word_list.append(temp)
            word_list.sort()
            #print(word_list)
            pos_list = []
            neg_list = []
            for i in range(10):
                if(len(word_list)<=i or word_list[i][0]>0.000):
                    break
                neg_list.append(word_list[i])
            for i in range(1,11):
                if(len(word_list)<i or word_list[-i][0]<=0.000):
                    break
                pos_list.append(word_list[-i])
            
                
            return render_template("info.html",grade_name=grade_name,grade_rate=grade_rate,grade_len = len(grade_name),lec_count = int(lec_count),
                    unit = unit, lec_code = lec_code,lec_major = lec_major, lec_type = lec_type,lec_star_rate = lec_star_rate,
                    content_list = content_list,act_list = act_list,
                    pre_lec = pre_lec, ret_list = ret_list,neg_list = neg_list,pos_list=pos_list,pos_len = len(pos_list),neg_len = len(neg_list),lec_aim = lec_aim,review_rate=review_rate,review_len=len(review_rate),img_name=img_name,my_word_list=my_word_list,list_len = len(my_word_list),lecName=lecName)
        else:
            return render_template("info.html",grade_name=grade_name,grade_rate=grade_rate,grade_len = len(grade_name),lec_count = int(lec_count),
                    unit = unit, lec_code = lec_code,lec_major = lec_major, lec_type = lec_type,lec_star_rate = lec_star_rate,
                    content_list = content_list,act_list = act_list,
                    pre_lec = pre_lec,neg_list = "non",pos_list="non",lec_aim = lec_aim,list_len=-1,lecName=lecName)
    else:
        return redirect('/')


@app.route("/get_page",methods = ['POST','GET'])
def get_page():
    my_page = request.args['my_page']
    
    return redirect(url_for('get_index',my_page=my_page))

@app.route("/delete_lecture",methods = ['POST','GET'])
def delete_lecture():
    lecNum = int(request.args["lecNum"])
    if 'user' in session:
        user_id = '%s' % escape(session['user'])
        conn = sqlite3.connect ('db.sqlite')
        c = conn.cursor()
        c.execute(f"delete FROM Lecture where userid = '{user_id}' and lecture_code = {lecNum};")
        conn.commit()
        
        lecture = all_list[lecNum]
        if("전공핵심" in lecture[4]):
            c.execute(f"UPDATE user SET grade_point= grade_point-{int(lecture[7])} WHERE user_id = '{user_id}';")
            c.execute(f"UPDATE user SET major_point= major_point-{int(lecture[7])} WHERE user_id = '{user_id}';")
            c.execute(f"UPDATE user SET major_main_point = major_main_point-{int(lecture[7])} WHERE user_id = '{user_id}';")
            conn.commit()
        elif("전공심화" in lecture[4]):
            c.execute(f"UPDATE user SET grade_point= grade_point-{int(lecture[7])} WHERE user_id = '{user_id}';")
            c.execute(f"UPDATE user SET major_point= major_point-{int(lecture[7])} WHERE user_id = '{user_id}';")
            conn.commit()
        elif("전공기초" in lecture[4]):
            c.execute(f"UPDATE user SET grade_point= grade_point-{int(lecture[7])} WHERE user_id = '{user_id}';")
            c.execute(f"UPDATE user SET major_point= major_point-{int(lecture[7])} WHERE user_id = '{user_id}';")
            conn.commit()
        elif("교양필수" in lecture[4]):
            c.execute(f"UPDATE user SET grade_point= grade_point-{int(lecture[7])} WHERE user_id = '{user_id}';")
            conn.commit()
        elif("교양선택" in lecture[4]):
            c.execute(f"UPDATE user SET grade_point= grade_point-{int(lecture[7])} WHERE user_id = '{user_id}';")
            c.execute(f"UPDATE user SET elec_point= elec_point-{int(lecture[7])} WHERE user_id = '{user_id}';") 
            conn.commit()
            
        if('사회봉사' in lecture[1]):
            c.execute(f"UPDATE user SET vol_point= 0 WHERE user_id = '{user_id}';") 
            conn.commit()
            
    return redirect(url_for('get_mytable'))




@app.route("/login")
def get_login():
    return render_template("login.html")

app.secret_key = "sample_key"


with app.app_context():
    if db.engine.url.drivername == 'sqlite':
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app, db)
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)