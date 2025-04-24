from mongoengine import Document, StringField, DateTimeField
import datetime

class Genre(Document):
    meta = {
        'collection': 'genre',
        'strict': False
    }

    name = StringField(required=True)
    description = StringField(required=True)
    imageUrl = StringField(required=True)
    createdAt = DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = DateTimeField(default=datetime.datetime.utcnow)

    def save(self, *args, **kwargs):
        self.updatedAt = datetime.datetime.utcnow()
        return super(Genre, self).save(*args, **kwargs)
