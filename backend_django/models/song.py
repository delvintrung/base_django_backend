from mongoengine import Document, StringField, DateTimeField, ObjectIdField, ReferenceField, IntField
from datetime import datetime
from .artist import Artist
class Song(Document):
    meta = {
        'collection': 'songs',
        'strict': False,
        'indexes': [
            'title',
            'artist',
            'albumId',
        ]
    }
    title = StringField(required=True)
    artist = ReferenceField(Artist, required=True)
    albumId = ObjectIdField(required=True)
    duration = IntField(required=True)
    imageUrl = StringField(required=True)   
    audioUrl = StringField(required=True)
    createdAt = DateTimeField(default=datetime.now)
    updatedAt = DateTimeField(default=datetime.now)
    videoUrl = StringField()
 
    def save(self, *args, **kwargs):
        self.updatedAt = datetime.now()
        return super(Song, self).save(*args, **kwargs)
