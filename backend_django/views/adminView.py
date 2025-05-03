from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..models.artist import Artist
from ..models.album import Album
from ..models.playlist import Playlist
from ..models.genre import Genre 
from ..models.user import User   
import json
from django.http import QueryDict
from django.http.multipartparser import MultiPartParser, MultiPartParserError
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from datetime import datetime
from bson import ObjectId 
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
import cloudinary.uploader
from django.core.files.uploadedfile import UploadedFile
from ..models.song import Song
from django.views.decorators.http import require_http_methods
import mongoengine
import os
import requests
from dotenv import load_dotenv
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from functools import wraps
from rest_framework.decorators import api_view
from django.conf import settings
from django.http import JsonResponse

# Tải các biến môi trường từ tệp .env
load_dotenv()

CLERK_API_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_BASE_URL = "https://api.clerk.dev/v1"

# Header cho API của Clerk
headers = {
    "Authorization": f"Bearer {CLERK_API_KEY}",
    "Content-Type": "application/json"
}
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
# @csrf_exempt
# @require_http_methods(["PUT"])
# def update_song(request, id):
#     if request.method != 'PUT':
#         return JsonResponse({"message": "Method not allowed"}, status=405)

#     try:
#         song = Song.objects.get(id=ObjectId(id))
#     except Song.DoesNotExist:
#         return JsonResponse({"message": "Song not found"}, status=404)

#     request.upload_handlers = [TemporaryFileUploadHandler(request)]
#     try:
#         parser = MultiPartParser(request.META, request, request.upload_handlers)
#         data, files = parser.parse()
#     except MultiPartParserError:
#         return JsonResponse({"message": "Invalid form data"}, status=400)

#     title = data.get('title')
#     artist = data.get('artist')
#     duration = data.get('duration')
#     album_id = data.get('albumId')

#     audio_file = files.get('audioUrl')
#     image_file = files.get('imageUrl')

#     if audio_file:
#         song.audioUrl = upload_to_cloudinary(audio_file)

#     if image_file:
#         song.imageUrl = upload_to_cloudinary(image_file)

#     if title:
#         song.title = title
#     if artist:
#         artist_obj = Artist.objects.get(id=ObjectId(artist))  # Tìm Artist từ ObjectId
#         song.artist = artist_obj
#     if duration:
#         song.duration = duration
#     album_id_value = str(song.albumId) if song.albumId else None 
#     print(album_id_value)
#     if album_id:
#         # id có thay đổi
#         if str(album_id) != album_id_value:
#             if album_id_value:
#                 old_album = Album.objects.filter(id=ObjectId(album_id_value)).first()
#                 if old_album:
#                     old_album.songs.remove(song)
#                     old_album.updatedAt = datetime.now() 
#                     old_album.save() 
#             new_album = Album.objects.filter(id=ObjectId(album_id)).first()
#             if new_album:
#                 new_album.songs.append(song)
#                 new_album.updatedAt = datetime.now() 
#                 new_album.save() 
#             song.albumId = new_album.id

#     else:
#         if str(album_id) !=  album_id_value:
#             old_album = Album.objects.filter(id=ObjectId(song.albumId.id)).first()
#             if old_album:
#                 old_album.songs.remove(song)
#                 old_album.updatedAt = datetime.now()  
#                 old_album.save() 

#     song.save()
#     return JsonResponse({
#         "_id": str(song["id"]),
#         "title": song["title"],
#         "artist": str(song["artist"]), 
#         "audio_url": song["audioUrl"],
#         "image_url": song["imageUrl"],
#         "duration": song["duration"],
#         "updatedAt":song["updatedAt"],
    
