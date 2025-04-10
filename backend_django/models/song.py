from mongoengine import Document, StringField, ReferenceField, IntField, DateTimeField
import datetime

class Song(Document):
    title = StringField(required=True)
    artist = ReferenceField('Artist', required=True)  # Sử dụng chuỗi cho Artist
    imageUrl = StringField(required=True)
    audioUrl = StringField(required=True)
    duration = IntField(required=True)
    albumId = ReferenceField('Album', required=False)  # Sử dụng chuỗi cho Album

    createdAt = DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = DateTimeField(default=datetime.datetime.utcnow)

    def save(self, *args, **kwargs):
        self.updatedAt = datetime.datetime.utcnow()
        return super(Song, self).save(*args, **kwargs)
