import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..models.genre import Genre


def get_all_genres(request):
    try:
        genres = Genre.objects.all()
        genres_data = []
        for genre in genres:
            genre_dict = genre.to_mongo().to_dict()
            # Chuyển đổi _id thành string
            genre_dict['_id'] = str(genre_dict['_id'])
            
            genres_data.append(genre_dict)
        return JsonResponse(genres_data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)