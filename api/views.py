
from .models import User
from .serializers import UserSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from pymongo import MongoClient
import os

@api_view(['GET'])
def user_list(request):
    if request.method == 'GET':
        try:
            client = MongoClient(os.getenv("MONGO_URI"))
            db = client['spotify_clone']
            users_collection = db['users']
            users = list(users_collection.find()) 
            users = [{**user, '_id': str(user['_id'])} for user in users]
            return Response({"message": "Danh sách user", "data": users}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": f"Lỗi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
