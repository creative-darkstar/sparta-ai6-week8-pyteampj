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

test=list(contentlist.stream())
print(test[0].to_dict(),test[0].id)
# for doc in test:
#     print(f'{doc.id}=>{doc.to_dict()}')


# @app.route("/")
# def mainpage():
#     return render_template("mainpage.html")

# if __name__ == '__main__':
#     app.run(debug=True)