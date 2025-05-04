from mongoengine import Document, StringField, DateTimeField, EmbeddedDocument, EmbeddedDocumentListField, ObjectIdField, ListField
from datetime import datetime

class Song(EmbeddedDocument):
    _id = ObjectIdField()

class Playlist(Document):
    meta = {
        'collection': 'playlists',
        'strict': False,
    }

    title = StringField(required=True)
    avatar = StringField()
    clerkId = StringField(required=True)
    songs = ListField(ObjectIdField())

    createdAt = DateTimeField(default=datetime.utcnow)
    updatedAt = DateTimeField(default=datetime.utcnow)

    def save(self, *args, **kwargs):
        self.updatedAt = datetime.utcnow()
        return super(Playlist, self).save(*args, **kwargs)
