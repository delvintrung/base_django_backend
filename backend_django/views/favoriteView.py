# views/favorite_views.py
import json
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from mongoengine.connection import get_db
import datetime

from ..models.favorite import Favorite
from ..models.song import Song
from ..models.artist import Artist

@csrf_exempt
def get_favorite_by_id(request):
    try:
        user_id = request.GET.get('userId') or request.GET.get('clerkId')
        if not user_id:
            return JsonResponse({'error': 'Missing userId'}, status=400)

        favorites = Favorite.objects(clerkId=user_id).order_by("-createdAt").select_related()
        data = []

        for fav in favorites:
            song = fav.songId
            if not song:
                continue

            song_data = song.to_mongo().to_dict()
            data.append({
                "_id": str(fav.id),
                "clerkId": fav.clerkId,
                "createdAt": fav.createdAt.isoformat(),
                "updatedAt": fav.updatedAt.isoformat(),
                "songId": {
                    "_id": str(song.id),
                    "title": song_data.get("title"),
                    "artist": None,
                    "imageUrl": song_data.get("imageUrl"),
                    "audioUrl": song_data.get("audioUrl")
                }
            })
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def add_to_favorite(request):
    try:
        if request.method != "POST":
            return JsonResponse({'error': 'Method not allowed'}, status=405)

        body = json.loads(request.body)
        clerk_id = body.get('clerkId')
        song_id = body.get('songId')

        if not clerk_id or not song_id:
            return JsonResponse({'error': 'Missing clerkId or songId'}, status=400)

        existed = Favorite.objects(clerkId=clerk_id, songId=song_id).first()
        if existed:
            return JsonResponse({'message': 'Song already in favorites'}, status=400)

        favorite = Favorite(clerkId=clerk_id, songId=song_id)
        favorite.save()

        song = favorite.songId
        song_data = song.to_mongo().to_dict()

        return JsonResponse({
            "_id": str(favorite.id),
            "clerkId": favorite.clerkId,
            "createdAt": favorite.createdAt.isoformat(),
            "updatedAt": favorite.updatedAt.isoformat(),
            "songId": {
                "_id": str(song.id),
                "title": song_data.get("title"),
                "artist": None,
                "imageUrl": song_data.get("imageUrl"),
                "audioUrl": song_data.get("audioUrl")
            }
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def remove_favorite(request):
    try:
        if request.method != "DELETE":
            return JsonResponse({'error': 'Method not allowed'}, status=405)

        clerk_id = request.GET.get("clerkId")
        song_id = request.GET.get("songId")

        if not clerk_id or not song_id:
            return JsonResponse({'error': 'Missing clerkId or songId'}, status=400)

        favorite = Favorite.objects(clerkId=clerk_id, songId=song_id).first()
        if not favorite:
            return JsonResponse({'error': 'Favorite not found'}, status=404)

        favorite.delete()
        return JsonResponse({'message': 'Favorite removed'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
       
    