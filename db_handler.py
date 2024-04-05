import time
from datetime import datetime

# Firebase 관련 패키지
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

cred = credentials.Certificate('authentication/firebase_auth.json')
firebase_admin.initialize_app(cred)
ITEM_PER_PAGE = 5


class Database:
    @classmethod
    def __init__(cls):
        pass

    @classmethod
    def get_userinfo(cls):
        db = cls.__connection()
        return db.collection('UserInfo')

    @classmethod
    def get_contentinfo(cls):
        db = cls.__connection()
        return db.collection('ContentInfo')

    @classmethod
    def content_select(cls, contentinfo_id):
        db = cls.__connection()
        return db.collection("ContentInfo").document(contentinfo_id).get()

    @classmethod
    def comment_select(cls, contentinfo_id):
        db = cls.__connection()
        data = db.collection("CommentInfo").where(
            filter=FieldFilter("contentinfo_id", "==", contentinfo_id)
        ).where(
            filter=FieldFilter("is_visible", "==", True)
        ).order_by("cm_create_date").limit(ITEM_PER_PAGE)
        docs = data.get()
        if len(docs) == ITEM_PER_PAGE:
            last = docs[-1].to_dict()["cm_create_date"]
        else:
            last = None
        return data.stream(), last

    @classmethod
    def comment_select_more(cls, contentinfo_id, cursor):
        db = cls.__connection()
        data = db.collection("CommentInfo").where(
            filter=FieldFilter("contentinfo_id", "==", contentinfo_id)
        ).where(
            filter=FieldFilter("is_visible", "==", True)
        ).order_by("cm_create_date").limit(ITEM_PER_PAGE).start_after({"cm_create_date": cursor})
        docs = data.get()
        if len(docs) == ITEM_PER_PAGE:
            last = docs[-1].to_dict()["cm_create_date"]
        else:
            last = None
        return data.stream(), last

    @classmethod
    def comment_insert(cls, data: dict):
        table = cls.__connection().collection("CommentInfo")
        num = int(table.count().get()[0][0].value) + 1
        curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        table.add(
            document_data={
                "contentinfo_id": data["contentinfo_id"],
                "userinfo_id": data["userinfo_id"],
                "comment": data["comment"],
                "is_visible": True,
                "cm_create_date": curr_time,
                "cm_update_date": curr_time
            },
            document_id=str(num)
        )

    @classmethod
    def comment_edit(cls, data: dict, doc_id: str):
        table = cls.__connection().collection("CommentInfo")
        curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        target = table.document(doc_id)
        if "is_visible" in data.keys():
            target.update({
                "is_visible": data["is_visible"],
                "cm_update_date": curr_time
            })
        else:
            target.update({
                "comment": data["comment"],
                "cm_update_date": curr_time
            })
            return curr_time

    @classmethod
    def __connection(cls, retry_count=5):
        for try_num in range(retry_count + 1):
            try:
                db = firestore.client()
            except Exception as e:
                print("[Error: DB Connection] ", e)
                pass
            else:
                return db
            if try_num == 5:
                print("Connection will stop.")
                return None
            time.sleep(2 ** try_num)
            print(f"RETRY CONNECTION... {try_num + 1}th try")
            continue


if __name__ == "__main__":
    # Database.comment_insert(data={})
    rows, c = Database.comment_select("1")
    for row in rows:
        print(row.id, row.to_dict())
    # print(Database.content_select("f15ruAbukPXoMihgbfx8").to_dict())
