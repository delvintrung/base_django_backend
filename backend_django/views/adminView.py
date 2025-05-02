from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..models.artist import Artist
from ..models.album import Album
from ..models.playlist import Playlist
from ..models.genre import Genre    
import json
from django.http import QueryDict
from django.http.multipartparser import MultiPartParser, MultiPartParserError
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from datetime import datetime
from bson import ObjectId 
from django.shortcuts import get_object_or_404
import cloudinary.uploader
from django.core.files.uploadedfile import UploadedFile
from ..models.song import Song
from django.views.decorators.http import require_http_methods
from mongoengine.queryset.visitor import Q
import random
import traceback
import os
import requests
from dotenv import load_dotenv
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Tải các biến môi trường từ tệp .env
load_dotenv()

CLERK_API_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_BASE_URL = "https://api.clerk.dev/v1"

# Header cho API của Clerk
headers = {
    "Authorization": f"Bearer {CLERK_API_KEY}",
    "Content-Type": "application/json"
}

# def token_required(f):
#     @wraps(f)
#     def decorated_function(request, *args, **kwargs):
#         token = request.headers.get("Authorization")
#         if not token:
#             return JsonResponse({"error": "Authorization token is missing."}, status=401)

#         response = requests.post(
#             f"{CLERK_BASE_URL}/verify_token", 
#             json={"token": token}, 
#             headers=headers
#         )

#         # 4. Nếu API trả về lỗi hoặc token không hợp lệ, trả về lỗi 401
#         if response.status_code != 200:
#             return JsonResponse({"error": "Invalid or expired token."}, status=401)

#         # 5. Nếu token hợp lệ, tiếp tục thực thi function view
#         return f(request, *args, **kwargs)

# 1
@csrf_exempt
def upload_to_cloudinary(file: UploadedFile, folder="songs/source"):
    try:
        result = cloudinary.uploader.upload(
            file,
            resource_type="auto",  # Automatically detect the resource type (image, video, etc.)
            folder=folder  # Set the folder for the upload
        )
        return result.get("secure_url")
    except Exception as e:
        return None
