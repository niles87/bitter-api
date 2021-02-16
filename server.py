import os
from flask import Flask, request, Response, jsonify
from firebase_admin import credentials, db, initialize_app
from dotenv import load_dotenv, find_dotenv
from werkzeug.security import check_password_hash, generate_password_hash
from time import time
import uuid


load_dotenv(find_dotenv())

cred = credentials.Certificate(os.getenv("GOOGLE_CREDENTIALS"))
db_url = os.getenv("DB_URL")
initialize_app(cred, {
    'databaseURL': db_url
})

app = Flask(__name__)
app.config.from_object('config.Development')
PORT = os.getenv('PORT')

def get_all():
    all_bits = db.reference("Bits").get()
    return all_bits


@app.route('/bits') # http://localhost:4000/bits?user=xxx
def get_bits():
    username = request.args.get('user')
    if username == None:
        try:
            all_bits = get_all()
        except FirebaseError:
            return {"msg": "Firebase error"}, 400
        return {"data": all_bits}, 200
    else:
        try:
            all_bits = get_all()
        except FirebaseError:
            return {"msg":"Firebase error"}, 400
        bits_list = []
        for key, value in all_bits.items():
            if value['username'] == username:
                bits_list.append({key: value})
        return {"data": bits_list}, 200
    

@app.route('/bits', methods=['POST'])
def add_bit():
    bit = request.json['bit']
    r_name = request.json['username']
    timestamp = int(time() * 1000)

    if (bit is None or bit == "") or (r_name is None or r_name == ""):
        return {"msg": "missing data in request body"}, 400

    new_bit = {}
    new_bit['username'] = r_name
    new_bit['bit'] = bit
    new_bit['timestamp'] = timestamp
    new_bit['comments'] = 0
    
    bits = db.reference('Bits')

    try:
        new_bit_ref = bits.push()
        new_bit_ref.set(new_bit)
    except FirebaseError:
        return {"msg": "Firebase error"}, 400
        
    key = new_bit_ref.key
    return {"data":{ key: new_bit}}, 200


@app.route('/bit')  # http://localhost:PORT/bit?bitid=xzy123
def get_bit():
    bit_id = request.args.get('bitid')

    all_bits = get_all()

    if bit_id is not None:
        if bit_id in all_bits:
            return {"data": {bit_id: all_bits[bit_id]}}
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

    if comment is None or comment == "":
        return {"msg": "Need a comment"}, 400
    if c_user is None or c_user == "":
        return {"msg": "Need a user"}, 400

    comment_obj = {"comment": comment, "username": c_user, "timestamp": timestamp}

    comments = db.reference('Comments')
    try:
        comment_ref = comments.child(bit_id).push()
        comment_ref.set(comment_obj)
    except FirebaseError:
        return {"msg": "Firebase error"}, 400

    key = comment_ref.key
    
    return {"data": {key: comment_obj}}, 200

@app.route('/bits/<username>/<bit_id>/comments')
def get_comments(username, bit_id):
    try:
        all_comments = db.reference(f"Comments/{bit_id}").get()
    except FirebaseError:
        return {"msg": f"Failed to get comments for {bit_id}"}, 400
    return {"data": all_comments}, 200

# User routes
@app.route('/register', methods=['POST'])
def register():
    id = str(uuid.uuid4())
    username = request.json['username']
    r_name = request.json['name']
    r_email = request.json['email']
    r_password = request.json['password']
    r_image = request.json['image']
    friends = []

    try:
        existing_users = db.reference('Users').get()
    except FirebaseError:
        return {"msg": "There was an error in get request to db"}, 400
    if username in existing_users:
        return {"msg": "pick another username"}
    
    new_user = {}
    new_user["name"] = r_name
    new_user["id"] = id
    new_user["email"] = r_email
    new_user["password"] = generate_password_hash(r_password)
    new_user["friends"] = friends
    new_user["image"] = r_image

    try:
        db.reference('Users').child(username).set(new_user)
    except FirebaseError:
        return {"msg": "There was an error in request to db"}, 400
    else:
        return {"msg": "success"}, 201


@app.route('/login', methods=['POST'])
def login():
    r_name = request.json['username']
    r_password = request.json['password']
    username_str = 'Users/{}'.format(r_name)
    
    try:
        user = db.reference(username_str).get()
    except FirebaseError:
        return {"msg": "Error in query"}, 400
    else:
        if check_password_hash(user['password'], r_password):
            r_user = {
                "email": user['email'],
                "id": user['id'],
                "name": user['name']
            }
            return {"data": r_user}, 200
        else:
            return {"msg": "That password wasn't correct"}, 401


@app.route('/all-users') 
def all_users():
    users = db.reference('Users')
    try:
        users_ref = users.get()
    except FirebaseError:
        return {"msg": "Failed to get users"}, 400
    user_list = []
    for user, details in users_ref.items():
        user_list.append({user: {
            "email": details['email'],
            "id": details['id'],
            "name": details['name']
        }})
    return {"data": user_list}, 200


if __name__ == "__main__":
    app.run(debug=True, port=PORT)
