import os
from flask import Flask, request, Response, jsonify
import firebase_admin
from firebase_admin import credentials, db
from dotenv import load_dotenv, find_dotenv
from werkzeug.security import check_password_hash, generate_password_hash
from time import time
import uuid


load_dotenv(find_dotenv())

cred = credentials.Certificate(os.getenv("GOOGLE_CREDENTIALS"))
db_url = os.getenv("DB_URL")
firebase_admin.initialize_app(cred, {
    'databaseURL': db_url
})

app = Flask(__name__)
app.config.from_object('config.Development')
PORT = os.getenv('PORT')

dbase = db.reference()

posts = dbase.child("Posts")
users = dbase.child("Users")
comments = {}


@app.route('/posts', methods=['GET'])
def get_all_bits():
    all_bits = db.reference("Posts").get()
    return all_bits


@app.route('/posts', methods=['POST'])
def add_bit():
    post = request.json['post']
    r_name = request.json['username']
    post_id = str(uuid.uuid4())
    timestamp = int(time() * 1000)

    new_bit = {}
    new_bit['username'] = r_name
    new_bit['post'] = post
    new_bit['timestamp'] = timestamp

    posts.child(post_id).set(new_bit)

    bit = db.reference(f"Posts/{post_id}").get()
    
    return bit


@app.route('/post')  # http://localhost:PORT/post?postid=xzy123
def get_bit():
    post_id = request.args.get('postid')

    if user is not None and post_id is not None:
        if post_id in posts[user]:
            return posts[user][post_id]
        else:
            return {"msg": "post does not exist"}
    else:
        return {"msg": "missing param args"}


# Comments
@app.route('/<username>/<post_id>/comment', methods=['POST'])
def addComment(username, post_id):
    comment = request.json['comment']
    c_user = request.json['username']
    timestamp = int(time() * 1000)

    if comment is None:
        return {"msg": "Need a comment"}, 400

    comment_obj = {"comment": comment, "username": c_user}

    if username in comments:
        if post_id in comments[username]:
            comments[username][post_id].insert(0, comment_obj)
        else:
            comments[username][post_id] = [comment_obj]
    else:
        comments[username] = {}
        comments[username][post_id] = [comment_obj]

    return jsonify(comments[username][post_id])


# User routes
@app.route('/register', methods=['POST'])
def register():
    id = str(uuid.uuid4())
    username = request.json['username']
    r_name = request.json['name']
    r_email = request.json['email']
    r_password = request.json['password']

    existing_users = db.reference('Users').get()
    
    if username in existing_users:
        return {"msg": "pick another username"}
    
    new_user = {}
    new_user["name"] = r_name
    new_user["id"] = id
    new_user["email"] = r_email
    new_user["password"] = generate_password_hash(r_password)

    users.child(username).set(new_user)

    r_user = db.reference(f"Users/{username}").get()
    # todo return user without password
    return r_user


@app.route('/login', methods=['POST'])
def login():
    r_name = request.json['username']
    r_password = request.json['password']
    username_str = 'Users/{}'.format(r_name)
    
    user = db.reference(username_str).get()

    if check_password_hash(user['password'], r_password):
        # todo return user without password
        return user, 200
    else:
        return {}, 401


@app.route('/allUsers', methods=['GET'])
def allUsers():
    # todo return users without passwords
    return users


@app.route('/users', methods=['GET'])
def query_user_posts():
    username = request.args.get('user')
    if username in posts:
        return posts[username]
    else:
        return {"msg": "user does not exist"}, 400


if __name__ == "__main__":
    app.run(debug=True, port=PORT)
