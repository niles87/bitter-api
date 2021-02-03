import os
from flask import Flask, request, Response
import firebase_admin
from firebase_admin import credentials, db
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

cred = credentials.Certificate(os.getenv("GOOGLE_CREDENTIALS"))
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://bitter-api-default-rtdb.firebaseio.com/'
})

app = Flask(__name__)
app.config.from_object('config.Development')


@app.route('/posts', methods=['GET'])
def allPosts():
    return "<h1>Hello world</h1>"


@app.route('/post')
def getPost():
    user = request.args['user']
    post = request.args['post']
    return '''
            <h1>user is {}</h1>
            <h1>post is {}</h1>'''.format(user, post)


@app.route('/posts', methods=['POST'])
def addPost():
    return "post added"


@app.route('/register', methods=['POST'])
def register():
    return True


@app.route('/login', methods=['POST'])
def login():
    return True


if __name__ == "__main__":
    app.run(debug=True, port=4000)
