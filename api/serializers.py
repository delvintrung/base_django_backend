from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["_id", "fullName", "imageUrl", "clerkId", "createdAt", "updatedAt"]
