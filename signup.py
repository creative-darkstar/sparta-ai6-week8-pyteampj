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


# 유저 아이디 중복 체크
def check_id(userid):
    userid = str(userid)
    lst = [i.id for i in UserInfo.list_documents()]
    if userid in lst:
        return False
    else:
        return True


# 데이터 무결성 체크 - 회원가입용
def check_signup_data(userid, password, nickname, name, email):
    idc = r'^[A-Za-z\d]$'
    pwc = r'^[A-Za-z\d]$'
    nickc = r'^[A-Za-z\dㄱ-ㅣ가-힣]$'
    namec = r'^[A-Za-z\dㄱ-ㅣ가-힣]$'
    emailc = r'^^[a-zA-Z0-9+-\_.ㄱ-ㅣ가-힣]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    templist = [userid, password, nickname, name, email]
    checklist = [idc, pwc, nickc, namec, emailc]
    for i,e in enumerate(templist):
        if re.match(checklist[i], e):
            checklist[i] = True
        else:
            checklist[i] = False

    return checklist


# 비밀번호 확인
def check_password(password, checkpassword):
    if password == checkpassword:
        return True
    else:
        return False


# 유저 데이터 DB에 추가
def set_user_info(userid, password, nickname, name, email):
    userid = str(userid)
    nickname = str(nickname)
    name = str(name)
    email = str(email)
    password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    data = {
        'id': userid,
        'password': password,
        'nickname': nickname,
        'name': name,
        'email': email,
        'level': 0
    }

    try:
        UserInfo.document(userid).set(data)
        return True
    except:
        return False

# document id, document 안의 모든 요소 출력
# for doc in firestore.client().collection("테이블명").stream():
#     print(doc.id, doc.to_dict())

# 아이디가 test1 인 유저 데이터 가져오기
# a = UserInfo.document('test1').get()
# print(a.to_dict())

# collection 안에 document 개수
# results = UserInfo.count().get()[0][0].value
# print(results[0][0].value)

# 아이디 순서대로 추가
# check = True
# if check:
#     for i in range(3):
#         num = UserInfo.count().get()[0][0].value + 1
#         set_user_info(f'test{num}', 'password', 'nickname', 'name', 'email')