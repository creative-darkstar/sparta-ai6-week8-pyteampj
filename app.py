from datetime import datetime
from itertools import chain
from db_handler import Database
from flask import Flask, request, render_template, session, url_for, redirect
from login import check_login_data, check_login
from register import check_id, check_signup_data, check_password, set_user_info

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'


# app_login.py
# ----------------------------------------------------------


# 기본페이지->login페이지
@app.route("/")
def home():
    return redirect(url_for('login'))


# app_watch.py 에러 페이지
@app.route("/error/")
def invalid():
    return render_template('invalid.html')


# 로그인페이지->회원가입, 메인페이지
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']
        if check_login_data(userid, password):
            user_info = Database.get_userinfo()
            if check_login(user_info, userid, password):
                session["logged_in"] = True
                session['userid'] = userid
                print(session)
                return redirect(url_for('mainpage1'))
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
        user_info = Database.get_userinfo()
        if check_id(user_info, userid):
            if check_signup_data(password, nickname, name, email):
                if check_password(password, passwordcheck):
                    set_user_info(user_info, userid, password,nickname, name, email)
                    return redirect(url_for('login'))
        return render_template('register.html')
    else:
        return render_template('register.html')


@app.route("/mainpage1", methods=['GET', 'POST'])
def mainpage1():
    session_id = session['userid']
    content_info = Database.get_contentinfo()
    ccl = list(content_info.where("category", "==", "1").where("is_visible", "==", True).stream())
    return render_template("mainpage1.html", ccl=ccl, session_id=session_id)


@app.route("/mainpage2", methods=['GET', 'POST'])
def mainpage2():
    session_id = session['userid']
    content_info = Database.get_contentinfo()
    ccl = list(content_info.where("category", "==", "2").where("is_visible", "==", True).stream())
    return render_template("mainpage1.html", ccl=ccl, session_id=session_id)


@app.route("/mainpage3", methods=['GET', 'POST'])
def mainpage3():
    session_id = session['userid']
    content_info = Database.get_contentinfo()
    ccl = list(content_info.where("category", "==", "3").where("is_visible", "==", True).stream())
    return render_template("mainpage1.html", ccl=ccl, session_id=session_id)


@app.route("/logout")
def logout():
    session['logged_in'] = False
    session.pop('userid', None)
    print(session)
    return redirect(url_for('login'))


# app_write.py
# ----------------------------------------------------------


# 게시글 작성하기 24.04.03
@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        content = request.form['content']
        userinfo_id = session["userid"]
        create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # # 새로운 게시글 생성
        content_info = Database.get_contentinfo()
        doc_count = len(content_info.get())
        new_doc_id = str(doc_count + 1)
        # 새로운 doc id - doc_count +1 해서 길이 조정.
        post_ref = content_info.document(new_doc_id)

        # post_ref = db.collection(u'ContentInfo').document()
        post_ref.set({
            u'title': title,
            u'category': category,
            u'content': content,
            u'userinfo_id': userinfo_id,
            u'create_date': create_date,
            u'images': [],
            u'is_secret': False,
            # is_secrt : 비밀글 여부.
            u'is_visible': True,
            u'update_date': create_date
            # 작성 시점 (timestamp 기록)
            #  post_ref에 set으로 받음.
        })
        return redirect(url_for(f"mainpage{post_ref.get().to_dict()['category']}"))
    return render_template('write.html')


# 게시글 수정하기
@app.route('/edit/<post_id>', methods=['GET', 'POST'])
# post_id -> content_info 수정
def edit(post_id):
    # print(f"{post_id=}")
    content_info = Database.get_contentinfo()
    post_ref = content_info.document(post_id)
    #  db에 ContentInfo collection에 document id 가져옴
    post = post_ref.get().to_dict()
    # 글 가져와서 get dict 형태로 작성 (to dict)
    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        content = request.form['content']
        update_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 수정된 게시글 정보 업데이트 - 수정 필요 post_id
        post_ref.update({
            u'title': title,
            u'category': category,
            u'content': content,
            u'update_date': update_date
        })
        return redirect(url_for(f"mainpage{post_ref.get().to_dict()['category']}"))
    # url for index
    return render_template('edit.html', post=post, post_id=post_id)  # 수정

    # return render_template('edit.html', post=post)


# 글 삭제하기 - 추가(24.04.03)
@app.route('/delete/<post_id>')
# post_id에 대해서도 다시 Crosscheck 필요
def delete(post_id):
    content_info = Database.get_contentinfo()
    post_ref = content_info.document(post_id)
    post_ref.update({'is_visible': False})
    # 삭제할경우, is visible을 False로 업데이트
    return redirect(url_for(f"mainpage{post_ref.get().to_dict()['category']}"))
    # post_ref.delete()


# app_write.py
# ----------------------------------------------------------
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
                    "userinfo_id": session["userid"],
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
                if "userid" in session:
                    if session["userid"] == row["userinfo_id"]:
                        is_comment_owner = True
                    else:
                        is_comment_owner = False
                else:
                    is_comment_owner = False
                html_text = f"""<td>{session["userid"]}</td>
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
            return package

    # create_time, update_time 형식에 맞게 변환
    c_t = datetime.strptime(content["create_date"], "%Y-%m-%d %H:%M:%S")
    content["create_date"] = c_t.strftime("%Y년 %m월 %d일 %p %I시 %M분 %S초")
    u_t = datetime.strptime(content["update_date"], "%Y-%m-%d %H:%M:%S")
    content["update_date"] = u_t.strftime("%Y년 %m월 %d일 %p %I시 %M분 %S초")

    # 현재 접속한 유저가 게시글 작성자인지 확인
    if "userid" in session:
        if session["userid"] == content["userinfo_id"]:
            is_content_owner = True
        else:
            is_content_owner = False
    else:
        is_content_owner = False

    # html 전송 패키지
    if "userid" in session:
        curr_user_id = session["userid"]
    else:
        curr_user_id = ""
    package = {
        "contentinfo_id": contentinfo_id,
        "current_user_id": curr_user_id,
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
        if "userid" in session:
            if session["userid"] == row["userinfo_id"]:
                is_comment_owner = True
            else:
                is_comment_owner = False
        else:
            is_comment_owner = False
        row["is_comment_owner"] = is_comment_owner
        row["row_id"] = item.id
        package["comments"].append(row)

    return render_template('view.html', data=package)


if __name__ == '__main__':
    app.run(debug=True)
