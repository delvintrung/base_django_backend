# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import cloudinary.uploader
import cloudinary.uploader
import json
from django.utils.dateparse import parse_date
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import cloudinary.api   
import os
from bson import ObjectId

from ..models.song import Song
from ..models.album import Album
from ..models.artist import Artist
from ..models.genre import Genre
from ..models.user import User


def upload_to_cloudinary(file, folder_name="others"):
    try:
        result = cloudinary.uploader.upload(
            file,
            folder=f"{folder_name}",
            resource_type="auto"
        )
        return result['secure_url']
    except Exception as e:
        print("Error in uploadToCloudinary:", e)
        raise Exception("Error uploading to cloudinary")

#user
#update user
@csrf_exempt
def update_user(request, user_id):
    if request.method != "PUT":
        return JsonResponse({"error": "Only PUT allowed"}, status=405)

    try:
        user = User.objects.get(id=user_id)
        data = json.loads(request.body)

        full_name = data.get("fullName", user.fullName)
        clerk_id = data.get("clerkId", user.clerkId)

        data_changed = False

        if user.fullName != full_name:
            user.fullName = full_name
            data_changed = True
        if user.clerkId != clerk_id:
            user.clerkId = clerk_id
            data_changed = True

        if data_changed:
            user.save()

        return JsonResponse({
            "message": "User updated successfully" if data_changed else "No changes detected",
            "user": {
                "id": str(user.id),
                "fullName": user.fullName,
                "clerkId": user.clerkId,
                "imageUrl": user.imageUrl,
                "createdAt": user.createdAt.isoformat(),
                "updatedAt": user.updatedAt.isoformat()
            }
        }, status=200)

    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except Exception as e:
        print("Error in update_user:", e)
        return JsonResponse({"error": str(e)}, status=500)

#delete user
@csrf_exempt
def delete_user(request, user_id):
    if request.method != "DELETE":
        return JsonResponse({"error": "Only DELETE allowed"}, status=405)

    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return JsonResponse({
            "message": "User deleted successfully",
            "userId": user_id
        }, status=200)

    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except Exception as e:
        print("Error in delete_user:", e)
        return JsonResponse({"error": str(e)}, status=500)


