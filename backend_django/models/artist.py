from mongoengine import Document, StringField, DateTimeField, DateField, ListField, ReferenceField,IntField
import datetime
from .genre import Genre  # Đảm bảo import đúng vị trí file chứa genre

class Artist(Document):
    meta = {
        'collection': 'artists',
        'strict': False
    }

    name = StringField(required=True)
    birthdate = DateField(required=True)
    imageUrl = StringField(required=True)
    genres = ListField(ReferenceField(Genre))
    listeners=IntField(default=0)
    description=StringField(required=True)
    followers=IntField(default=0)
    createdAt = DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = DateTimeField(default=datetime.datetime.utcnow)

    def save(self, *args, **kwargs):
        self.updatedAt = datetime.datetime.utcnow()
        return super(Artist, self).save(*args, **kwargs)
