from mongoengine import Document, StringField, ReferenceField, DateTimeField
import datetime
from .song import Song  # hoặc từ đúng vị trí import nếu Song nằm nơi khác

class Favorite(Document):
    meta = {
        'collection': 'favorite_songs',
        'strict': False,
    }

    clerkId = StringField(required=True)
    songId = ReferenceField(Song, required=True)
    createdAt = DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = DateTimeField(default=datetime.datetime.utcnow)

    def save(self, *args, **kwargs):
        self.updatedAt = datetime.datetime.utcnow()
        return super(Favorite, self).save(*args, **kwargs)
