from mongoengine import Document, StringField, DateTimeField, ObjectIdField, ReferenceField, IntField, BooleanField
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
    artist = ReferenceField(Artist, required=False)
    albumId = ObjectIdField(required=False, null=True)
    duration = IntField(required=True)
    imageUrl = StringField(required=True)   
    audioUrl = StringField(required=True)
    createdAt = DateTimeField(default=datetime.now)
    updatedAt = DateTimeField(default=datetime.now)
    lyrics = StringField()
    videoUrl = StringField()
    premium = BooleanField()
 
    def save(self, *args, **kwargs):
        self.updatedAt = datetime.now()
        return super(Song, self).save(*args, **kwargs)
