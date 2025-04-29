from django.http import JsonResponse
from ..models.song import Song
import random

def get_trending_songs(request):
    try:
        # Lấy tất cả bài hát
        all_songs = list(Song.objects)

        # Random lấy 4 bài hát bất kỳ
        sampled_songs = random.sample(all_songs, min(len(all_songs), 4))

        # Format lại dữ liệu giống như Node.js đang làm
        result = []
        for song in sampled_songs:
            artist = song.artist  # ReferenceField sẽ tự động fetch
            song_data = {
                '_id': str(song.id),  # MongoEngine ObjectId thành string
                'title': song.title,
                'artist': {
                    '_id': str(artist.id) if artist else None,
                    'name': artist.name if artist else None,
                    'imageUrl': artist.imageUrl if artist else None,
                },
                'imageUrl': song.imageUrl,
                'audioUrl': song.audioUrl,
                'videoUrl': getattr(song, 'videoUrl', None),  # Nếu có trường videoUrl
                'description': getattr(song, 'description', None),  # Nếu có trường description
                'followers': getattr(song, 'followers', 0),
                'listeners': getattr(song, 'listeners', 0),
                'premium': getattr(song, 'premium', False),
            }
            result.append(song_data)

        return JsonResponse(result, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