# 2
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_album(request, album_id):
    try:
        if request.method != 'DELETE':
            return JsonResponse({'message': 'Method not allowed'}, status=405)
        Song.objects(albumId=album_id).delete()
        album = Album.objects(id=album_id).first()
        if not album:
            return JsonResponse({'message': 'Album not found'}, status=404)
        album.delete()
        return JsonResponse({'message': 'Album deleted successfully'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
# 3
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_song(request, song_id):
    try:
        song = Song.objects(id=ObjectId(song_id)).first()
        if not song:
            return JsonResponse({'message': 'Song not found'}, status=404)
        if song.albumId:
            album_id = song.albumId.id if hasattr(song.albumId, 'id') else song.albumId
            Album.objects(id=album_id).update_one(pull__songs=song.id)
        song.delete()
        return JsonResponse({'message': 'Song deleted successfully'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
# 4
@csrf_exempt
@require_http_methods(["PUT"])
def update_song(request, id):
    if request.method != 'PUT':
        return JsonResponse({"message": "Method not allowed"}, status=405)

    try:
        song = Song.objects.get(id=ObjectId(id))
    except Song.DoesNotExist:
        return JsonResponse({"message": "Song not found"}, status=404)

    request.upload_handlers = [TemporaryFileUploadHandler(request)]
    try:
        parser = MultiPartParser(request.META, request, request.upload_handlers)
        data, files = parser.parse()
    except MultiPartParserError:
        return JsonResponse({"message": "Invalid form data"}, status=400)

    title = data.get('title')
    artist = data.get('artist')
    duration = data.get('duration')
    album_id = data.get('albumId')

    audio_file = files.get('audioUrl')
    image_file = files.get('imageUrl')

    if audio_file:
        song.audioUrl = upload_to_cloudinary(audio_file)

    if image_file:
        song.imageUrl = upload_to_cloudinary(image_file)

    if title:
        song.title = title
    if artist:
        artist_obj = Artist.objects.get(id=ObjectId(artist))  # Tìm Artist từ ObjectId
        song.artist = artist_obj
    if duration:
        song.duration = duration
    try:
        if song.albumId and song.albumId.id:
            album_id_value = str(song.albumId.id)
        else:
            album_id_value = "" 
    except mongoengine.errors.DoesNotExist:
        album_id_value = ""  

    if album_id:
        # id có thay đổi
        if str(album_id) != album_id_value:
            if album_id_value:
                old_album = Album.objects.filter(id=ObjectId(album_id_value)).first()
                if old_album:
                    old_album.songs.remove(song)
                    old_album.updatedAt = datetime.now() 
                    old_album.save() 
            new_album = Album.objects.filter(id=ObjectId(album_id)).first()
            if new_album:
                new_album.songs.append(song)
                new_album.updatedAt = datetime.now() 
                new_album.save() 
            song.albumId = new_album.id

    else:
        if str(album_id) !=  album_id_value:
            old_album = Album.objects.filter(id=ObjectId(song.albumId.id)).first()
            if old_album:
                old_album.songs.remove(song)
                old_album.updatedAt = datetime.now()  
                old_album.save() 

    song.save()
    return JsonResponse({
        "_id": str(song["id"]),
        "title": song["title"],
        "artist": str(song["artist"]), 
        "audio_url": song["audioUrl"],
        "image_url": song["imageUrl"],
        "duration": song["duration"],
        "updatedAt":song["updatedAt"],
    
}, status=200)
 

# # 5
@csrf_exempt
@require_http_methods(["POST"])
def create_song(request):
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            artist_id = request.POST.get('artist') 
            album_id = request.POST.get('albumId')  
            duration = request.POST.get('duration')
            audio_file = request.FILES.get('audioFile')  
            image_file = request.FILES.get('imageFile')  
        
            if not all([title, duration, audio_file, image_file]):
                return JsonResponse({"message": "Missing required fields"}, status=400)
            imageUrl = upload_to_cloudinary(image_file)
            if not imageUrl:
                return JsonResponse({"message": "Error uploading image to Cloudinary"}, status=500)
            audioUrl = upload_to_cloudinary(audio_file)  # Bạn cần xử lý upload tương tự
            if not audioUrl:
                return JsonResponse({"message": "Error uploading image to Cloudinary"},)
            song = Song(
                title=title,
                artist=artist_id, 
                audioUrl=audioUrl,
                imageUrl=imageUrl,
                duration=duration,
                albumId = album_id if album_id not in (None, '', 'null') else None,
                createdAt=datetime.now(),
                updatedAt=datetime.now(),
            )
            song.save()
            if  not album_id :
                albums_collection.update_one(album_id,song.id)
            
            song_data = {
                "_id": str(song.id),
                "title": song.title,
                "artist": str(song.artist.id),   # Giả sử artist có thuộc tính name
                "audioUrl": song.audioUrl,
                "imageUrl": song.imageUrl,
                "duration": song.duration,
                "albumId": str(song.albumId.id) if song.albumId else None,
                "createdAt": song.createdAt.isoformat(),
                "updatedAt": song.updatedAt.isoformat(),
            }
            return JsonResponse(song_data, status=201)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
@csrf_exempt
@require_http_methods(["POST"])
def createAlbum(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        artist = request.POST.get('artist')
        releaseYear = request.POST.get('releaseYear')
        image_file = request.FILES.get('imageFile')
        song_ids = request.POST.getlist("songIds[]")

        if not all([title, releaseYear, image_file]):
            return JsonResponse({"message": "Missing required fields"}, status=400)
        
        if not title or not title.strip():
            return JsonResponse({"message": "Album title is required"}, status=400)
        
        if not image_file:
            return JsonResponse({"message": "Album artwork is required"}, status=400)

        try:
            release_year = int(releaseYear) 
        except ValueError:
            return JsonResponse({"message": "Invalid release year. Must be an integer"}, status=400)

        current_year = datetime.now().year
        if release_year < 1900 or release_year > current_year:
            return JsonResponse({"message": f"Invalid release year. Must be between 1900 and {current_year}"}, status=400)
        if not song_ids or len(song_ids) < 2:
            return JsonResponse({"message": "At least 2 songs are required for an album"}, status=400)

        count = 0
        for song_id in song_ids:
            song = Song.objects.filter(id=ObjectId(song_id)).first()
            if song:
                count += 1

        if count != len(song_ids):
            return JsonResponse({'message': 'One or more song IDs are invalid'}, status=400)

        imageUrl = upload_to_cloudinary(image_file)
        if not imageUrl:
            return JsonResponse({"message": "Error uploading image to Cloudinary"}, status=500)

        # Tạo album
        album = Album.objects.create(
            title=title,
            artist=artist if artist else None,
            songs=[ObjectId(gid) for gid in song_ids],
            releaseYear=release_year,
            imageUrl=imageUrl, 
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
        )
        # Trả về thông tin album
        album_data = {
            "_id": str(album.id),
            "title": album.title,
            "artist": album.artist,
            "imageUrl": album.imageUrl,
            "releaseYear": album.releaseYear,
            "songs": [str(song.id) for song in album.songs],  
            "createdAt": album.createdAt.isoformat() if hasattr(album, 'createdAt') else datetime.now().isoformat(),
            "updatedAt": album.updatedAt.isoformat() if hasattr(album, 'updatedAt') else datetime.now().isoformat(),
        }
        return JsonResponse(album_data, status=201) 
 

@csrf_exempt
@require_http_methods(["POST"])
def createArtist(request):
    try:
        # Lấy dữ liệu từ POST và FILES
        name = request.POST.get('name')
        birthdate = request.POST.get('birthdate')
        description = request.POST.get('description')
        listeners = request.POST.get('listeners')
        followers = request.POST.get('followers')
        genre_ids = request.POST.getlist('genreIds[]')  # Lưu ý đây là 'genreIds[]'
        image_file = request.FILES.get('imageFile')

        # Validate các trường
        if not name or not name.strip():
            return JsonResponse({"message": "Artist name is required"}, status=400)
        if not birthdate:
            return JsonResponse({"message": "Valid birthdate is required"}, status=400)
        try:
            birthdate = datetime.strptime(birthdate, "%Y-%m-%d")
        except ValueError:
            return JsonResponse({"message": "Birthdate format must be YYYY-MM-DD"}, status=400)
        if not description or not description.strip():
            return JsonResponse({"message": "Artist description is required"}, status=400)
        if not listeners or not str(listeners).isdigit() or int(listeners) < 0:
            return JsonResponse({"message": "Valid listeners count is required"}, status=400)
        if not followers or not str(followers).isdigit() or int(followers) < 0:
            return JsonResponse({"message": "Valid followers count is required"}, status=400)
        if not genre_ids or len(genre_ids) == 0:
            return JsonResponse({"message": "At least one genre is required"}, status=400)

        # Validate genres
        count=0
        for gid in genre_ids:
            genre = Genre.objects.filter(id=ObjectId(gid)).first()
            if genre:
                count+=1
        if count !=  len(genre_ids):
             return JsonResponse({'message': 'One or more genre IDs are invalid'}, status=400)
        image_url = ""
        if image_file:
            image_url = upload_to_cloudinary(image_file)

        # Tạo artist
        artist = Artist(
            name=name.strip(),
            birthdate=birthdate,
            imageUrl=image_url,
            genres=[ObjectId(gid) for gid in genre_ids],
            description=description.strip(),
            listeners=int(listeners),
            followers=int(followers),
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
        )
        artist.save()

        # Trả về thông tin artist mới tạo
        return JsonResponse({
            "_id": str(artist.id),
            "name": artist.name,
            "birthdate": artist.birthdate.isoformat(),
            "imageUrl": artist.imageUrl,
            "genres": [str(genre.id) for genre in artist.genres],
            "description": artist.description,
            "listeners": artist.listeners,
            "followers": artist.followers,
            "createdAt": artist.createdAt,
            "updatedAt": artist.updatedAt,
        }, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_playlist(request, playlist_id):
    try:
        if request.method != 'DELETE':
            return JsonResponse({'message': 'Method not allowed'}, status=405)
        playlist_id = ObjectId(playlist_id)

        # Truy vấn Playlist theo ID
        playlist = Playlist.objects(id=playlist_id).first() 
       
        if not playlist:
            return JsonResponse({'message': 'Playlist not found'}, status=404)
        playlist.delete()
        return JsonResponse({'message': 'Playlist deleted successfully'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
@csrf_exempt
@require_http_methods(["PUT"])
def update_playlist(request, playlist_id):
    if request.method == 'PUT':
        request.upload_handlers = [TemporaryFileUploadHandler(request)]
        try:
           
            parser = MultiPartParser(request.META, request, request.upload_handlers)
            data, files = parser.parse() 
            # Lấy các giá trị từ data
            title = data.get('title', None)
            avatar = files.get('avatar', None)  # Lấy avatar từ file upload
            try:
                playlist = Playlist.objects.get(id=playlist_id)
            except ObjectDoesNotExist:
                return JsonResponse({"message": "Playlist not found"}, status=404)
            if title and not title.strip():
                return JsonResponse({"message": "Playlist title cannot be empty"}, status=400)

            if title:
                playlist.title = title
            if avatar:
                playlist.avatar = upload_to_cloudinary(avatar)  
            playlist.save()

            return JsonResponse({
                "id": str(playlist.id),
                "title": playlist.title,
                "avatar": playlist.avatar.url if playlist.avatar else None,  # Trả về URL của avatar
            }, status=200)

        except MultiPartParserError:
            return JsonResponse({"message": "Invalid form data"}, status=400)
        except Exception as e:
            return JsonResponse({"message": f"Error: {str(e)}"}, status=500)

    return JsonResponse({"message": "Method not allowed"}, status=405)
def get_admin_user():
    try:
        url = f"{CLERK_BASE_URL}/users"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            users = response.json()
            print(users) 
            for user in users:
                if user.get("email_addresses", [{}])[0].get("email_address") == os.getenv("ADMIN_EMAIL"):
                    return JsonResponse({"admin": True, "message": "You are an admin"}, status=200)
            return  JsonResponse({"admin": False, "message": "Unauthorized - you must be an admin"}, status=403)
        else:
            return None  
    except Exception as e:
        print(f"Error while fetching admin user: {str(e)}")
        return None





@csrf_exempt
@require_http_methods(["PUT"])
def update_album(request, album_id):
    if request.method == 'PUT':
        request.upload_handlers = [TemporaryFileUploadHandler(request)]

        try:
            parser = MultiPartParser(request.META, request, request.upload_handlers)
            data, files = parser.parse() 

            title = data.get('title')
            description = data.get('description')
            avatar = files.get('avatar')  # File hình ảnh

            # Kiểm tra hợp lệ ID
            if not ObjectId.is_valid(playlist_id):
                return JsonResponse({'error': 'Invalid playlist ID'}, status=400)

            # Tìm playlist
            playlist = Playlist.objects(id=playlist_id).first()
            if not playlist:
                return JsonResponse({'error': 'Playlist not found'}, status=404)

            # Kiểm tra và cập nhật
            if title is not None:
                if not title.strip():
                    return JsonResponse({'error': 'Title cannot be empty'}, status=400)
                playlist.title = title

            if description is not None:
                playlist.description = description

            if avatar:
                # Gọi hàm upload lên Cloudinary hoặc nơi lưu khác
                playlist.avatar_url = upload_to_cloudinary(avatar)

            playlist.save()
            return JsonResponse({'message': 'Playlist updated successfully'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)