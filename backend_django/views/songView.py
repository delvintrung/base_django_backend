from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..models.song import Song
from ..models.artist import Artist
from ..models.album import Album
import random
from bson import ObjectId
from datetime import datetime
import json

def serialize_document(song):
    data = song.to_mongo().to_dict()
    data['_id'] = str(data['_id'])

    # Serialize artist
    if song.artist:
        artist = song.artist.fetch() if hasattr(song.artist, 'fetch') else song.artist
        data['artist'] = {
            "id": str(artist.id),
            "name": artist.name,
            "imageUrl": artist.imageUrl
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


