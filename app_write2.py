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
    user_ref = db.collection(u'Userinfo').document(user_id)
    user_data = user_ref.get().to_dict()
    return user_data

# 게시글 정보 가져오기


def get_posts():
    posts_ref = db.collection(u'posts').order_by(
        u'timestamp', direction=firestore.Query.DESCENDING)
    #  timestamp -> 통일하고 contentinfo에다가도 쏘기. format 통일
    # date = datetime.now().strftime("%Y-%m-%d %I:%M:%S.%f")
    posts = posts_ref.stream()

    return [post.to_dict() for post in posts]

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
        })
        return redirect(url_for('index'))
    return render_template('write.html')


# 게시글 수정하기
@app.route('/edit/<post_id>', methods=['GET', 'POST'])
# post_id -> content_info 수정
def edit(post_id):
    post_ref = db.collection(u'posts').document(post_id)
    #  db에 post collection에 document id 가져옴
    post = post_ref.get().to_dict()
    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        content = request.form['content']
        # 수정된 게시글 정보 업데이트
        post_ref.update({
            u'title': title,
            u'category': category,
            u'content': content
        })
        return redirect(url_for('index'))
    # url for index
    return render_template('edit.html', post=post, post_id=post_id)  # 수정

    # return render_template('edit.html', post=post)


# 인덱스 페이지 - 게시글 목록 보기


@app.route('/')
def index():
    user_id = 'id_test'  # 임시로 설정, 실제 세션 등을 통해 사용자 ID를 가져와야 함
    user_info = get_user_info(user_id)
    posts = get_posts()
    return render_template('index.html', user_info=user_info, posts=posts)


if __name__ == '__main__':
    app.run(debug=True)
