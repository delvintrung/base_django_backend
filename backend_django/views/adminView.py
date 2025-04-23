from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..models.artist import Artist
from ..models.album import Album
import json
from datetime import datetime
from bson import ObjectId 
from django.shortcuts import get_object_or_404
import cloudinary.uploader
from django.core.files.uploadedfile import UploadedFile
from ..models.song import Song
from mongoengine.queryset.visitor import Q
import random
import traceback
# 1@csrf_exempt
def upload_to_cloudinary(file: UploadedFile, folder="songs/source"):
    try:
        result = cloudinary.uploader.upload(
            file,
            resource_type="auto",  # Automatically detect the resource type (image, video, etc.)
            folder=folder  # Set the folder for the upload
        )
        print(result.get("secure_url"))
        return result.get("secure_url")
    except Exception as e:
        print("Error uploading to Cloudinary:", e)
        return None

@csrf_exempt
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
        print("Error in delete_album:", e)
        return JsonResponse({'error': str(e)}, status=500)
# 3
@csrf_exempt
def delete_song(request, song_id):
    try:
        if request.method != 'DELETE':
            return JsonResponse({'message': 'Method not allowed'}, status=405)

        song = Song.objects(id=song_id).first()
        if not song:
            return JsonResponse({'message': 'Song not found'}, status=404)

        if song.albumId:
            Album.objects(id=song.albumId).update_one(pull__songs=song.id)

        # Xóa bài hát
        song.delete()

        return JsonResponse({'message': 'Song deleted successfully'}, status=200)

    except Exception as e:
        print("Error in delete_song:", e)
        return JsonResponse({'error': str(e)}, status=500)
