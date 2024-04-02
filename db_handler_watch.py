import firebase_admin
from google.cloud.firestore_v1.base_query import FieldFilter
import time
from datetime import datetime
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('authentication/firebase_auth.json')
firebase_admin.initialize_app(cred)


class Database:
    @classmethod
    def __init__(cls):
        pass

    @classmethod
    def content_select(cls, contentinfo_id):
        db = cls.__connection()
        return db.collection("ContentInfo").document(contentinfo_id).get()

    @classmethod
    def comment_select(cls, contentinfo_id):
        db = cls.__connection()
        return db.collection("CommentInfo").where(filter=FieldFilter("contentinfo_id", "==", contentinfo_id)).stream()

    @classmethod
    def comment_insert(cls, data):
        table = cls.__connection().collection("CommentInfo")
        num = table.count().get()[0][0].value + 1
        curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        table.add(
            document_data={
                "contentinfo_id": "f15ruAbukPXoMihgbfx8",
                "userinfo_id": "test2",
                "comment": "comment_test_2024-04-02",
                "cm_update_date": curr_time
            },
            document_id=str(num)
        )

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
    # for row in Database.comment_select("f15ruAbukPXoMihgbfx8"):
    #     print(row.id, row.to_dict())
    print(Database.content_select("f15ruAbukPXoMihgbfx8").to_dict())