# }, status=200)
 
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
        try:
            artist_obj = Artist.objects.get(id=ObjectId(artist))
            song.artist = artist_obj
        except Artist.DoesNotExist:
            return JsonResponse({"message": "Artist not found"}, status=404)

    if duration:
        song.duration = duration

    old_album_id = str(song.albumId) if song.albumId else None

    if album_id:
        if album_id != old_album_id:
            # Xóa khỏi album cũ
            if old_album_id:
                old_album = Album.objects.filter(id=ObjectId(old_album_id)).first()
                if old_album and song.id in old_album.songs:
                    old_album.songs.remove(song.id)
                    old_album.updatedAt = datetime.now()
                    old_album.save()

            # Thêm vào album mới
            new_album = Album.objects.filter(id=ObjectId(album_id)).first()
            if new_album:
                if song.id not in new_album.songs:
                    new_album.songs.append(song.id)
                    new_album.updatedAt = datetime.now()
                    new_album.save()
                song.albumId = new_album.id
    else:
        # Nếu album_id bị xóa (set None)
        if old_album_id:
            old_album = Album.objects.filter(id=ObjectId(old_album_id)).first()
            if old_album and song.id in old_album.songs:
                old_album.songs.remove(song.id)
                old_album.updatedAt = datetime.now()
                old_album.save()
            song.albumId = None

    song.updatedAt = datetime.now()
    song.save()

    return JsonResponse({
        "_id": str(song.id),
        "title": song.title,
        "artist": str(song.artist.id),
        "audio_url": song.audioUrl,
        "image_url": song.imageUrl,
        "duration": song.duration,
        "albumId": str(song.albumId) if song.albumId else None,
        "updatedAt": song.updatedAt.isoformat(),
    }, status=200)

