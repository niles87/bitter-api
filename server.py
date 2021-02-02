import os
from flask import Flask
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
def posts():
    return "<h1>Hello world</h1>"

if __name__ == "__main__":
    app.run(debug=True, port=4000)
