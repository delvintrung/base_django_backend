from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..models.artist import Artist
from ..models.genre import Genre
from ..models.song import Song
from mongoengine.queryset.visitor import Q
import random
from datetime import datetime


def serialize_document(artist):
    data = artist.to_mongo().to_dict()
    data['_id'] = str(data['_id'])

    # ISO format cho datetime
    if 'createdAt' in data and isinstance(data['createdAt'], datetime):
        data['createdAt'] = data['createdAt'].isoformat()
    if 'updatedAt' in data and isinstance(data['updatedAt'], datetime):
        data['updatedAt'] = data['updatedAt'].isoformat()

    return data


@csrf_exempt
@csrf_exempt
def get_all_artists(request):
    try:
        artists = Artist.objects.all()
        artist_list = []

        for artist in artists:
            genres_data = []
            if artist.genres:
                for genre in artist.genres:
                    try:
                        genres_data.append({
                           
                            'name': genre.name
                        })
                    except Exception:
                        genres_data.append({
                            '_id': None,
                            'name': "Unknown Genre"
                        })

            artist_list.append({
                '_id': str(artist.id),
                'name': artist.name,
                'birthdate': str(artist.birthdate) if artist.birthdate else None,
                'imageUrl': artist.imageUrl,
                'createdAt': artist.createdAt.isoformat() if artist.createdAt else None,
                'updatedAt': artist.updatedAt.isoformat() if artist.updatedAt else None,
                'listeners': artist.listeners,
                'followers': artist.followers,
                'description': artist.description,
                'genres': genres_data,  # gồm cả _id và name
            })

        return JsonResponse(artist_list, safe=False)
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
