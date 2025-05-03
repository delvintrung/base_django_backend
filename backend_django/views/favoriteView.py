# views/favorite_views.py
import json
import random
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from mongoengine.connection import get_db
import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from ..models.favorite import Favorite
from ..models.song import Song
from ..models.artist import Artist

@api_view(['GET'])
@permission_classes([AllowAny])
def get_favorite_by_id(request):
    try:
        user_id = request.GET.get('clerkId')
        if not user_id:
            return Response({'error': 'Missing userId'}, status=400)

        favorites = Favorite.objects(clerkId=user_id).order_by("-createdAt").select_related()
        data = []

        for fav in favorites:
            song = fav.songId
            if not song:
                continue

            song_data = song.to_mongo().to_dict()
            artist = song.artist 
            artist_data = None
            if artist:
                artist_data = {
                    "_id": str(artist.id),
                    "name": artist.name,
                    "imageUrl": artist.imageUrl,
                    "createdAt": artist.createdAt.isoformat(),
                    "updatedAt": artist.updatedAt.isoformat(),
                }
            data.append({
                "_id": str(fav.id),
                "clerkId": fav.clerkId,
                "createdAt": fav.createdAt.isoformat(),
                "updatedAt": fav.updatedAt.isoformat(),
                "songId": {
                    "_id": str(song.id),
                    "title": song_data.get("title"),
                    "artist": artist_data,
                    "imageUrl": song_data.get("imageUrl"),
                    "audioUrl": song_data.get("audioUrl"),
                    "duration": song_data.get("duration"),
                    "albumId": song_data.get("albumId"),
                }
            })
        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
def add_to_favorite(request):
    try:
        body = request.data
        clerk_id = body.get('clerkId')
        song_id = body.get('songId')

        if not clerk_id or not song_id:
            return Response({'error': 'Missing clerkId or songId'}, status=400)

        existed = Favorite.objects(clerkId=clerk_id, songId=song_id).first()
        if existed:
            return Response({'message': 'Song already in favorites'}, status=400)

        favorite = Favorite(clerkId=clerk_id, songId=song_id)
        favorite.save()

        song = favorite.songId
        song_data = song.to_mongo().to_dict()

        return Response({
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
        return Response({'error': str(e)}, status=500)

@api_view(['DELETE'])
def remove_favorite(request):
    try:
        data = json.loads(request.body)
        clerk_id = data.get("clerkId")
        song_id = data.get("songId")


        if not clerk_id or not song_id:
            return Response({'error': 'Missing clerkId or songId'}, status=400)

        favorite = Favorite.objects(clerkId=clerk_id, songId=song_id).first()
        if not favorite:
            return Response({'error': 'Favorite not found'}, status=404)

        favorite.delete()
        return Response({'message': 'Favorite removed'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
       
    