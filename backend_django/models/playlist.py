from mongoengine import Document, StringField, DateTimeField, EmbeddedDocument, EmbeddedDocumentListField, ObjectIdField, ListField
import datetime

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

    createdAt = StringField(default=lambda: datetime.datetime.utcnow().isoformat())
    updatedAt = StringField(default=lambda: datetime.datetime.utcnow().isoformat())

    def save(self, *args, **kwargs):
        self.updatedAt = datetime.datetime.utcnow().isoformat()
        return super(Playlist, self).save(*args, **kwargs)
