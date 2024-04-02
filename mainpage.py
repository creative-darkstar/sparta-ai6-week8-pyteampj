from flask import Flask,redirect,render_template,url_for,request
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

app=Flask(__name__)

cred = credentials.Certificate('authentication/firebase_auth.json')
firebase_admin.initialize_app(cred)

db = firestore.client()
contentlist = db.collection('ContentInfo')
userlist=db.collection('UserInfo')
categroy=contentlist.document('f15ruAbukPXoMihgbfx8').get().to_dict()['category']
title=contentlist.document('f15ruAbukPXoMihgbfx8').get().to_dict()['title']
content=contentlist.document('f15ruAbukPXoMihgbfx8').get().to_dict()['content']
is_secret=contentlist.document('f15ruAbukPXoMihgbfx8').get().to_dict()['is_secret']
update_date=contentlist.document('f15ruAbukPXoMihgbfx8').get().to_dict()['update_date']
userinfo_id=contentlist.document('f15ruAbukPXoMihgbfx8').get().to_dict()['userinfo_id']
nickname=userlist.document('test1').get().to_dict()['nickname']
print(categroy,title,content,is_secret,update_date,userinfo_id,nickname)

@app.route("/")
def mainpage():
    return render_template("mainpage.html")

if __name__ == '__main__':
    app.run(debug=True)