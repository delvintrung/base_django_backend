from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..models.artist import Artist
from ..models.genre import Genre
from ..models.song import Song
from mongoengine.queryset.visitor import Q
import random
@csrf_exempt
def upload_to_cloudinary(file, folder="songs/source"):
    try:
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type="auto"  
        )
        return result.get("secure_url")
    except Exception as e:
        print("Error in upload_to_cloudinary:", e)
        raise Exception("Error uploading to Cloudinary")
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
