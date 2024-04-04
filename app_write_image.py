from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime


app = Flask(__name__)

# Firebase 초기화
cred = credentials.Certificate('authentication/firebase_auth.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# 사용자 정보 가져오기


def get_user_info(userinfo_id):
    user_ref = db.collection(u'ContentInfo').document(userinfo_id)
    user_data = user_ref.get().to_dict()
    if user_data is None:
        return {'username': 'Unknown'}
    return user_data

# 게시글 정보 가져오기


def get_posts():
    posts_ref = db.collection(u'ContentInfo').where(u'is_visible', u'==', True).order_by(
        u'create_date', direction=firestore.Query.DESCENDING)

    posts_list = []
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
            'userinfo_id': post_data['userinfo_id'],
            'content': post_data['content']
        }
        posts_list.append(post_info)
    return posts_list

# 게시글 작성하기


@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        content = request.form['content']
        userinfo_id = 'id_test'
        create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 이미지 업로드 및 URL 저장
        images = request.files.getlist('images[]')
        image_urls = []
        for image in images:
            # Firebase에 이미지 업로드
            # 예: image_url = upload_image_to_firebase(image)
            image_url = f'https://example.com/{image.filename}'
            image_urls.append(image_url)

        doc_count = len(db.collection(u'ContentInfo').get())
        new_doc_id = str(doc_count + 1)
        post_ref = db.collection(u'ContentInfo').document(new_doc_id)

        post_ref.set({
            u'title': title,
            u'category': category,
            u'content': content,
            u'userinfo_id': userinfo_id,
            u'create_date': create_date,
            u'images': image_urls,
            u'is_secret': False,
            u'is_visible': True,
            u'update_date': create_date
        })
        return redirect(url_for('index'))
    return render_template('write_image.html')

# 게시글 수정하기


@app.route('/edit/<post_id>', methods=['GET', 'POST'])
def edit(post_id):
    post_ref = db.collection(u'ContentInfo').document(post_id)
    post = post_ref.get().to_dict()
    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        content = request.form['content']
        update_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        post_ref.update({
            u'title': title,
            u'category': category,
            u'content': content,
            u'update_date': update_date
        })
        return redirect(url_for('index'))
    return render_template('edit_image.html', post=post, post_id=post_id)

# 글 삭제하기


@app.route('/delete/<post_id>')
def delete(post_id):
    post_ref = db.collection('ContentInfo').document(post_id)
    post_ref.update({'is_visible': False})
    return redirect(url_for('index'))

# 인덱스 페이지 - 게시글 목록 보기


@app.route('/')
def index():
    user_id = 'id_test'
    user_info = get_user_info(user_id)
    posts = get_posts()
    return render_template('index_image.html', user_info=user_info, posts=posts)


if __name__ == '__main__':
    app.run(debug=True)
