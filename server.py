import os
from flask import Flask, request, Response, jsonify
import firebase_admin
from firebase_admin import credentials, db
from dotenv import load_dotenv, find_dotenv
from werkzeug.security import check_password_hash, generate_password_hash
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

db = firebase_admin.db.reference()

posts = {}
users = db.child("Users")
comments = {}


@app.route('/posts', methods=['GET'])
def all_bits():
    return posts


@app.route('/posts', methods=['POST'])
def add_bit():
    user_id = request.json['userId']
    post = request.json['post']
    r_name = request.json['username']
    post_id = str(uuid.uuid4())

    if r_name in posts:
        posts[r_name][post_id] = {}
    else:
        posts[r_name] = {}
        posts[r_name][post_id] = {}

    posts[r_name][post_id]['userId'] = user_id
    posts[r_name][post_id]['post'] = post
    return posts[r_name][post_id]


@app.route('/post')  # http://localhost:PORT/post?user=username&postid=xzy123
def get_bit():
    user = request.args.get('user')
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

    # if username in users:
    #     return {"msg": "pick another username"}
    new_user = {}
    new_user[username] = {}
    new_user[username]["name"] = r_name
    new_user[username]["id"] = id
    new_user[username]["email"] = r_email
    new_user[username]["password"] = generate_password_hash(r_password)

    
    user = users.push(new_user)
    # print(user.Reference)
    # todo return user without password
    return user


@app.route('/login', methods=['POST'])
def login():
    r_name = request.json['name']
    r_password = request.json['password']
    if check_password_hash(users[r_name]['password'], r_password):
        # todo return user without password
        return users[r_name]
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
