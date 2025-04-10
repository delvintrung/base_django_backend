from mongoengine import Document, StringField, DateTimeField, DateField, ListField, ReferenceField
import datetime
from .genre import Genre  # Đảm bảo import đúng vị trí file chứa genre

class Artist(Document):
    meta = {
        'collection': 'artist',
        'strict': False
    }

    name = StringField(required=True)
    birthdate = DateField(required=True)
    imageUrl = StringField(required=True)
    genres = ListField(ReferenceField(Genre))
    createdAt = DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = DateTimeField(default=datetime.datetime.utcnow)

    def save(self, *args, **kwargs):
        self.updatedAt = datetime.datetime.utcnow()
        return super(Artist, self).save(*args, **kwargs)
