from mongoengine import Document, StringField, DateField, ListField, ReferenceField
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
    genres = ListField(ReferenceField(Genre))  # Trường genres lưu các ObjectId của Genre

    def save(self, *args, **kwargs):
        # Nếu bạn muốn tự động cập nhật thời gian khi đối tượng được chỉnh sửa, thêm dòng này:
        return super(Artist, self).save(*args, **kwargs)
