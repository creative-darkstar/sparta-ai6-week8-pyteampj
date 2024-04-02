import re
import hashlib
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# DB 초기화
cred = credentials.Certificate('authentication/firebase_auth.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
UserInfo = db.collection('UserInfo')


# 데이터 무결성 체크 - 로그인용
def check_login_data(userid, password):
    idc = r'^[A-Za-z\d]$'
    pwc = r'^[A-Za-z\d]$'

    if re.match(idc, userid) and re.match(pwc, password):
        return True
    else:
        return False


# 로그인 체크
def check_login(userid, password):
    if check_login_data(userid, password):
        if UserInfo.document(userid).get().to_dict() != None:
            password = hashlib.sha256(password.encode('utf-8')).hexdigest()
            if UserInfo.document(userid).get().to_dict()['password'] == password:
                return True
            else:
                return False
        else:
            return False
    else:
        return False
