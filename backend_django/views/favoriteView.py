from django.http import JsonResponse
from ..models.favorite import Favorite
from ..models.song import Song
from mongoengine.queryset.visitor import Q
import random

def get_favorite_by_id(request):
    try:
        user_id = request.GET.get("userId")
        favorites = Favorite.objects(clerkId=user_id).order_by("-createdAt").select_related()

        data = []
        for fav in favorites:
            data.append(fav.to_mongo().to_dict())

        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_featured_songs(request):
    try:
        all_songs = list(Song.objects.select_related())  # Lấy toàn bộ bài hát
        songs_sample = random.sample(all_songs, min(len(all_songs), 6))  # Lấy 6 bài random

        data = []
        for song in songs_sample:
            s_dict = song.to_mongo().to_dict()
            if song.artist:
                s_dict['artist'] = song.artist.to_mongo().to_dict()
            data.append({
                "_id": str(s_dict["_id"]),
                "title": s_dict.get("title"),
                "artist": s_dict.get("artist"),
                "imageUrl": s_dict.get("imageUrl"),
                "audioUrl": s_dict.get("audioUrl")
            })
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_made_for_you_songs(request):
    try:
        all_songs = list(Song.objects.select_related())
        songs_sample = random.sample(all_songs, min(len(all_songs), 4))

        data = []
        for song in songs_sample:
            s_dict = song.to_mongo().to_dict()
            if song.artist:
                s_dict['artist'] = song.artist.to_mongo().to_dict()
            data.append({
                "_id": str(s_dict["_id"]),
                "title": s_dict.get("title"),
                "artist": s_dict.get("artist"),
                "imageUrl": s_dict.get("imageUrl"),
                "audioUrl": s_dict.get("audioUrl")
            })
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
