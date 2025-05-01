import json
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from mongoengine.connection import get_db
import datetime

from ..models.playlist import Playlist
from ..models.song import Song


@csrf_exempt
def get_playlist_by_id(request):
    try:
        clerk_id = request.GET.get('clerkId')
        if not clerk_id:
            return JsonResponse({'error': 'Missing clerk_id'}, status=400)

        playlists = Playlist.objects.filter(clerkId=clerk_id).order_by("-createdAt")
        data = []

        for playlist in playlists:
            # Kiểm tra nếu playlist có songs
            if not playlist.songs:
                continue
            playlist_data = {
                "_id": str(playlist.id),
                "title": playlist.title,
                "avatar": playlist.avatar,
                "clerkId": playlist.clerkId,
                "createdAt": playlist.createdAt.isoformat(),  # Chuyển datetime thành string
                "songs": [] 
            }
            # songs là danh sách các ObjectId, truy vấn các Song tương ứng
            song_ids = playlist.songs  # Danh sách các ObjectId
            songs = Song.objects.filter(id__in=song_ids)  # Truy vấn tất cả Song có id trong song_ids

            for song in songs:
                playlist_data["songs"].append({
                    "_id": str(song.id),  # Chuyển ObjectId thành string
                })

            data.append(playlist_data)

        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
