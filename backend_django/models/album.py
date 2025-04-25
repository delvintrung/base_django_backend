from mongoengine import Document, StringField, DateTimeField, DateField, ListField, ReferenceField, IntField
import datetime
from .artist import Artist  
from .song import Song
class Album(Document):
    meta = {
        'collection': 'albums',
        'strict': False,
        'indexes': [
            'title',
            'artist',
            'releaseYear'
        ]
    }

    title = StringField(required=True)
    artist = ReferenceField(Artist, required=True)
    imageUrl = StringField(required=True)
    releaseYear = IntField(required=True)
    songs = ListField(ReferenceField(Song))   

    createdAt = DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = DateTimeField(default=datetime.datetime.utcnow)

    def save(self, *args, **kwargs):
        self.updatedAt = datetime.datetime.utcnow()
        return super(Album, self).save(*args, **kwargs)
