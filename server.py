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

bits = dbase.child("Bits")
users = dbase.child("Users")
comments = dbase.child("Comments")

def get_all():
    all_bits = db.reference("Bits").get()
    return all_bits


@app.route('/bits', methods=['GET'])
def get_all_bits():
    all_bits = get_all()
    return all_bits


@app.route('/bits', methods=['POST'])
def add_bit():
    bit = request.json['bit']
    r_name = request.json['username']
    bit_id = str(uuid.uuid4())
    timestamp = int(time() * 1000)

    new_bit = {}
    new_bit['username'] = r_name
    new_bit['bit'] = bit
    new_bit['timestamp'] = timestamp

    bits.child(bit_id).set(new_bit)

    bit = db.reference(f"Bits/{bit_id}").get()
    
    return bit


@app.route('/bit')  # http://localhost:PORT/bits?bitid=xzy123
def get_bit():
    bit_id = request.args.get('bitid')

    all_bits = get_all()

    if bit_id is not None:
        if bit_id in all_bits:
            return { bit_id: all_bits[bit_id]}
        else:
            return {"msg": "bit does not exist"}
    else:
        return {"msg": "missing param args"}


# Comments
@app.route('/bits/<username>/<bit_id>/comments', methods=['POST'])
def add_comment(username, bit_id):
    comment = request.json['comment']
    c_user = request.json['username']
    timestamp = int(time() * 1000)
    comment_id = str(uuid.uuid4())

    if comment is None:
        return {"msg": "Need a comment"}, 400

    comment_obj = {"comment": comment, "username": c_user, "timestamp": timestamp}

    comments.child(bit_id).child(comment_id).set(comment_obj)

    r_comment = db.reference(f"Comments/{bit_id}/{comment_id}").get()
    return r_comment

@app.route('/bits/<username>/<bit_id>/comments')
def get_comments(username, bit_id):

    all_comments = db.reference(f"Comments/{bit_id}").get()
    return all_comments

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
def all_users():
    # todo return users without passwords
    return users


@app.route('/users', methods=['GET'])
def query_user_bits():
    username = request.args.get('user')
    if username in bits:
        return bits[username]
    else:
        return {"msg": "user does not exist"}, 400


if __name__ == "__main__":
    app.run(debug=True, port=PORT)
