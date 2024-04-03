from datetime import datetime
from itertools import chain
from db_handler_watch import Database
# Flask 관련 패키지
"""
0. Flask : 웹서버를 시작할 수 있는 기능. app이라는 이름으로 플라스크를 시작한다
1. render_template : html파일을 가져와서 보여준다
"""
from flask import Flask, session, render_template, request, redirect, url_for, make_response
# Flask app 세팅
app = Flask(__name__)
app.secret_key = "1234"


@app.route("/error/")
def invalid():
    return render_template('invalid.html')


@app.route("/view/<contentinfo_id>/", methods=["GET", "POST"])
def view(contentinfo_id):
    # 페이지 이동 시 or 새로고침 시 cursor 삭제
    if request.method == 'GET':
        if "cm_cursor" in session:
            session.pop("cm_cursor", None)
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

    # 게시글 데이터 불러오기
    content = Database.content_select(contentinfo_id).to_dict()
    # 존재하지 않는 게시물이거나 삭제한 게시물인 경우
    if content is None or content["is_visible"] is False:
        return redirect(url_for("invalid"))

    # create_time, update_time 형식에 맞게 변환
    c_t = datetime.strptime(content["create_date"], "%Y-%m-%d %H:%M:%S")
    content["create_date"] = c_t.strftime("%Y년 %m월 %d일 %p %I시 %M분 %S초")
    u_t = datetime.strptime(content["update_date"], "%Y-%m-%d %H:%M:%S")
    content["update_date"] = u_t.strftime("%Y년 %m월 %d일 %p %I시 %M분 %S초")

    # 현재 접속한 유저가 게시글 작성자인지 확인
    # if "userinfo_id" in session:
    #     if session["userinfo_id"] == content["userinfo_id"]:
    #         is_content_owner = True
    #     else:
    #         is_content_owner = False
    # else:
    #     is_content_owner = False
    is_content_owner = True

    # 댓글 데이터 불러오기
    # 처음 페이지 로드한 경우에만 comment_cursor에 저장
    comments, last = Database.comment_select(contentinfo_id)
    if last is not None and "cm_cursor" not in session:
        print("Fisrt visit")
        print(last)
        session["cm_cursor"] = last

    # 추가 댓글 데이터 불러오기
    if request.method == "POST":
        if "cm_cursor" in session:
            more_comments, last = Database.comment_select_more(contentinfo_id, session["cm_cursor"])
            print(last)
            comments = chain(comments, more_comments)
            if last is not None:
                session["cm_cursor"] = last
            else:
                session.pop("cm_cursor", None)

    # 추가 댓글 여부에 따른 패키지에 저장할 bool 값
    is_more_comment = True if "cm_cursor" in session else False
    print(is_more_comment)

    # html 전송 패키지
    package = {
        "contentinfo_id": contentinfo_id,
        "is_content_owner": is_content_owner,
        "is_more_comment": is_more_comment,
        "content": content,
        "comments": []
    }
    for item in comments:
        row = item.to_dict()
        # cm_update_time 형식에 맞게 변환
        t = datetime.strptime(row["cm_update_date"], "%Y-%m-%d %H:%M:%S")
        row["cm_update_date"] = t.strftime("%Y년 %m월 %d일 %p %I시 %M분 %S초")
        # 현재 접속한 유저가 댓글 작성자인지 확인
        # if "userinfo_id" in session:
        #     if session["userinfo_id"] == row["userinfo_id"]:
        #         is_comment_owner = True
        #     else:
        #         is_comment_owner = False
        # else:
        #     is_comment_owner = False
        is_comment_owner = True if row["userinfo_id"] == "test3" else False
        row["is_comment_owner"] = is_comment_owner
        package["comments"].append(row)
    # print(package)
    return render_template('view.html', data=package)


if __name__ == "__main__":
    app.run(debug=True)
