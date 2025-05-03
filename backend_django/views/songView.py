from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..models.song import Song
from ..models.artist import Artist
from ..models.album import Album
import random
from bson import ObjectId
from datetime import datetime
import json
from mongoengine import Q

def serialize_document(song):
    data = song.to_mongo().to_dict()
    data['_id'] = str(data['_id'])

    # Serialize artist
    if song.artist:
        artist = song.artist.fetch() if hasattr(song.artist, 'fetch') else song.artist
        data['artist'] = {
            "id": str(artist.id),
            "name": artist.name,
            "imageUrl": artist.imageUrl,
            "birthday": artist.birthdate,
            "description": artist.description,
            "followers": artist.followers,
            "listeners": artist.listeners,
            "genres": [str(genre.id) for genre in artist.genres] if artist.genres else [],
        }

    # Serialize albumId (lookup Album từ ObjectId)
    if song.albumId:
        try:
            album = Album.objects.get(id=song.albumId)
            data['albumId'] = {
                "_id": str(album.id),
                "title": album.title,
                "imageUrl": album.imageUrl,
                "releaseYear": album.releaseYear
            }
        except Album.DoesNotExist:
            data['albumId'] = str(song.albumId)

    # ISO format cho datetime
    if 'createdAt' in data and isinstance(data['createdAt'], datetime):
        data['createdAt'] = data['createdAt'].isoformat()
    if 'updatedAt' in data and isinstance(data['updatedAt'], datetime):
        data['updatedAt'] = data['updatedAt'].isoformat()

    return data

@csrf_exempt

def get_all_songs(request): 

    try:
        songs = Song.objects.all()
        songs_data = []
        artist_ids = [str(song.artist.id) for song in songs if song.artist]
        
        artists = Artist.objects(id__in=artist_ids)
        artist_dict = {str(artist.id): artist for artist in artists}

        # Tương tự cho album (nếu cần)
        album_ids = [str(song.albumId.id) for song in songs if song.albumId]
        albums = Album.objects(id__in=album_ids)
        album_dict = {str(album.id): album for album in albums}

        # Xử lý từng bài hát
        for song in songs:
            song_dict = song.to_mongo().to_dict()
            song_dict['_id'] = str(song_dict['_id'])

            # Xử lý trường artist
            if 'artist' in song_dict:
                artist_id = str(song_dict['artist'])
                artist = artist_dict.get(artist_id)
                if artist:
                    song_dict['artist'] = {
                        '_id': str(artist.id),
                        'name': artist.name,
                        'imageUrl': artist.imageUrl,
                        "birthday": artist.birthdate,
                        "description": artist.description,
                        "followers": artist.followers,
                        "listeners": artist.listeners,
                        "genres": [str(genre.id) for genre in artist.genres] if artist.genres else [],
                    }
                else:
                    song_dict['artist'] = {
                        '_id': artist_id,
                        'name': 'Unknown Artist',
                        'imageUrl': ''
                    }

            # Xử lý trường album
            if 'albumId' in song_dict:
                album_id = str(song_dict['albumId'])
                album = album_dict.get(album_id)
                if album:
                    song_dict['albumId'] = {
                        '_id': str(album.id),
                        'title': album.title,
                        'imageUrl': album.imageUrl
                    }
                else:
                    song_dict['albumId'] = {
                        '_id': album_id,
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
        song = Song.objects.get(id=ObjectId(song_id))  # Tìm bài hát theo ObjectId
        song_data = serialize_document(song)  # Chuyển bài hát thành dict JSON-compatible
        return JsonResponse(song_data)  # Trả về JSON response
    except Song.DoesNotExist:
        return JsonResponse({'error': 'Song not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_featured_songs(request):
    try:
        # Lấy tất cả bài hát
        all_songs = list(Song.objects.all())
        
        # Random lấy tối đa 6 bài hát
        sampled_songs = random.sample(all_songs, min(6, len(all_songs)))
        
        # Preload artists và albums để tối ưu truy vấn
        artist_ids = [str(song.artist.id) for song in sampled_songs if song.artist]
        artists = Artist.objects(id__in=artist_ids)
        artist_dict = {str(artist.id): artist for artist in artists}

        album_ids = [str(song.albumId.id) for song in sampled_songs if song.albumId]
        albums = Album.objects(id__in=album_ids)
        album_dict = {str(album.id): album for album in albums}

        # Serialize từng bài hát bằng serialize_document
        result = []
        for song in sampled_songs:
            # Gán artist và albumId từ dictionary preload để serialize_document sử dụng
            song.artist = artist_dict.get(str(song.artist.id)) if song.artist else None
            song.albumId = album_dict.get(str(song.albumId.id)) if song.albumId else None
            song_data = serialize_document(song)
            result.append(song_data)

        return JsonResponse(result, safe=False)
    except Exception as e:
        print("Error in get_featured_songs:", str(e))
        return JsonResponse({'error': str(e)}, status=500)
    
    
@csrf_exempt
def create_song(request):
    try:
        if request.method != 'POST':
            return JsonResponse({'message': 'Method not allowed'}, status=405)

        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST

        title = data.get('title')

        artist_id = data.get('artist')

        albumId = data.get('albumId')
        duration = data.get('duration')
        imageUrl = data.get('imageUrl')
        audioUrl = data.get('audioUrl')

        required_fields = ['title', 'artist', 'albumId', 'duration', 'imageUrl', 'audioUrl']
        missing = [f for f in required_fields if not data.get(f)]
        if missing:
            return JsonResponse({'error': f'Missing fields: {missing}'}, status=400)

        artist = Artist.objects.get(id=ObjectId(artist_id))

        song = Song(
            title=title,

            artist=artist,
            albumId=ObjectId(albumId),
            duration=int(duration),
            imageUrl=imageUrl,
            audioUrl=audioUrl

        )
        song.save()

        return JsonResponse({'message': 'Song created successfully', 'id': str(song.id)}, status=201)


    except Artist.DoesNotExist:
        return JsonResponse({'error': 'Artist not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

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

            song.artist = ObjectId(data['artist'])

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



def get_trending_songs(request):
    try:
        # Lấy tất cả bài hát
        all_songs = list(Song.objects)

        # Random lấy 4 bài hát bất kỳ
        sampled_songs = random.sample(all_songs, min(len(all_songs), 4))

        # Format lại dữ liệu giống như Node.js đang làm
        result = []
        for song in sampled_songs:
            artist = song.artist  # ReferenceField sẽ tự động fetch
            song_data = {
                '_id': str(song.id),  # MongoEngine ObjectId thành string
                'title': song.title,
                'artist': {
                    '_id': str(artist.id) if artist else None,
                    'name': artist.name if artist else None,
                    'imageUrl': artist.imageUrl if artist else None,
                },
                'imageUrl': song.imageUrl,
                'audioUrl': song.audioUrl,
                'videoUrl': getattr(song, 'videoUrl', None),  # Nếu có trường videoUrl
                'description': getattr(song, 'description', None),  # Nếu có trường description
                'followers': getattr(song, 'followers', 0),
                'listeners': getattr(song, 'listeners', 0),
                'premium': getattr(song, 'premium', False),
            }
            result.append(song_data)

        return JsonResponse(result, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
