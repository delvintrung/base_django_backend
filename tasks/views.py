
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializer
from pymongo import MongoClient

# Create your views here.
client = MongoClient("mongodb+srv://delvintrung:14032004trung@cluster0.0ftnj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["spotify_clone"]
collection = db["tasks"]

@api_view(["GET"])
def get_tasks(request):
    tasks = list(collection.find({}, {"_id": 0}))  # Ẩn _id nếu không cần
    return Response(tasks)
