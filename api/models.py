from django.db import models
from api.config.ObjectId import ObjectIdField


class User(models.Model):
    _id = ObjectIdField(primary_key=True, default=None)
    fullName = models.CharField(max_length=255)
    imageUrl = models.URLField(max_length=500) 
    clerkId = models.CharField(max_length=255, unique=True)
    createdAt = models.DateTimeField() 
    updatedAt = models.DateTimeField()

    def __str__(self):
        return self.fullName
    
    class Meta:
        db_table = "users"

