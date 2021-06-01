# config.py
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # 응용프로그램 데이터베이스의 위치를 가져옴, DATABASE_URL 환경 변수에서 데이터베이스 URL을 가져오고, 정의되지 않은 경우 변수에 저장된 응용 프로그램의 기본 디렉토리에 app.db라는 데이터베이스를 구성하고 있다.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False