# 4
@csrf_exempt
def update_song(request, id):  # id được truyền vào như tham số
    if request.method != 'PUT':
        return JsonResponse({"message": "Method not allowed"}, status=405)

    print("Received song_id:", id)  # id sẽ có giá trị lấy từ URL path

    try:
        # Chuyển id từ string sang ObjectId
        song = Song.objects.get(id=ObjectId(id))
    except Song.DoesNotExist:
        return JsonResponse({"message": "Song not found"}, status=404)

    # Lấy dữ liệu từ form (FormData)
    title = request.POST.get('title')
    artist = request.POST.get('artist')
    duration = request.POST.get('duration')
    album_id = request.POST.get('albumId')

    audio_file = request.FILES.get('audioFile')
    image_file = request.FILES.get('imageFile')

    # Cập nhật audioUrl nếu có tệp mới
    if audio_file:
        song.audioUrl = upload_to_cloudinary(audio_file)

    # Cập nhật imageUrl nếu có tệp mới
    if image_file:
        song.imageUrl = upload_to_cloudinary(image_file)

    # Cập nhật các trường khác nếu có dữ liệu
    if title:
        song.title = title
    if artist:
        song.artist = artist
    if duration:
        song.duration = duration

    # Cập nhật album nếu albumId thay đổi
    if album_id and str(song.albumId) != str(album_id):
        if song.albumId:
            old_album = Album.objects.filter(id=ObjectId(song.albumId)).first()
            if old_album:
                old_album.songs.remove(song)
        new_album = Album.objects.filter(id=ObjectId(album_id)).first()
        if new_album:
            new_album.songs.add(song)
        song.albumId = album_id  
    else:
    # Nếu albumId không thay đổi, chỉ cần thông báo hoặc xử lý khác
        song.albumId= None   
    song.updatedAt=datetime.now()
    # Lưu thông tin đã cập nhật
    song.save()

    return JsonResponse({
     
        "_id": str(song["id"]),  # Chuyển ObjectId thành chuỗi
        "title": song["title"],
        "artist": str(song["artist"]),  # Chuyển ObjectId của artist thành chuỗi
        "audio_url": song["audioUrl"],
        "image_url": song["imageUrl"],
        "duration": song["duration"],
        "updatedAt":song["updatedAt"],
      # Chuyển ObjectId của album thành chuỗi
    
}, status=200)
@csrf_exempt
def create_song(request):
    if request.method == 'POST':
        try:
            # Lấy dữ liệu từ request.POST (tương tự với việc tạo album)
            title = request.POST.get('title')
            artist_id = request.POST.get('artist')  # Đây là ID của artist
            album_id = request.POST.get('albumId')  # Đây là ID của album
            duration = request.POST.get('duration')
            audio_file = request.FILES.get('audioFile')  # Tải lên file âm thanh (nếu có)
            image_file = request.FILES.get('imageFile')  # Tải lên file hình ảnh (nếu có)

            # Kiểm tra nếu thiếu trường bắt buộc
            if not all([title, duration, audio_file, image_file]):
                return JsonResponse({"message": "Missing required fields"}, status=400)

            # Upload image to Cloudinary (nếu có)
            imageUrl = upload_to_cloudinary(image_file)
            if not imageUrl:
                return JsonResponse({"message": "Error uploading image to Cloudinary"}, status=500)

            # Upload audio file to Cloudinary (nếu có)
            audioUrl = upload_to_cloudinary(audio_file)  # Bạn cần xử lý upload tương tự

            # Truy xuất artist và album từ ID
            artist = Artist.objects.filter(id=artist_id).first() if artist_id else None
            album = Album.objects.filter(id=album_id).first() if album_id else None

            # Kiểm tra nếu artist không tồn tại
            if not artist:
                return JsonResponse({"message": "Artist not found"}, status=404)

            # Tạo mới bài hát
            song = Song(
                title=title,
                artist=artist_id,  # Sử dụng đối tượng artist, không phải artist_id
                audioUrl=audioUrl,
                imageUrl=imageUrl,
                duration=duration,
                albumId=album_id,  # Sử dụng đối tượng album, không phải albumId
                createdAt=datetime.now(),
                updatedAt=datetime.now(),
            )

            song.save()

            # Tạo dữ liệu song trả về
            song_data = {
                "_id": str(song.id),
                "title": song.title,
                "artist": str(song.artist.id),   # Giả sử artist có thuộc tính name
                "audioUrl": song.audioUrl,
                "imageUrl": song.imageUrl,
                "duration": song.duration,
                "albumId": str(song.albumId.id) , 
                "createdAt": song.createdAt.isoformat(),
                "updatedAt": song.updatedAt.isoformat(),
            }

            # Trả về dữ liệu song dưới dạng JSON
            return JsonResponse(song_data, status=201)
        except Exception as e:
            traceback.print_exc()  # In toàn bộ traceback lỗi ra console
            return JsonResponse({"message": str(e)}, status=500)

@csrf_exempt
def createAlbum(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        artist = request.POST.get('artist')
        releaseYear = request.POST.get('releaseYear')
        image_file = request.FILES.get('imageFile')

        if not all([title, artist, releaseYear, image_file]):
            return JsonResponse({"message": "Missing required fields"}, status=400)

        # Upload image to Cloudinary
        imageUrl = upload_to_cloudinary(image_file)
        if not imageUrl:
            return JsonResponse({"message": "Error uploading image to Cloudinary"}, status=500)
           
        album = Album.objects.create(
            title=title,
            artist=artist,
            releaseYear=int(releaseYear),
            imageUrl=imageUrl
        )
        album_data = {
            "_id": str(album.id),
            "title": album.title,
            "artist": album.artist,
            "imageUrl": album.imageUrl,
            "releaseYear": album.releaseYear,
            "songs": [],  # Mặc định rỗng khi mới tạo
            "createdAt": album.createdAt.isoformat() if hasattr(album, 'createdAt') else now().isoformat(),
            "updatedAt": album.updatedAt.isoformat() if hasattr(album, 'updatedAt') else now().isoformat(),
        }    

        return JsonResponse({album_data}, status=201)