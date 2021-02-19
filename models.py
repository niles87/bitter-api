from mongoengine import *
from datetime import datetime

class User(Document):
    username = StringField(max_length=20, required=True)
    email = StringField(max_length=50, required=True)
    password = StringField(required=True)
    image = StringField(required=True)
    name = StringField(max_length=50, required=True)
    profile_desc = StringField(max_length=200)


class Comment(EmbeddedDocument):
    comment = StringField(required=True, max_length=150)
    author = ReferenceField(User)
    date_time = DateTimeField(default=datetime.utcnow)

  
class Bit(Document):
    author = ReferenceField(User, reverse_delete_rule=CASCADE, required=True)
    bit = StringField(required=True, max_length=240)
    date_time = DateTimeField(default=datetime.utcnow)
    comments = ListField(EmbeddedDocumentField(Comment))
