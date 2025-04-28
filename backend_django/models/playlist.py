from mongoengine import Document, StringField, ListField, ReferenceField
import datetime

class Playlist(Document):
    meta = {
        'collection': 'playlists',
        'strict': False,
    }

    title = StringField(required=True)
    avatar = StringField()
    clerkId = StringField(required=True)
    songs = ListField(ReferenceField('Song'))

    createdAt = StringField(default=lambda: datetime.datetime.utcnow().isoformat())
    updatedAt = StringField(default=lambda: datetime.datetime.utcnow().isoformat())

    def save(self, *args, **kwargs):
        self.updatedAt = datetime.datetime.utcnow().isoformat()
        return super(Playlist, self).save(*args, **kwargs)
