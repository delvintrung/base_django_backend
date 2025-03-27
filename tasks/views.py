
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializer
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Create your views here.
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)

db = client["spotify_clone"]
collection = db["tasks"]

@api_view(["GET"])
def get_tasks(request):
    tasks = list(collection.find({}, {"_id": 0}))  # Ẩn _id nếu không cần
    return Response(tasks)
