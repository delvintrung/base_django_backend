from django.http import JsonResponse
from ..models.song import Song
from ..models.artist import Artist
from ..models.user import User
from ..models.album import Album
import requests
import os
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

from mongoengine.queryset.visitor import Q


CLERK_API_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_BASE_URL = "https://api.clerk.dev/v1"

headers = {
    "Authorization": f"Bearer {CLERK_API_KEY}",
    "Content-Type": "application/json"
}
def token_required(f):
    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        token = request.headers.get("Authorization")
     
        if not token:
            return JsonResponse({"error": "Authorization token is missing."}, status=401)
        
        token = token.split(" ")[1] if "Bearer " in token else token
        print( token) 
        try:
            response = requests.post(
                f"{CLERK_BASE_URL}/tokens/verify", 
                json={"token": token}, 
                headers=headers
            )
            print(response.status_code)
        except Exception as e:
            print(f"Clerk API error: {str(e)}")
            return JsonResponse({"error": "Clerk API error", "detail": str(e)}, status=500)

        # if response.status_code != 200:
        #     return JsonResponse({"error": "Invalid or expired token."}, status=401)

        # Đảm bảo phản hồi là JSON
        if "application/json" not in response.headers.get("Content-Type", ""):
            return JsonResponse({"error": "Invalid response format from Clerk."}, status=500)

        try:
            user_data = response.json()
        except Exception as e:
            return JsonResponse({"error": "Failed to parse Clerk response", "detail": str(e)}, status=500)

        print("Thông tin token từ Clerk:", user_data)

        request.clerk_user = user_data  # lưu thông tin user vào request nếu muốn dùng tiếp
        return f(request, *args, **kwargs)

    return decorated_function



@csrf_exempt
# @token_required   
def get_counts(request):
    try:
        album_count = Album.objects.count()
        artist_count = Artist.objects.count()
        user_count = User.objects.count()
        song_count = Song.objects.count()
        return JsonResponse({
            'totalAlbums': album_count,
            'totalSongs': song_count,
            'totalUsers': user_count,
            'totalArtists': artist_count,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
