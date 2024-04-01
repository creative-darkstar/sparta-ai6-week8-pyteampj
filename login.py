import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('authentication/firebase_auth.json')
firebase_admin.initialize_app(cred)
db = firestore.client().collection(u'Project_DB').document(u'database').get().to_dict()

print(db['UserInfo'])


