import os
from flask import Flask, request, Response
import firebase_admin
from firebase_admin import credentials, db
from dotenv import load_dotenv, find_dotenv
from werkzeug.security import check_password_hash, generate_password_hash
import uuid


load_dotenv(find_dotenv())

# cred = credentials.Certificate(os.getenv("GOOGLE_CREDENTIALS"))
# firebase_admin.initialize_app(cred, {
#     'databaseURL': 'https://bitter-api-default-rtdb.firebaseio.com/'
# })

app = Flask(__name__)
app.config.from_object('config.Development')
PORT = os.getenv('PORT')

posts = {}
users = {}
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


# User routes
@app.route('/register', methods=['POST'])
def register():
    id = uuid.uuid4()
    username = request.json['username']
    r_name = request.json['name']
    r_email = request.json['email']
    r_password = request.json['password']

    if username in users:
        return {"msg": "pick another username"}

    users[username] = {}
    users[username]["name"] = r_name
    users[username]["id"] = id
    users[username]["email"] = r_email
    users[username]["password"] = generate_password_hash(r_password)
    # todo return user without password
    return users[username]


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
