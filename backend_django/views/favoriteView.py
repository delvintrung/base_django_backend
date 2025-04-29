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
        clerk_id = request.GET.get("clerkId")
        song_id = request.GET.get("songId")

        if not clerk_id or not song_id:
            return Response({'error': 'Missing clerkId or songId'}, status=400)

        favorite = Favorite.objects(clerkId=clerk_id, songId=song_id).first()
        if not favorite:
            return Response({'error': 'Favorite not found'}, status=404)

        favorite.delete()
        return Response({'message': 'Favorite removed'}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def get_featured_songs(request):
    try:
        db = get_db()
        pipeline = [
            {"$sample": {"size": 6}},
            {
                "$lookup": {
                    "from": "artist",
                    "localField": "artist",
                    "foreignField": "_id",
                    "as": "artist"
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "title": 1,
                    "imageUrl": 1,
                    "audioUrl": 1,
                    "artist": {"$arrayElemAt": ["$artist", 0]}
                }
            }
        ]

        songs = list(db.songs.aggregate(pipeline))

        for song in songs:
            song["_id"] = str(song["_id"])
            if "artist" in song and song["artist"]:
                song["artist"]["_id"] = str(song["artist"]["_id"])
                if "birthdate" in song["artist"]:
                    song["artist"]["birthdate"] = song["artist"]["birthdate"].isoformat()

        return Response(songs)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def get_made_for_you_songs(request):
    try:
        db = get_db()
        pipeline = [
            {"$sample": {"size": 4}},
            {
                "$lookup": {
                    "from": "artist",
                    "localField": "artist",
                    "foreignField": "_id",
                    "as": "artist"
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "title": 1,
                    "imageUrl": 1,
                    "audioUrl": 1,
                    "artist": {"$arrayElemAt": ["$artist", 0]}
                }
            }
        ]

        songs = list(db.songs.aggregate(pipeline))

        for song in songs:
            song["_id"] = str(song["_id"])
            if "artist" in song and song["artist"]:
                song["artist"]["_id"] = str(song["artist"]["_id"])
                if "birthdate" in song["artist"]:
                    song["artist"]["birthdate"] = song["artist"]["birthdate"].isoformat()

        return Response(songs)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
def create_artist(request):
    try:
        name = request.data.get('name')
        birthdate = request.data.get('birthdate')
        image_file = request.FILES.get('imageFile')

        if not name or not birthdate or not image_file:
            return Response({'error': 'Please upload all required fields'}, status=400)

        # 👇 Upload ảnh lên Cloudinary hoặc nơi khác
        # upload_result = config(image_file)
        # image_url = upload_result.get('secure_url')

        # 👇 Parse birthdate string (yyyy-mm-dd) thành datetime.date
        # parsed_birthdate = datetime.datetime.strptime(birthdate, "%Y-%m-%d").date()

        # 👇 Tạo artist mới
        # artist = Artist(
        #     name=name,
        #     birthdate=parsed_birthdate,
        #     imageUrl=image_url,
        # )
        # artist.save()

        # return Response({
        #     '_id': str(artist.id),
        #     'name': artist.name,
        #     'birthdate': artist.birthdate.isoformat(),
        #     'imageUrl': artist.imageUrl,
        # }, status=201)

        return Response({'message': 'Artist created (dummy)'})
    except Exception as e:
        print("❌ Error in create_artist:", e)
        return Response({'error': str(e)}, status=500)
