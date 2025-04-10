from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..models.artist import Artist
from ..models.genre import Genre
from ..models.song import Song
from mongoengine.queryset.visitor import Q
import random

@csrf_exempt
def get_all_artists(request):
    try:
        # -1 = Descending => newest -> oldest
        # 1 = Ascending => oldest -> newest
        artists = Artist.objects.order_by('-created_at').select_related()
        artists_data = [a.to_mongo().to_dict() for a in artists]
        return JsonResponse(artists_data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def get_featured_songs(request):
    try:
        # fetch 6 random songs using mongodb's aggregation pipeline
        # Django (MongoEngine) doesn't support full aggregation like Mongoose.
        # You can simulate `$sample` by fetching all and randomly picking:

        all_songs = list(Song.objects.all())
        sampled_songs = random.sample(all_songs, min(6, len(all_songs)))

        result = []
        for song in sampled_songs:
            artist = song.artist.fetch() if song.artist else None
            result.append({
                "_id": str(song.id),
                "title": song.title,
                "artist": artist.to_mongo().to_dict() if artist else None,
                "imageUrl": song.imageUrl,
                "audioUrl": song.audioUrl,
            })

        return JsonResponse(result, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def get_made_for_you_songs(request):
    try:
        all_songs = list(Song.objects.all())
        sampled_songs = random.sample(all_songs, min(4, len(all_songs)))

        result = []
        for song in sampled_songs:
            artist = song.artist.fetch() if song.artist else None
            result.append({
                "_id": str(song.id),
                "title": song.title,
                "artist": artist.to_mongo().to_dict() if artist else None,
                "imageUrl": song.imageUrl,
                "audioUrl": song.audioUrl,
            })

        return JsonResponse(result, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def create_artist(request):
    try:
        if request.method != 'POST':
            return JsonResponse({'message': 'Method not allowed'}, status=405)

        if 'imageFile' not in request.FILES:
            return JsonResponse({'message': 'Please upload all files'}, status=400)

        name = request.POST.get('name')
        birthdate = request.POST.get('birthdate')
        image_file = request.FILES['imageFile']

        print("imageFile:", image_file, "name:", name, "birthdate:", birthdate)

        # === Comment phần xử lý upload + tạo artist ===

        # from backend_django.utils.cloudinary import upload_to_cloudinary
        # import datetime

        # image_url = upload_to_cloudinary(image_file)

        # artist = Artist(
        #     name=name,
        #     birthdate=datetime.datetime.strptime(birthdate, "%Y-%m-%d"),
        #     imageUrl=image_url
        # )
        # artist.save()

        return JsonResponse({'message': 'artist'}, status=201)
    except Exception as e:
        print("Error in create_artist", e)
        return JsonResponse({'error': str(e)}, status=500)
