import json
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from mongoengine.connection import get_db
import datetime
from bson.objectid import ObjectId

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
@csrf_exempt
def create_playlist(request):
    try:
        data = json.loads(request.body)
        title = data.get('title')
        avatar = data.get('avatar')
        clerk_id = data.get('clerkId')
        songs = data.get('songs')

        playlist = Playlist(
            title=title,
            avatar=avatar,
            clerkId=clerk_id,
            songs=songs
        )
        playlist.save()

        return JsonResponse(serialize_playlist(playlist), status=201)
    except Exception as e:  
        return JsonResponse({'error': str(e)}, status=500)
@csrf_exempt
def update_playlist(request, playlist_id):
    try:
        data = json.loads(request.body)
        title = data.get('title')
        avatar = data.get('avatar')
        songs = data.get('songs')

        playlist = Playlist.objects.get(id=playlist_id)
        playlist.title = title
        playlist.avatar = avatar
        playlist.songs = songs
        playlist.save()

        return JsonResponse(serialize_playlist(playlist), status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)  
@csrf_exempt
def add_song_to_playlist(request, playlist_id):
    try:
        data = json.loads(request.body)
        song_id = data.get('songId')
        
        if not song_id:
            return JsonResponse({'error': 'Missing songId'}, status=400)
            
        try:
            # Chuyển đổi song_id thành ObjectId
            song_object_id = ObjectId(song_id)
        except Exception as e:
            return JsonResponse({'error': 'Invalid songId format'}, status=400)
            
        # Kiểm tra xem bài hát có tồn tại không
        song = Song.objects(id=song_object_id).first()
        if not song:
            return JsonResponse({'error': 'Song not found'}, status=404)
            
        playlist = Playlist.objects(id=playlist_id).first()
        if not playlist:
            return JsonResponse({'error': 'Playlist not found'}, status=404)
            
        # Kiểm tra xem bài hát đã có trong playlist chưa
        if song_object_id in playlist.songs:
            return JsonResponse({'error': 'Song already in playlist'}, status=400)
            
        playlist.songs.append(song_object_id)
        playlist.save()
        
        return JsonResponse(serialize_playlist(playlist), status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)  
@csrf_exempt
def get_playlist(request, playlist_id):
    try:
        playlist = Playlist.objects.get(id=playlist_id)
        return JsonResponse(serialize_playlist(playlist), status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
@csrf_exempt
def get_all_playlist(request):
    try:
        playlists = Playlist.objects.all()
        data = []
        for playlist in playlists:
            data.append(serialize_playlist(playlist))
        return JsonResponse(data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
def serialize_playlist(playlist):
    return {
        "_id": str(playlist.id),
        "title": playlist.title,
        "avatar": playlist.avatar,
        "clerkId": playlist.clerkId,    
        "songs": [str(song_id) for song_id in playlist.songs]  # Chuyển đổi ObjectId thành string
    }
def serialize_song(song):
    return {
        "_id": str(song.id),
        "title": song.title,    
        "artist": song.artist,
        "album": song.album,
        "duration": song.duration,
        "imageUrl": song.imageUrl,
        "audioUrl": song.audioUrl,
        "lyrics": song.lyrics
    }   
