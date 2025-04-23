from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from mongoengine.queryset.visitor import Q
from mongoengine.errors import ValidationError as MongoValidationError
import random
from django.utils.dateparse import parse_date
import json
from bson import DBRef


from ..models.artist import Artist
from ..models.genre import Genre
from ..models.song import Song

# GET /artists
def get_all_artists(request):
    try:
        artists = Artist.objects.order_by('-createdAt')
        result = []

        for artist in artists:
            genres_data = []

            # Chuyển genre thành ObjectId (chuỗi)
            genre_ids = [str(g.id) for g in artist.genres]  # Đảm bảo việc genres là ObjectId

            # Tìm tất cả các genre tương ứng với các objectId trong genre_ids
            genres = Genre.objects(id__in=genre_ids)

            for g in genres:
                genres_data.append({
                    "id": str(g.id),
                    "name": g.name
                })

            result.append({
                "id": str(artist.id),
                "name": artist.name,
                "birthdate": str(artist.birthdate),
                "imageUrl": artist.imageUrl,
                "genres": genres_data,
            })

        return JsonResponse(result, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)




