from db_handler_watch import Database
from datetime import datetime

# 필수 라이브러리
"""
0. Flask : 웹서버를 시작할 수 있는 기능. app이라는 이름으로 플라스크를 시작한다
1. render_template : html파일을 가져와서 보여준다
"""
from flask import Flask, session, render_template, request, redirect, url_for
app = Flask(__name__)


@app.route("/view/<contentinfo_id>/", methods=["GET", "POST"])
def view(contentinfo_id):
    # if request.method == 'POST':
    #     if "userinfo_id" in session:
    #         comment = request.form["comment"]
    #         cm_update_date = datetime.now().strftime("%Y-%m-%d %I:%M:%S.%f")
    #
    #         # 댓글 생성
    #         comment_data = {
    #             'contentinfo_id': contentinfo_id,
    #             'userinfo_id': session["userinfo_id"],
    #             'comment': comment,
    #             'cm_update_date': cm_update_date,
    #         }
    #         Database.comment_insert(comment_data)
    #         return redirect(url_for("view"))

    content = Database.content_select(contentinfo_id).to_dict()
    c_t = datetime.strptime(content["create_date"], "%Y-%m-%d %H:%M:%S.%f")
    u_t = datetime.strptime(content["update_date"], "%Y-%m-%d %H:%M:%S.%f")
    content["create_date"] = c_t.strftime("%Y년 %m월 %d일 %p %I시 %M분 %S초")
    content["update_date"] = u_t.strftime("%Y년 %m월 %d일 %p %I시 %M분 %S초")

    comments = Database.comment_select(contentinfo_id)
    package = {
        "contentinfo_id": contentinfo_id,
        "content": content,
        "comments": []
    }
    for item in comments:
        row = item.to_dict()
        t = datetime.strptime(row["cm_update_date"], "%Y-%m-%d %H:%M:%S.%f")
        row["cm_update_date"] = t.strftime("%Y년 %m월 %d일 %p %I시 %M분 %S초")
        package["comments"].append(row)
    print(package)
    return render_template('view.html', data=package)

    # edit button
    # return redirect(url_for("edit/<contentinfo_id>/"))


if __name__ == "__main__":
    app.run(debug=True)
