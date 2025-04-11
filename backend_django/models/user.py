from mongoengine import Document, StringField, DateTimeField
import datetime

class User(Document):
    meta = {
        'collection': 'users',
        'strict': False,  # Cho phép thêm các field không khai báo nếu cần
        'indexes': [
            {'fields': ['clerkId'], 'unique': True}
        ]
    }

    fullName = StringField(required=True)
    imageUrl = StringField(required=True)
    clerkId = StringField(required=True, unique=True)
    createdAt = DateTimeField(default=datetime.datetime.utcnow)
    updatedAt = DateTimeField(default=datetime.datetime.utcnow)

    def save(self, *args, **kwargs):
        """Tự động cập nhật updatedAt mỗi lần save."""
        self.updatedAt = datetime.datetime.utcnow()
        return super(User, self).save(*args, **kwargs)
