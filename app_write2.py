from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
# 플라스크 앱 생성 코드

# Firebase 초기화
cred = credentials.Certificate('authentication/firebase_auth.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# 사용자 정보 가져오기


def get_user_info(user_id):
    user_ref = db.collection(u'UserInfo').document(user_id)
    # 성현님 페이지에서 user_id 가져오게끔 수정.
    user_data = user_ref.get().to_dict()
    print(user_data)
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
    posts_ref = db.collection(u'posts').order_by(
        u'timestamp', direction=firestore.Query.DESCENDING)
    # print(posts_ref)
    # <google.cloud.firestore_v1.query.Query object at 0x000002C9CB9F4FD0>
    # [{'post_id': '1O4yqA7SIBPoriYEsaF3', 'title': '123',
    # 'category': 'category2', 'author': 'Unknown', 'timestamp': '2024-04-03 01:32:08.090000'}]
    # 출력결과

    #  timestamp -> 통일하고 contentinfo에다가도 쏘기. format 통일
    # date = datetime.now().strftime("%Y-%m-%d %I:%M:%S.%f")
    posts_list = []
    # posts_list 초기화
    posts = posts_ref.stream()
    # print(posts)
    for post in posts:
        post_data = post.to_dict()
        author_id = post_data['author_id']
        user_info = get_user_info(author_id)
        post_info = {
            'post_id': post.id,
            'title': post_data['title'],
            'category': post_data['category'],
            'author': user_info['username'],
            # 사용자 정보에서 작성자 이름(username) 가져오기
            'timestamp': post_data['timestamp'].strftime("%Y-%m-%d %I:%M:%S.%f")
            # 타임스탬프 형식 변환
            # 'timestamp': post_data['timestamp'].strftime("%Y-%m-%d %H:%M:%S")

            # date = datetime.now().strftime("%Y-%m-%d %I:%M:%S.%f")
            # print(post_info)
        }
        posts_list.append(post_info)
    return posts_list


# print(get_posts())
# post.id랑 post.to_dict() 를 묶어서 return 이부분 수정이 필요... -> 일단 수정함.


# 게시글 작성하기

@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        content = request.form['content']
        author_id = 'id_test'  # 임시로 설정, 실제 세션 등을 통해 사용자 ID를 가져와야 함
        # 새로운 게시글 생성
        post_ref = db.collection(u'posts').document()
        post_ref.set({
            u'title': title,
            u'category': category,
            u'content': content,
            u'author_id': author_id,
            u'timestamp': firestore.SERVER_TIMESTAMP
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
    post_ref = db.collection(u'posts').document(post_id)
    #  db에 post collection에 document id 가져옴
    post = post_ref.get().to_dict()
    # 글 가져와서 get dict 형태로 작성 (to dict)
    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        content = request.form['content']
        # 수정된 게시글 정보 업데이트 - 수정 필요 post_id
        post_ref.update({
            u'title': title,
            u'category': category,
            u'content': content
        })
        return redirect(url_for('index'))
    # url for index
    return render_template('edit.html', post=post, post_id=post_id)  # 수정

    # return render_template('edit.html', post=post)


# 글 삭제하기 - 추가(24.04.03)

@app.route('/delete/<post_id>')
# post_id에 대해서도 다시 Crosscheck 필요
def delete(post_id):
    post_ref = db.collection('posts').document(post_id)
    post_ref.delete()
    # delete/post_id로 가서 게시물 삭제.
    return redirect(url_for('index'))
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
