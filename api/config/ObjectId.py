from bson import ObjectId
from django.db import models

class ObjectIdField(models.Field):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 24  
        super().__init__(*args, **kwargs)

    def db_type(self, connection):
        return 'objectid' 

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return str(value)  

    def to_python(self, value):
        if isinstance(value, ObjectId):
            return str(value)
        return value

    def get_prep_value(self, value):
        if value is None:
            return value
        return ObjectId(value)