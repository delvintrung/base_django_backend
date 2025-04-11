from mongoengine import Document, StringField, IntField, ListField, ReferenceField, DateTimeField
import datetime
from .song import Song  # đảm bảo bạn đã có model Song

class Album(Document):
    meta = {
        'collection': 'album',
        'indexes': ['title', 'releaseYear'],
        'ordering': ['-createdAt']
    }

    title = StringField(required=True)
    artist = StringField(required=True)
    imageUrl = StringField(required=True)
    releaseYear = IntField(required=True)
    songs = ListField(ReferenceField('Song'))  # Dùng string thay vì import Song

    createdAt = DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = DateTimeField(default=datetime.datetime.utcnow)

    def save(self, *args, **kwargs):
        self.updatedAt = datetime.datetime.utcnow()
        return super(Album, self).save(*args, **kwargs)
