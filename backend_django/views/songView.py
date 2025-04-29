from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..models.song import Song
from ..models.artist import Artist
import random
from bson import ObjectId
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from pymongo import MongoClient
import os

def serialize_document(doc):
    """Chuyển đổi Document MongoEngine sang dict và ép _id thành string"""
    d = doc.to_mongo().to_dict()
    if '_id' in d:
        d['_id'] = str(d['_id'])
    return d    

@csrf_exempt
def get_all_songs(request): 
    try:
        songs = Song.objects.all()
        songs_data = []
        for song in songs:
            song_dict = song.to_mongo().to_dict()
            # Chuyển đổi _id thành string
            song_dict['_id'] = str(song_dict['_id'])
            
            # Xử lý trường artist
            if 'artist' in song_dict:
                try:
                    artist = song.artist.fetch()
                    song_dict['artist'] = {
                        '_id': str(artist.id),
                        'name': artist.name,
                        'imageUrl': artist.imageUrl
                    }
                except:
                    song_dict['artist'] = {
                        '_id': str(song_dict['artist']),
                        'name': 'Unknown Artist',
                        'imageUrl': ''
                    }
            
            # Xử lý trường album
            if 'albumId' in song_dict:
                try:
                    album = song.albumId.fetch()
                    song_dict['albumId'] = {
                        '_id': str(album.id),
                        'title': album.title,
                        'imageUrl': album.imageUrl
                    }
                except:
                    song_dict['albumId'] = {
                        '_id': str(song_dict['albumId']),
                        'title': 'Unknown Album',
                        'imageUrl': ''
                    }
            
            songs_data.append(song_dict)
        return JsonResponse(songs_data, safe=False) 
    except Exception as e:
        print("Error in get_all_songs:", str(e))
        return JsonResponse({'error': str(e)}, status=500)



