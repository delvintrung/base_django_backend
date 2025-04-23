from mongoengine import Document, StringField, DateTimeField, BooleanField, IntField
import datetime

class Genre(Document):
    meta = {
        'collection': 'genres',
        'strict': False
    }

    name = StringField(required=True)
    description = StringField(required=True)
    coverImage = StringField(required=True)  # Thay cho imageUrl
    isActive = BooleanField(default=True)  # Trường isActive
    songCount = IntField(default=0)  # Trường songCount
    createdAt = DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = DateTimeField(default=datetime.datetime.utcnow)

    def save(self, *args, **kwargs):
        self.updatedAt = datetime.datetime.utcnow()
        return super(Genre, self).save(*args, **kwargs)
