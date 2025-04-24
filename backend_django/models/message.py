from mongoengine import Document, StringField, DateTimeField
import datetime

class Message(Document):
    senderId = StringField(required=True)      # Clerk user ID
    receiverId = StringField(required=True)    # Clerk user ID
    content = StringField(required=True)
    createdAt = DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'message',  # Trỏ tới đúng collection trong MongoDB
        'ordering': ['createdAt']
    }
