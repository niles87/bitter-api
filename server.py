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


@app.route('/posts', methods=['GET'])
def allPosts():
    return posts


@app.route('/post')
def getPost():
    user = request.args['user']
    post_id = request.args['postid']
    return '''
            <h1>user is {}</h1>
            <h1>post is {}</h1>'''.format(user, post_id)


@app.route('/posts', methods=['POST'])
def addPost():
    user_id = request.json['userId']
    post = request.json['post']
    r_name = request.json['name']
    title = request.json['title']
    post_id = str(uuid.uuid4())
    posts[r_name] = {}
    posts[r_name][post_id] = {}
    posts[r_name][post_id]['userId'] = user_id
    posts[r_name][post_id]['post'] = post
    return posts[r_name][post_id]


@app.route('/register', methods=['POST'])
def register():
    id = uuid.uuid4()
    r_name = request.json['name']
    r_email = request.json['email']
    r_password = request.json['password']
    users[r_name] = {}
    users[r_name]["id"] = id
    users[r_name]["email"] = r_email
    users[r_name]["password"] = generate_password_hash(r_password)
    # return user without password
    return users[r_name]


@app.route('/login', methods=['POST'])
def login():
    r_name = request.json['name']
    r_password = request.json['password']
    if check_password_hash(users[r_name]['password'], r_password):
        # return user without password
        return users[r_name]
    else:
        return {}, 401


@app.route('/allUsers', methods=['GET'])
def allUsers():
    return users


if __name__ == "__main__":
    app.run(debug=True, port=PORT)
