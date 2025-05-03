import json
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from mongoengine.connection import get_db
import datetime
from bson import ObjectId
from bson.errors import InvalidId

from ..models.playlist import Playlist
from ..models.song import Song
from ..models.artist import Artist
from ..models.album import Album
from ..models.genre import Genre

from mongoengine import DoesNotExist



@csrf_exempt
def get_playlist_by_clerki_id(request):
    try:
        print(request.auth)
        clerk_id = request.auth.get('userId')
        if not clerk_id:
            return JsonResponse({'error': 'Missing clerk_id'}, status=400)

        playlists = Playlist.objects.filter(clerkId=clerk_id).order_by('-createdAt')
        data = []

        for playlist in playlists:
            # Prepare playlist data
            playlist_data = {
                '_id': str(playlist.id),
                'title': playlist.title,
                'avatar': playlist.avatar,
                'clerkId': playlist.clerkId,
                'createdAt': playlist.createdAt,
                'updatedAt': playlist.updatedAt,
                'songs': []
            }

            
            if playlist.songs:
                song_ids = playlist.songs  
                songs = Song.objects.filter(id__in=song_ids)
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
                playlist_data['songs'] = songs_data
            data.append(playlist_data)
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    
@csrf_exempt
def get_playlist_by_id(request, playlist_id):
    try:
        try:
            object_id = ObjectId(playlist_id)
            print(f"ObjectId: {object_id}")
        except InvalidId:
            return JsonResponse({'error': 'Invalid playlist ID'}, status=400)

        # Find the playlist by ID
        try:
            playlist = Playlist.objects.get(id=object_id)
        except Playlist.DoesNotExist:
            return JsonResponse({'error': 'Playlist not found'}, status=404)

        # Prepare playlist data
        playlist_data = {
            '_id': str(playlist.id),
            'title': playlist.title,
            'avatar': playlist.avatar if hasattr(playlist, 'avatar') else None,
            'clerkId': playlist.clerkId if hasattr(playlist, 'clerkId') else None,
            'createdAt': playlist.createdAt.isoformat() if hasattr(playlist, 'createdAt') else None,
            'songs': []
        }

        # Populate songs if the playlist has a songs field
        if hasattr(playlist, 'songs') and playlist.songs:
            song_ids = playlist.songs  # List of ObjectIds
            songs = Song.objects.filter(id__in=song_ids)
            
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
            playlist_data['songs'] = songs_data
        return JsonResponse(playlist_data, status=200)

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
