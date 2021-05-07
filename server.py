import os
from flask import Flask, request, Response, jsonify
from mongoengine import *
from models import User, Bit, Comment
from dotenv import load_dotenv, find_dotenv
from werkzeug.security import check_password_hash, generate_password_hash
import uuid, json


load_dotenv(find_dotenv())

app = Flask(__name__)
app.config.from_object('config.Development')
PORT = os.getenv('PORT')
db_url = os.getenv("DB_URL")
connect(host=db_url)


@app.route('/bits') # http://localhost:4000/bits?user=xxx
def get_bits():
    username = request.args.get('user')
    if username == None:
        bits = Bit.objects.to_json()
        return {"data": json.loads(bits)}
    else:
        user = User.objects.filter(username=username)
        bits = Bit.objects.filter(author=user[0]).to_json()
        return {"data": {"user": json.loads(user[0].to_json()), "bits": json.loads(bits)}}
    

@app.route('/bits', methods=['POST'])
def add_bit():
    bit = request.json['bit']
    r_name = request.json['username']

    if (bit is None or bit == "") or (r_name is None or r_name == ""):
        return {"msg": "missing data in request body"}, 400

    user = User.objects.filter(username=r_name)

    new_bit = Bit(bit=bit)
    new_bit.author = user[0].username
    new_bit.author_image = user[0].image

    try:
        new_bit.save()
    except:
        return {"msg": "failed to add new bit"}, 400
    else:
        return {"msg": "success"}, 201


@app.route('/bit')  # http://localhost:PORT/bit?bitid=xzy123
def get_bit():
    bit_id = request.args.get('bitid')

    if bit_id is not None:
        bit = Bit.objects(id=bit_id)
        if bit is None:
            return {"msg": "Bit does not exist"}, 400
        else:
            user = User.objects(id=bit[0].author.id)
            return {"data": {"bit": json.loads(bit[0].to_json(use_db_field=False)), "user": {"username": user[0].username, "email": user[0].email, "image": user[0].image}}}
    else:
        return {"msg": "missing param args"}, 400


# Comments
@app.route('/bits/<bit_id>/comments', methods=['POST'])
def add_comment(bit_id):
    comment = request.json['comment']
    c_user = request.json['username']

    if comment is None or comment == "":
        return {"msg": "Need a comment"}, 400
    if c_user is None or c_user == "":
        return {"msg": "Need a user"}, 400

    user = User.objects(username=c_user)
    new_comment = Comment(comment=comment, author=user[0])
    bit = Bit.objects(id=bit_id)
    try:
        bit[0].modify(push__comments=new_comment)
        bit[0].reload()      
    except:
        return {"msg": "failed to save comment"}, 400
    else:
        return {"data": {"bit": json.loads(bit[0].to_json())}}


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


@app.route('/user') # http://localhost:4000/user?user=abc123
def get_user():
    user = request.args.get("user")
    if user is None:
        return {"msg": "Missing params"}
    r_user = User.objects.filter(username=user)
    bits = Bit.objects.filter(author=r_user[0].id)
    return {"data": {"user": {"username": r_user[0].username, "email": r_user[0].email, "image": r_user[0].image}, "bits": json.loads(bits.to_json())}}
    

@app.route('/all-users') 
def all_users():
    users = User.objects.to_json()
    # return without passwords
    return jsonify({"data": json.loads(users)})


if __name__ == "__main__":
    app.run(debug=True, port=PORT)
