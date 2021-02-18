import os
from flask import Flask, request, Response, jsonify
# from firebase_admin import credentials, db, initialize_app
from mongoengine import *
from models import User, Bit, Comment
from dotenv import load_dotenv, find_dotenv
from werkzeug.security import check_password_hash, generate_password_hash
from time import time
import uuid, json


load_dotenv(find_dotenv())

# cred = credentials.Certificate(os.getenv("GOOGLE_CREDENTIALS"))
# initialize_app(cred, {
#     'databaseURL': db_url
# })

app = Flask(__name__)
app.config.from_object('config.Development')
PORT = os.getenv('PORT')
db_url = os.getenv("DB_URL")
connect(host=db_url)

def get_all():
    # all_bits = db.reference("Bits").get()
    return {}


@app.route('/bits') # http://localhost:4000/bits?user=xxx
def get_bits():
    username = request.args.get('user')
    if username == None:
        bits = Bit.objects.to_json()
        return jsonify({"data": json.loads(bits)})
    else:
        user = User.objects.filter(username=username)
        bits = Bit.objects.filter(author=user[0]).to_json()
        return jsonify({"data": json.loads(bits)})
    

@app.route('/bits', methods=['POST'])
def add_bit():
    bit = request.json['bit']
    r_name = request.json['username']

    if (bit is None or bit == "") or (r_name is None or r_name == ""):
        return {"msg": "missing data in request body"}, 400

    user = User.objects.filter(username=r_name)

    new_bit = Bit(bit=bit)
    new_bit.author = user[0]

    try:
        new_bit.save()
    except:
        return {"msg": "failed to add new bit"}, 400
    else:
        return {"msg": "success"}, 201


@app.route('/bit')  # http://localhost:PORT/bit?bitid=xzy123
def get_bit():
    bit_id = request.args.get('bitid')

    # all_bits = get_all()

    # if bit_id is not None:
    #     if bit_id in all_bits:
    #         return {"data": {bit_id: all_bits[bit_id]}}
    #     else:
    #         return {"msg": "bit does not exist"}
    # else:
    #     return {"msg": "missing param args"}
    return {}


# Comments
@app.route('/bits/<username>/<bit_id>/comments', methods=['POST'])
def add_comment(username, bit_id):
    comment = request.json['comment']
    c_user = request.json['username']
    timestamp = int(time() * 1000)

    # if comment is None or comment == "":
    #     return {"msg": "Need a comment"}, 400
    # if c_user is None or c_user == "":
    #     return {"msg": "Need a user"}, 400

    # comment_obj = {"comment": comment, "username": c_user, "timestamp": timestamp}

    # comments = db.reference('Comments')
    # try:
    #     comment_ref = comments.child(bit_id).push()
    #     comment_ref.set(comment_obj)
    # except FirebaseError:
    #     return {"msg": "Firebase error"}, 400

    # key = comment_ref.key
    
    # return {"data": {key: comment_obj}}, 200
    return {}

@app.route('/bits/<username>/<bit_id>/comments')
def get_comments(username, bit_id):
    # try:
    #     all_comments = db.reference(f"Comments/{bit_id}").get()
    # except FirebaseError:
    #     return {"msg": f"Failed to get comments for {bit_id}"}, 400
    # return {"data": all_comments}, 200
    return {}

# User routes
@app.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    r_name = request.json['name']
    r_email = request.json['email']
    r_password = request.json['password']
    r_image = request.json['image']


    user = User.objects.filter(username=username)
    if user[0].username == username:
        return {"msg": "pick another username"}, 400
    if user[0].email == r_email:
        return {"msg": "that email already exists"}, 400

    new_user = User(username=username)
    new_user.name = r_name
    new_user.email = r_email
    new_user.password = generate_password_hash(r_password)
    new_user.image = r_image
    
    try:
        new_user.save()
    except ValueError:
        return {"msg": "There was an error in request to db"}, 400
    else:
        return {"msg": "success"}, 201



@app.route('/login', methods=['POST'])
def login():
    r_name = request.json['username']
    r_password = request.json['password']

    try:
        user = User.objects(username=r_name)  
    except:
        return {"msg": "error in request"}, 404
    else:
        if check_password_hash(user[0].password, r_password):
            return {"data":{"username": user[0].username, "email": user[0].email, "image": user[0].image}}
        else:
            return {"msg": "Not found"}, 400



@app.route('/all-users') 
def all_users():
    users = db.reference('Users')
    return {}


if __name__ == "__main__":
    app.run(debug=True, port=PORT)