# # 5
@csrf_exempt
@require_http_methods(["POST"])
def create_songadmin(request):
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            artist_id = request.POST.get('artist') 
            album_id = request.POST.get('albumId')  
            duration = request.POST.get('duration')
            audio_file = request.FILES.get('audioFile')  
            image_file = request.FILES.get('imageFile')  
        
            missing_fields = []
            if not title:
                missing_fields.append("title")
            if not duration:
                missing_fields.append("duration")
            if not audio_file:
                missing_fields.append("audioFile")
            if not image_file:
                missing_fields.append("imageFile")

            if missing_fields:
                return JsonResponse({"message": f"Missing required fields: {', '.join(missing_fields)}"}, status=400)
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
            if album_id and album_id not in ('', 'null'):
                albums_collection = Album._get_collection()
                albums_collection.update_one({'_id': ObjectId(album_id)}, {'$push': {'songs': song.id}})
            album_intance = None
            if album_id and album_id not in ('', 'null'):
                    try:
                        album_instance = Album.objects.get(id=album_id)
                    except Album.DoesNotExist:
                        return JsonResponse({"message": "Album not found"}, status=404)

            print(album_id)
            song_data = {
                "_id": str(song.id),
                "title": song.title,
                "artist": str(song.artist),
                "audioUrl": song.audioUrl,
                "imageUrl": song.imageUrl,
                "duration": song.duration,
                "albumId": album_id,
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
            "artist": str(album.artist.id) if album.artist else None,
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
            # try:
            #     print(f"Trying genre id: {gid}")
            #     genre = Genre.objects.filter(id=ObjectId(gid)).first()
            #     if not genre:
            #         print(f"Genre with id {gid} not found.")
            #     else:
            #         print(f"Genre found: {genre}")
            # except Exception as e:
            #     print(f"Error with gid {gid}: {e}")
            # # print(gid)
            genre = Genre.objects.filter(id=ObjectId(gid)).first()
            print(genre)
            if genre:
                count+=1
                print(count)    
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
def update_albumadmin(request, album_id):
    try:
        album = Album.objects.get(id=ObjectId(album_id))
    except Album.DoesNotExist:
        return JsonResponse({"message": "Album not found"}, status=404)

    try:
        parser = MultiPartParser(request.META, request, request.upload_handlers)
        data, files = parser.parse()
    except MultiPartParserError:
        return JsonResponse({"message": "Invalid form data"}, status=400)

    title = data.get('title')
    artist_id = data.get('artist')
    release_year = data.get('releaseYear')
    song_ids = data.getlist('songIds[]')
    image_file = files.get('imageFile')

    if not all([title, artist_id, release_year, image_file]):
        return JsonResponse({"message": "Missing required fields"}, status=400)

    if not title.strip():
        return JsonResponse({"message": "Album title is required"}, status=400)

    try:
        release_year = int(release_year)
    except ValueError:
        return JsonResponse({"message": "Release year must be an integer"}, status=400)

    current_year = datetime.now().year
    if release_year < 1900 or release_year > current_year:
        return JsonResponse({"message": f"Invalid release year. Must be between 1900 and {current_year}"}, status=400)

    if not song_ids or len(song_ids) < 2:
        return JsonResponse({"message": "At least 2 songs are required"}, status=400)

    valid_song_ids = [ObjectId(id) for id in song_ids if Song.objects.filter(id=ObjectId(id)).first()]
    if len(valid_song_ids) != len(song_ids):
        return JsonResponse({"message": "One or more song IDs are invalid"}, status=400)

    # Upload image
    image_url = upload_to_cloudinary(image_file)
    if not image_url:
        return JsonResponse({"message": "Failed to upload image"}, status=500)

    # Update album
    album.title = title
    album.artist = Artist.objects.get(id=ObjectId(artist_id))  # đảm bảo Artist tồn tại
    album.releaseYear = release_year
    album.image = image_url
    album.songs = valid_song_ids
    album.save()

    return JsonResponse({"message": "Album updated successfully"}, status=200)

@csrf_exempt
@require_http_methods(["PUT"])
def update_playlist(request, id):
    try:
        # Parse multipart/form-data
        request.upload_handlers = [TemporaryFileUploadHandler(request)]
        parser = MultiPartParser(request.META, request, request.upload_handlers)
        data, files = parser.parse()
        
        title = data.get('title')
        avatar = files.get('avatar')

        playlist = Playlist.objects(id=ObjectId(id)).first()
        if not playlist:
            return JsonResponse({"message": "Playlist not found"}, status=404)

        if title is not None and not title.strip():
            return JsonResponse({"message": "Playlist title cannot be empty"}, status=400)

        if title:
            playlist.title = title

        if avatar:
            playlist.avatar = upload_to_cloudinary(avatar)

        playlist.save()

        return JsonResponse({
            "_id": str(playlist.id),
            "title": playlist.title,
            "avatar": playlist.avatar,
            "updatedAt": playlist.updatedAt.isoformat() if playlist.updatedAt else None
        }, status=200)

    except Exception as e:
        print("Error in update_playlist:", e)
        return JsonResponse({"message": "Internal server error"}, status=500)

# def upload_to_cloudinary(file, folder_name="others"):
#     try:
#         result = cloudinary.uploader.upload(
#             file,
#             folder=f"{folder_name}",
#             resource_type="auto"
#         )
#         return result['secure_url']
#     except Exception as e:
#         print("Error in uploadToCloudinary:", e)
#         raise Exception("Error uploading to cloudinary")

# #user
# #update user
# @csrf_exempt
# def update_user(request, user_id):
#     if request.method != "PUT":
#         return JsonResponse({"error": "Only PUT allowed"}, status=405)

#     try:
#         user = User.objects.get(id=user_id)
#         data = json.loads(request.body)

#         full_name = data.get("fullName", user.fullName)
#         clerk_id = data.get("clerkId", user.clerkId)

#         data_changed = False

#         if user.fullName != full_name:
#             user.fullName = full_name
#             data_changed = True
#         if user.clerkId != clerk_id:
#             user.clerkId = clerk_id
#             data_changed = True

#         if data_changed:
#             user.save()

#         return JsonResponse({
#             "message": "User updated successfully" if data_changed else "No changes detected",
#             "user": {
#                 "id": str(user.id),
#                 "fullName": user.fullName,
#                 "clerkId": user.clerkId,
#                 "imageUrl": user.imageUrl,
#                 "createdAt": user.createdAt.isoformat(),
#                 "updatedAt": user.updatedAt.isoformat()
#             }
#         }, status=200)

#     except User.DoesNotExist:
#         return JsonResponse({"error": "User not found"}, status=404)
#     except Exception as e:
#         print("Error in update_user:", e)
#         return JsonResponse({"error": str(e)}, status=500)

# #delete user
# @csrf_exempt
# def delete_user(request, user_id):
#     if request.method != "DELETE":
#         return JsonResponse({"error": "Only DELETE allowed"}, status=405)

#     try:
#         user = User.objects.get(id=user_id)
#         user.delete()
#         return JsonResponse({
#             "message": "User deleted successfully",
#             "userId": user_id
#         }, status=200)

#     except User.DoesNotExist:
#         return JsonResponse({"error": "User not found"}, status=404)
#     except Exception as e:
#         print("Error in delete_user:", e)
#         return JsonResponse({"error": str(e)}, status=500)


# #artist
# #create artist
# @csrf_exempt
# def create_artist(request):
#     if request.method != "POST":
#         return JsonResponse({"error": "Only POST allowed"}, status=405)

#     try:
#         if 'imageFile' not in request.FILES:
#             return JsonResponse({"error": "Please upload an image file"}, status=400)

#         # Lấy dữ liệu nghệ sĩ từ yêu cầu
#         name = request.POST.get("name")
#         birthdate_str = request.POST.get("birthdate")
#         image_file = request.FILES["imageFile"]

#         # chuyển birthdate thành date
#         birthdate = parse_date(birthdate_str)

#         #upload ảnh đến cloudinary
#         image_url = upload_to_cloudinary(image_file,"artists/source")

#         # Lấy thể loại từ yêu cầu và kiểm tra xem chúng có tồn tại trong cơ sở dữ liệu không
#         genre_ids = request.POST.getlist("genres")  # Thông qua GET để lấy các genre_id
#         genres = []
#         if genre_ids:
#             genres = Genre.objects(id__in=genre_ids)  # Lấy tất cả Genre có id tương ứng

#         # tạo và lưu artist
#         artist = Artist(
#             name=name,
#             birthdate=birthdate,
#             imageUrl=image_url,
#             genres=genres  # Gán các genre vào artist
#         )
#         artist.save()

#         return JsonResponse({
#             "message": "Artist created successfully",
#             "artistId": str(artist.id)
#         }, status=201)

#     except Exception as e:
#         print("Error in create_artist:", e)
#         return JsonResponse({"error": str(e)}, status=500)
    
# #update artist
# @csrf_exempt
# def update_artist(request, artist_id):
#     if request.method == 'PUT':
#         try:
#             artist = Artist.objects.get(id=artist_id)

#             # Lấy dữ liệu JSON từ request body
#             data = json.loads(request.body)

#             name = data.get('name', artist.name)
#             birthdate_str = data.get('birthdate', str(artist.birthdate) if artist.birthdate else '')
#             birthdate = parse_date(birthdate_str) if birthdate_str else artist.birthdate

#             # Genres
#             genre_ids = data.get('genres', [])
#             genres = Genre.objects(id__in=genre_ids) if genre_ids else artist.genres

#             # Kiểm tra thay đổi
#             data_changed = False
#             if artist.name != name:
#                 artist.name = name
#                 data_changed = True
#             if artist.birthdate != birthdate:
#                 artist.birthdate = birthdate
#                 data_changed = True
#             if artist.genres != genres:
#                 artist.genres = genres
#                 data_changed = True
#             # Debug log
#             # print("Current artist data:", artist.name, artist.birthdate, artist.imageUrl)
#             # print("Updated artist data:", name, birthdate, list(genres))
#             if data_changed:
#                 artist.save()
#                 return JsonResponse({"message": "Artist updated successfully"}, status=200)
#             else:
#                 return JsonResponse({"message": "No changes detected, artist not updated"}, status=200)

#         except Artist.DoesNotExist:
#             return JsonResponse({"message": "Artist not found"}, status=404)
#         except Exception as e:
#             print("Error updating artist:", e)
#             return JsonResponse({"message": f"Error: {str(e)}"}, status=500)
#     else:
#         return JsonResponse({"error": "Only PUT allowed"}, status=405)
           
# #delete artist
# @csrf_exempt
# def delete_artist(request, artist_id):
#     if request.method != 'DELETE':
#         return JsonResponse({"error": "Only DELETE allowed"}, status=405)

#     try:
#         artist = Artist.objects.get(id=artist_id)
#         artist.delete()

#         return JsonResponse({"message": "Artist deleted successfully"}, status=200)

#     except Artist.DoesNotExist:
#         return JsonResponse({"error": "Artist not found"}, status=404)
#     except Exception as e:
#         print("Error in delete_artist:", e)
#         return JsonResponse({"error": str(e)}, status=500)

# #song
# @csrf_exempt
# def create_song(request):
#     if request.method == 'POST':
#         # Ensure files are uploaded
#         if 'audioFile' not in request.FILES or 'imageFile' not in request.FILES:
#             return JsonResponse({"message": "Please upload all files"}, status=400)

#         # Retrieve form data
#         title = request.POST['title']
#         artist = request.POST['artist']
#         album_id = request.POST.get('albumId')
#         duration = int(request.POST['duration'])
#         audio_file = request.FILES['audioFile']
#         image_file = request.FILES['imageFile']

#         audio_url = upload_to_cloudinary(audio_file,"songs/source")
#         image_url = upload_to_cloudinary(image_file,"songs/source")

#         # Create and save the song
#         song = Song(
#             title=title,
#             artist=artist,  # You may need to adjust the artist field handling
#             audioUrl=audio_url,
#             imageUrl=image_url,
#             duration=duration,
#             albumId=album_id if album_id else None
#         )

#         song.save()

#         # If the song belongs to an album, update the album's songs array
#         if album_id:
#             album = Album.objects.get(id=album_id)
#             album.songs.append(song)
#             album.save()

#         return JsonResponse(song.to_json(), status=201)

# @csrf_exempt
# def update_song(request, song_id):
#     if request.method == 'PUT':
#         try:
#             song = Song.objects.get(id=song_id)

#             # Update song details from form
#             title = request.POST.get('title', song.title)
#             artist = request.POST.get('artist', song.artist)
#             album_id = request.POST.get('albumId', song.albumId)
#             duration = int(request.POST.get('duration', song.duration))

#             audio_file = request.FILES.get('audioFile')
#             image_file = request.FILES.get('imageFile')

#             if audio_file:
#                 song.audioUrl = upload_to_cloudinary(audio_file)
#             if image_file:
#                 song.imageUrl = upload_to_cloudinary(image_file)

#             song.title = title
#             song.artist = artist
#             song.duration = duration

#             if album_id and album_id != song.albumId.id:
#                 # Remove song from the previous album
#                 if song.albumId:
#                     old_album = Album.objects.get(id=song.albumId.id)
#                     old_album.songs.remove(song)
#                     old_album.save()

#                 # Add song to the new album
#                 new_album = Album.objects.get(id=album_id)
#                 new_album.songs.append(song)
#                 new_album.save()

#             song.albumId = album_id

#             song.save()

#             return JsonResponse(song.to_json(), status=200)

#         except Song.DoesNotExist:
#             return JsonResponse({"message": "Song not found"}, status=404)


# @csrf_exempt
# def delete_song(request, song_id):
#     if request.method == 'DELETE':
#         try:
#             song = Song.objects.get(id=song_id)

#             # If song belongs to an album, update the album's songs array
#             if song.albumId:
#                 album = Album.objects.get(id=song.albumId.id)
#                 album.songs.remove(song)
#                 album.save()

#             song.delete()

#             return JsonResponse({"message": "Song deleted successfully"}, status=200)

#         except Song.DoesNotExist:
#             return JsonResponse({"message": "Song not found"}, status=404)


# @csrf_exempt
# def create_album(request):
#     if request.method == 'POST':
#         # Retrieve form data
#         title = request.POST['title']
#         artist = request.POST['artist']
#         release_year = int(request.POST['releaseYear'])
#         image_file = request.FILES['imageFile']

#         image_url = upload_to_cloudinary(image_file)

#         album = Album(
#             title=title,
#             artist=artist,
#             imageUrl=image_url,
#             releaseYear=release_year
#         )

#         album.save()

#         return JsonResponse(album.to_json(), status=201)


# @csrf_exempt
# def delete_album(request, album_id):
#     if request.method == 'DELETE':
#         try:
#             album = Album.objects.get(id=album_id)
#             # Delete all songs related to the album
#             Song.objects(albumId=album.id).delete()

#             album.delete()

#             return JsonResponse({"message": "Album deleted successfully"}, status=200)

#         except Album.DoesNotExist:
#             return JsonResponse({"message": "Album not found"}, status=404)

