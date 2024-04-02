import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from flask import Flask, request, render_template, session, url_for, redirect
from login import check_login_data, check_login
from register import check_id, check_signup_data, check_password, set_user_info

# DB 초기화
cred = credentials.Certificate('authentication/firebase_auth.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
UserInfo = db.collection('UserInfo')
contentlist = db.collection('ContentInfo')
userlist=db.collection('UserInfo')

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

#기본페이지->login페이지
@app.route("/")
def home():
    return redirect(url_for('login'))

#로그인페이지->회원가입, 메인페이지
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']
        if check_login_data(userid, password):
            if check_login(UserInfo, userid, password):
                session["logged_in"] = True
                session['userid'] = userid
                print(session)
                return redirect(url_for('mainpage'))
            else:
                print('아이디와 비밀번호를 정확히 입력해 주세요')
                return render_template('login.html')
        else:
            print('아이디와 비밀번호를 정확히 입력해 주세요')
            return render_template('login.html')
    else:
        return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']
        passwordcheck = request.form['passwordcheck']
        nickname = request.form['nickname']
        name = request.form['name']
        email = request.form['email']
        if check_id(UserInfo, userid):
            if check_signup_data(password, nickname, name, email):
                if check_password(password, passwordcheck):
                    set_user_info(UserInfo, userid, password,nickname, name, email)
                    return redirect(url_for('login'))
        return render_template('register.html')
    else:
        return render_template('register.html')


@app.route("/mainpage", methods=['GET', 'POST'])
def mainpage():
    categroy=contentlist.document('f15ruAbukPXoMihgbfx8').get().to_dict()['category']
    title=contentlist.document('f15ruAbukPXoMihgbfx8').get().to_dict()['title']
    content=contentlist.document('f15ruAbukPXoMihgbfx8').get().to_dict()['content']
    is_secret=contentlist.document('f15ruAbukPXoMihgbfx8').get().to_dict()['is_secret']
    update_date=contentlist.document('f15ruAbukPXoMihgbfx8').get().to_dict()['update_date']
    userinfo_id=contentlist.document('f15ruAbukPXoMihgbfx8').get().to_dict()['userinfo_id']
    nickname=userlist.document('test1').get().to_dict()['nickname']
    data={
        'category':categroy,
        'title':title,
        'content':content,
        'is_secret':is_secret,
        'update_date':update_date,
        'userinfo_id':userinfo_id,
        'nickname':nickname,
    }
    return render_template("mainpage.html",data=data)

@app.route("/logout")
def logout():
    session['logged_in'] = False
    session.pop('userid', None)
    print(session)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
