from datetime import datetime
from itertools import chain
from db_handler_watch import Database
# Flask 관련 패키지
"""
0. Flask : 웹서버를 시작할 수 있는 기능. app이라는 이름으로 플라스크를 시작한다
1. render_template : html파일을 가져와서 보여준다
"""
from flask import Flask, session, render_template, request, redirect, url_for, jsonify
# Flask app 세팅
app = Flask(__name__)
app.secret_key = "1234"


@app.route("/error/")
def invalid():
    return render_template('invalid.html')


@app.route("/view/<contentinfo_id>/", methods=["GET", "POST"])
def view(contentinfo_id):
    # 페이지 데이터 불러오기
    # 게시글 데이터
    content = Database.content_select(contentinfo_id).to_dict()
    # 존재하지 않는 게시물이거나 삭제한 게시물인 경우
    if content is None or content["is_visible"] is False:
        return redirect(url_for("invalid"))

    # 댓글 데이터
    # 처음 페이지 로드한 경우에만 comment_cursor에 저장
    comments, cursor = Database.comment_select(contentinfo_id)

    # 버튼
    if request.method == "POST":
        data = request.get_json()

        # create comment (ajax)
        if "insert_comment" in data.keys():
            input_comment = data["insert_comment"]
            Database.comment_insert(
                data={
                    "contentinfo_id": contentinfo_id,
                    # "userinfo_id": session["userinfo_id"],
                    "userinfo_id": "test3",
                    "comment": input_comment,
                }
            )
            return input_comment

        # update comment (ajax)
        elif "update_item" in data.keys() and "update_comment" in data.keys():
            target_id = str(data["update_item"])
            new_cmt = data["update_comment"]
            new_udate = Database.comment_edit(
                data={
                    "comment": new_cmt
                },
                doc_id=target_id
            )
            new_udate = datetime.strptime(new_udate, "%Y-%m-%d %H:%M:%S").strftime("%Y년 %m월 %d일 %p %I시 %M분 %S초")
            return {"row_id": target_id, "comment": new_cmt, "udate": new_udate}

        # delete comment (ajax)
        elif "delete_item" in data.keys():
            target_id = str(data["delete_item"])
            Database.comment_edit(
                data={
                    "is_visible": False
                },
                doc_id=target_id
            )
            return target_id

        # more comments (ajax)
        elif "cursor" in data.keys():
            cursor = data["cursor"]
            more_comments, cursor = Database.comment_select_more(contentinfo_id, cursor)

            # 전송 패키지
            html_rows = []

            for item in more_comments:
                row = item.to_dict()
                # cm_update_time 형식에 맞게 변환
                t = datetime.strptime(row["cm_update_date"], "%Y-%m-%d %H:%M:%S").strftime("%Y년 %m월 %d일 %p %I시 %M분 %S초")
                # 현재 접속한 유저가 댓글 작성자인지 확인
                # if "userinfo_id" in session:
                #     if session["userinfo_id"] == row["userinfo_id"]:
                #         is_comment_owner = True
                #     else:
                #         is_comment_owner = False
                # else:
                #     is_comment_owner = False
                is_comment_owner = True if row["userinfo_id"] == "test3" else False
                html_text = f"""<td>{row["userinfo_id"]}</td>
<td id="cm_row_{item.id}_cmt_view" style="display: run-in">
    {row["comment"]}
</td>
<td colspan="2" id="cm_row_{item.id}_cmt_edit" style="display: none">
    <label for="edit_comment_{item.id}" style="display: none">>댓글 수정</label>
    <textarea class="form-control" cols="25" rows="1"
              id="edit_comment_{item.id}"></textarea>
</td>"""
                if is_comment_owner is True:
                    html_text += f"""<td id="cm_row_{item.id}_udate" style="display: run-in">{t}</td>
<td id="cm_row_{item.id}_btns" style="display: run-in">
    <button class="btn btn-secondary pull-right" type="button"
            onclick="isEditClicked('{item.id}')">Edit</button>
    <button class="btn btn-danger pull-right" type="button"
            onclick="deleteConfirm('{item.id}')">Delete</button>
</td>
<td id="cm_row_{item.id}_edit_btn" style="display: none">
    <button class="btn btn-secondary pull-right" type="button"
            onclick="isEditClicked('{item.id}')">Cancel</button>
    <button class="btn btn-primary pull-right" type="button"
            onclick="isEditConfirmed('{item.id}')">Confirm</button>
</td>"""
                else:
                    html_text += f"""<td colspan="2">{t}</td>"""

                html_rows.append({"id": item.id, "html_text": html_text})

            package = {
                "more_comment_cursor": cursor,
                "comments_html": html_rows
            }
            # print(package)
            return package


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

    # html 전송 패키지
    package = {
        "contentinfo_id": contentinfo_id,
        "is_content_owner": is_content_owner,
        "more_comment_cursor": cursor,
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
        row["row_id"] = item.id
        package["comments"].append(row)
    # print(package)
    return render_template('view.html', data=package)


if __name__ == "__main__":
    app.run(debug=True)