@csrf_exempt
def get_song(request, song_id):
    try:
        song = Song.objects.get(id=ObjectId(song_id))
        song_data = serialize_document(song)
        return JsonResponse(song_data)
    except Song.DoesNotExist:
        return JsonResponse({'error': 'Song not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_featured_songs(request):
    try:
        all_songs = list(Song.objects.all())
        sampled_songs = random.sample(all_songs, min(6, len(all_songs)))

        result = []
        for song in sampled_songs:
            artist = song.artist.fetch() if song.artist else None
            album = song.albumId.fetch() if song.albumId else None
            result.append({
                "_id": str(song.id),
                "title": song.title,
                "artist": serialize_document(artist) if artist else None,
                "albumId": serialize_document(album) if album else None,          
                "imageUrl": song.imageUrl,
                "audioUrl": song.audioUrl,
                "duration": song.duration,
            })

        return JsonResponse(result, safe=False) 
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def create_song(request):
    try:
        if request.method != 'POST':
            return JsonResponse({'message': 'Method not allowed'}, status=405)

        data = request.POST
        title = data.get('title')
        artist = data.get('artist') 
        albumId = data.get('albumId')
        duration = data.get('duration') 
        imageUrl = data.get('imageUrl')
        audioUrl = data.get('audioUrl')

        song = Song(
            title=title,
            artist=Artist.objects.get(id=ObjectId(artist)),
            albumId=ObjectId(albumId),
            duration=duration,
            imageUrl=imageUrl,
            audioUrl=audioUrl,
            createdAt=datetime.now(),
            updatedAt=datetime.now()    
        )
        song.save()

        return JsonResponse({'message': 'Song created successfully', 'id': str(song.id)}, status=201)
    except Artist.DoesNotExist:
        return JsonResponse({'error': 'Artist not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_songs_by_artist(request, artist_id):
    try:
        artist = Artist.objects.get(id=ObjectId(artist_id))
        songs = Song.objects.filter(artist=artist)
        songs_data = [serialize_document(s) for s in songs]
        return JsonResponse(songs_data, safe=False)
    except Artist.DoesNotExist:
        return JsonResponse({'error': 'Artist not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def search_songs(request):
    try:
        query = request.GET.get('q', '')
        if not query:
            return JsonResponse([], safe=False)

        songs = Song.objects.filter(title__icontains=query)
        songs_data = [serialize_document(s) for s in songs]
        return JsonResponse(songs_data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def update_song(request, song_id):
    try:
        if request.method != 'PUT': 
            return JsonResponse({'message': 'Method not allowed'}, status=405)

        song = Song.objects.get(id=ObjectId(song_id))
        data = request.POST

        if 'title' in data:
            song.title = data['title']
        if 'artist' in data:
            song.artist = Artist.objects.get(id=ObjectId(data['artist']))
        if 'albumId' in data:
            song.albumId = ObjectId(data['albumId'])
        if 'duration' in data:
            song.duration = data['duration']
        if 'imageUrl' in data:
            song.imageUrl = data['imageUrl']
        if 'audioUrl' in data:
            song.audioUrl = data['audioUrl']
        if 'createdAt' in data:
            song.createdAt = data['createdAt']
        if 'updatedAt' in data:
            song.updatedAt = data['updatedAt']
   

        song.save()
        return JsonResponse({'message': 'Song updated successfully'})
    except Song.DoesNotExist:
        return JsonResponse({'error': 'Song not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def delete_song(request, song_id):
    try:
        if request.method != 'DELETE':
            return JsonResponse({'message': 'Method not allowed'}, status=405)

        song = Song.objects.get(id=ObjectId(song_id))
        song.delete()
        return JsonResponse({'message': 'Song deleted successfully'})
    except Song.DoesNotExist:
        return JsonResponse({'error': 'Song not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def create_sample_songs(request):
    try:
        # Tạo một số bài hát mẫu
        sample_songs = [
            {
                'title': 'Song 1',
                'artist': 'Artist 1',
                'album': 'Album 1',
                'duration': 180,
                'imageUrl': 'https://example.com/song1.jpg',
                'audioUrl': 'https://example.com/song1.mp3',
                'createdAt': datetime.now(),
                'updatedAt': datetime.now()
            },
            {
                'title': 'Song 2',
                'artist': 'Artist 2',
                'albumId': 'Album 2',
                'duration': 240,
                'imageUrl': 'https://example.com/song2.jpg',
                'audioUrl': 'https://example.com/song2.mp3',
                'createdAt': datetime.now(),
                'updatedAt': datetime.now()
            }
        ]
        
        for song_data in sample_songs:
            song = Song(**song_data)
            song.save()
            
        return JsonResponse({'message': 'Sample songs created successfully'}, status=201)
    except Exception as e:
        print("Error in create_sample_songs:", str(e))
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['PUT'])
def update_song(request, song_id):
    try:
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client['spotify']
        songs_collection = db['songs']
        
        update_data = request.data
        result = songs_collection.update_one(
            {"_id": song_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return Response({"message": "Cập nhật bài hát thành công"}, status=status.HTTP_200_OK)
        return Response({"message": "Không tìm thấy bài hát"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def search_songs(request):
    try:
        query = request.GET.get('q', '')
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client['spotify']
        songs_collection = db['songs']
        
        songs = songs_collection.find({
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"artist": {"$regex": query, "$options": "i"}},
                {"album": {"$regex": query, "$options": "i"}}
            ]
        })
        
        return Response(list(songs), status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_songs_by_artist(request, artist_id):
    try:
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client['spotify']
        songs_collection = db['songs']
        
        songs = songs_collection.find({"artist_id": artist_id})
        return Response(list(songs), status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_songs_by_genre(request, genre):
    try:
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client['spotify']
        songs_collection = db['songs']
        
        songs = songs_collection.find({"genre": genre})
        return Response(list(songs), status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_recently_played(request):
    try:
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client['spotify']
        history_collection = db['play_history']
        
        # Lấy lịch sử phát nhạc của người dùng hiện tại
        history = history_collection.find(
            {"user_id": request.user_info.get('sub')}
        ).sort("played_at", -1).limit(20)
        
        return Response(list(history), status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def like_song(request, song_id):
    try:
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client['spotify']
        likes_collection = db['likes']
        
        likes_collection.insert_one({
            "user_id": request.user_info.get('sub'),
            "song_id": song_id,
            "created_at": datetime.utcnow()
        })
        
        return Response({"message": "Đã thích bài hát"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def unlike_song(request, song_id):
    try:
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client['spotify']
        likes_collection = db['likes']
        
        result = likes_collection.delete_one({
            "user_id": request.user_info.get('sub'),
            "song_id": song_id
        })
        
        if result.deleted_count > 0:
            return Response({"message": "Đã bỏ thích bài hát"}, status=status.HTTP_200_OK)
        return Response({"message": "Không tìm thấy lượt thích"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 