#artist
#create artist
@csrf_exempt
def create_artist(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        if 'imageFile' not in request.FILES:
            return JsonResponse({"error": "Please upload an image file"}, status=400)

        # Lấy dữ liệu nghệ sĩ từ yêu cầu
        name = request.POST.get("name")
        birthdate_str = request.POST.get("birthdate")
        image_file = request.FILES["imageFile"]

        # chuyển birthdate thành date
        birthdate = parse_date(birthdate_str)

        #upload ảnh đến cloudinary
        image_url = upload_to_cloudinary(image_file,"artists/source")

        # Lấy thể loại từ yêu cầu và kiểm tra xem chúng có tồn tại trong cơ sở dữ liệu không
        genre_ids = request.POST.getlist("genres")  # Thông qua GET để lấy các genre_id
        genres = []
        if genre_ids:
            genres = Genre.objects(id__in=genre_ids)  # Lấy tất cả Genre có id tương ứng

        # tạo và lưu artist
        artist = Artist(
            name=name,
            birthdate=birthdate,
            imageUrl=image_url,
            genres=genres  # Gán các genre vào artist
        )
        artist.save()

        return JsonResponse({
            "message": "Artist created successfully",
            "artistId": str(artist.id)
        }, status=201)

    except Exception as e:
        print("Error in create_artist:", e)
        return JsonResponse({"error": str(e)}, status=500)
    
#update artist
@csrf_exempt
def update_artist(request, artist_id):
    if request.method == 'PUT':
        try:
            artist = Artist.objects.get(id=artist_id)

            # Lấy dữ liệu JSON từ request body
            data = json.loads(request.body)

            name = data.get('name', artist.name)
            birthdate_str = data.get('birthdate', str(artist.birthdate) if artist.birthdate else '')
            birthdate = parse_date(birthdate_str) if birthdate_str else artist.birthdate

            # Genres
            genre_ids = data.get('genres', [])
            genres = Genre.objects(id__in=genre_ids) if genre_ids else artist.genres

            # Kiểm tra thay đổi
            data_changed = False
            if artist.name != name:
                artist.name = name
                data_changed = True
            if artist.birthdate != birthdate:
                artist.birthdate = birthdate
                data_changed = True
            if artist.genres != genres:
                artist.genres = genres
                data_changed = True
            # Debug log
            # print("Current artist data:", artist.name, artist.birthdate, artist.imageUrl)
            # print("Updated artist data:", name, birthdate, list(genres))
            if data_changed:
                artist.save()
                return JsonResponse({"message": "Artist updated successfully"}, status=200)
            else:
                return JsonResponse({"message": "No changes detected, artist not updated"}, status=200)

        except Artist.DoesNotExist:
            return JsonResponse({"message": "Artist not found"}, status=404)
        except Exception as e:
            print("Error updating artist:", e)
            return JsonResponse({"message": f"Error: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Only PUT allowed"}, status=405)
           
#delete artist
@csrf_exempt
def delete_artist(request, artist_id):
    if request.method != 'DELETE':
        return JsonResponse({"error": "Only DELETE allowed"}, status=405)

    try:
        artist = Artist.objects.get(id=artist_id)
        artist.delete()

        return JsonResponse({"message": "Artist deleted successfully"}, status=200)

    except Artist.DoesNotExist:
        return JsonResponse({"error": "Artist not found"}, status=404)
    except Exception as e:
        print("Error in delete_artist:", e)
        return JsonResponse({"error": str(e)}, status=500)

#song
@csrf_exempt
def create_song(request):
    if request.method == 'POST':
        # Ensure files are uploaded
        if 'audioFile' not in request.FILES or 'imageFile' not in request.FILES:
            return JsonResponse({"message": "Please upload all files"}, status=400)

        # Retrieve form data
        title = request.POST['title']
        artist = request.POST['artist']
        album_id = request.POST.get('albumId')
        duration = int(request.POST['duration'])
        audio_file = request.FILES['audioFile']
        image_file = request.FILES['imageFile']

        audio_url = upload_to_cloudinary(audio_file,"songs/source")
        image_url = upload_to_cloudinary(image_file,"songs/source")

        # Create and save the song
        song = Song(
            title=title,
            artist=artist,  # You may need to adjust the artist field handling
            audioUrl=audio_url,
            imageUrl=image_url,
            duration=duration,
            albumId=album_id if album_id else None
        )

        song.save()

        # If the song belongs to an album, update the album's songs array
        if album_id:
            album = Album.objects.get(id=album_id)
            album.songs.append(song)
            album.save()

        return JsonResponse(song.to_json(), status=201)

@csrf_exempt
def update_song(request, song_id):
    if request.method == 'PUT':
        try:
            song = Song.objects.get(id=song_id)

            # Update song details from form
            title = request.POST.get('title', song.title)
            artist = request.POST.get('artist', song.artist)
            album_id = request.POST.get('albumId', song.albumId)
            duration = int(request.POST.get('duration', song.duration))

            audio_file = request.FILES.get('audioFile')
            image_file = request.FILES.get('imageFile')

            if audio_file:
                song.audioUrl = upload_to_cloudinary(audio_file)
            if image_file:
                song.imageUrl = upload_to_cloudinary(image_file)

            song.title = title
            song.artist = artist
            song.duration = duration

            if album_id and album_id != song.albumId.id:
                # Remove song from the previous album
                if song.albumId:
                    old_album = Album.objects.get(id=song.albumId.id)
                    old_album.songs.remove(song)
                    old_album.save()

                # Add song to the new album
                new_album = Album.objects.get(id=album_id)
                new_album.songs.append(song)
                new_album.save()

            song.albumId = album_id

            song.save()

            return JsonResponse(song.to_json(), status=200)

        except Song.DoesNotExist:
            return JsonResponse({"message": "Song not found"}, status=404)


@csrf_exempt
def delete_song(request, song_id):
    if request.method == 'DELETE':
        try:
            song = Song.objects.get(id=song_id)

            # If song belongs to an album, update the album's songs array
            if song.albumId:
                album = Album.objects.get(id=song.albumId.id)
                album.songs.remove(song)
                album.save()

            song.delete()

            return JsonResponse({"message": "Song deleted successfully"}, status=200)

        except Song.DoesNotExist:
            return JsonResponse({"message": "Song not found"}, status=404)


@csrf_exempt
def create_album(request):
    if request.method == 'POST':
        # Retrieve form data
        title = request.POST['title']
        artist = request.POST['artist']
        release_year = int(request.POST['releaseYear'])
        image_file = request.FILES['imageFile']

        image_url = upload_to_cloudinary(image_file)

        album = Album(
            title=title,
            artist=artist,
            imageUrl=image_url,
            releaseYear=release_year
        )

        album.save()

        return JsonResponse(album.to_json(), status=201)


@csrf_exempt
def delete_album(request, album_id):
    if request.method == 'DELETE':
        try:
            album = Album.objects.get(id=album_id)
            # Delete all songs related to the album
            Song.objects(albumId=album.id).delete()

            album.delete()

            return JsonResponse({"message": "Album deleted successfully"}, status=200)

        except Album.DoesNotExist:
            return JsonResponse({"message": "Album not found"}, status=404)


@csrf_exempt
def check_admin(request):
    return JsonResponse({"admin": True}, status=200)
