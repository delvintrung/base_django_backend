from django.http import JsonResponse
from ..models.song import Song
from ..models.artist import Artist
from ..models.user import User
from ..models.album import Album

from mongoengine.queryset.visitor import Q

def get_counts(request):
    print("Bắt đầu hàm get_counts")
    try:
        album_count = Album.objects.count()

        artist_count = Artist.objects.count()

        user_count = User.objects.count()

        song_count = Song.objects.count()

        print("Albums list:", list(Album.objects.all()))

        return JsonResponse({
            'totalAlbums': album_count,
            'totalSongs': song_count,
            'totalUsers': user_count,
            'totalArtists': artist_count,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
