from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime


app = Flask(__name__)
# 플라스크 앱 생성 코드

# Firebase 초기화
cred = credentials.Certificate('authentication/firebase_auth.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# 사용자 정보 가져오기


def get_user_info(userinfo_id):
    user_ref = db.collection(u'ContentInfo').document(userinfo_id)
    # 성현님 페이지에서 user_id 가져오게끔 수정.
    user_data = user_ref.get().to_dict()
    # print(user_data)
    if user_data is None:
        # 사용자 정보를 찾을 수 없는 경우, 기본 정보를 반환
        # return {'nicekname': 'Unknown'}
        return {'username': 'Unknown'}

    return user_data

# 게시글 정보 가져오기 - 24.04.02 ver
# def get_posts():
#     posts_ref = db.collection(u'posts').order_by(
#         u'timestamp', direction=firestore.Query.DESCENDING)
#     #  timestamp -> 통일하고 contentinfo에다가도 쏘기. format 통일
#     # date = datetime.now().strftime("%Y-%m-%d %I:%M:%S.%f")
#     posts = posts_ref.stream()
#     return [post.id for post in posts]


# 게시글 정보 가져오기 - 24.04.03 수정본
def get_posts():
    posts_ref = db.collection(u'ContentInfo').where(u'is_visible', u'==', True).order_by(
        u'create_date', direction=firestore.Query.DESCENDING)

    #  timestamp -> 통일하고 contentinfo에다가도 쏘기. format 통일
    # date = datetime.now().strftime("%Y-%m-%d %I:%M:%S.%f")
    posts_list = []
    # posts_list 초기화
    posts = posts_ref.stream()
    for post in posts:
        post_data = post.to_dict()
        author_id = post_data['userinfo_id']
        user_info = get_user_info(author_id)
        post_info = {
            'post_id': post.id,
            'title': post_data['title'],
            'category': post_data['category'],
            'author': user_info['username'],
            'create_date': post_data['create_date'],
            'images': post_data.get('images', []),
            'is_secret': post_data['is_secret'],
            'update_date': post_data['update_date'],
            'userinfo_id': post_data['userinfo_id']

            # 'post_id': post.id,
            # 'title': post_data['title'],
            # 'category': post_data['category'],
            # 'author': user_info['username'],
            # # 사용자 정보에서 작성자 이름(username) 가져오기
            # 'timestamp': post_data['timestamp'].strftime("%Y-%m-%d %I:%M:%S.%f")
            # # 타임스탬프 형식 변환
            # 'timestamp': post_data['timestamp'].strftime("%Y-%m-%d %H:%M:%S")

            # date = datetime.now().strftime("%Y-%m-%d %I:%M:%S.%f")
            # print(post_info)
        }

        posts_list.append(post_info)
    return posts_list


# print(get_posts())
# post.id랑 post.to_dict() 를 묶어서 return 이부분 수정이 필요... -> 일단 수정함.

#


# 게시글 작성하기 24.04.03

@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        content = request.form['content']
        userinfo_id = 'id_test'  # 임시로 설정. 병합 후에는 사용자 ID를 가져와야 함
        create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # # 새로운 게시글 생성
        doc_count = len(db.collection(u'ContentInfo').get())
        new_doc_id = str(doc_count + 1)
        # 새로운 doc id - doc_count +1 해서 길이 조정.
        post_ref = db.collection(u'ContentInfo').document(new_doc_id)

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
        return redirect(url_for('index'))
    return render_template('write.html')


# 게시글 수정하기
@app.route('/edit/<post_id>', methods=['GET', 'POST'])
# post_id -> content_info 수정
def edit(post_id):
    # print(f"{post_id=}")
    post_ref = db.collection(u'ContentInfo').document(post_id)
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
        return redirect(url_for('index'))
    # url for index
    return render_template('edit.html', post=post, post_id=post_id)  # 수정

    # return render_template('edit.html', post=post)


# 글 삭제하기 - 추가(24.04.03)

@app.route('/delete/<post_id>')
# post_id에 대해서도 다시 Crosscheck 필요
def delete(post_id):
    post_ref = db.collection('ContentInfo').document(post_id)
    post_ref.update({'is_visible': False})
    # 삭제할경우, is visible을 False로 업데이트
    return redirect(url_for('index'))
    # post_ref.delete()

# 게시물 삭제 후 index로 돌아가기.


# 인덱스 페이지 - 게시글 목록 보기
@app.route('/')
def index():
    user_id = 'id_test'  # 임시로 설정, 실제 세션 등을 통해 사용자 ID를 가져와야 함
    user_info = get_user_info(user_id)
    posts = get_posts()
    # print(posts)
    return render_template('index.html', user_info=user_info, posts=posts)


if __name__ == '__main__':
    app.run(debug=True)
