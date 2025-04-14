from django.contrib import admin
from django.urls import path
from .views import artistView  # nếu có view này ở cùng cấp
from .views import userView
from .views import favoriteView

from django.http import JsonResponse

def home(request):
    return JsonResponse({"message": "Welcome to the API!"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    # Lấy danh sách bài hát
    path('api/songs/', artistView.get_all_artists),

    # Lấy tất cả user
    path('api/users/', userView.get_all_users),

    # Lấy tin nhắn giữa current user và user khác (cần đăng nhập)
    path('api/users/messages/<int:user_id>/', userView.get_messages),
    #favorite
    path('favorites/favorite', favoriteView.get_favorite_by_id),
    path('favorites/add', favoriteView.add_to_favorite),
    path('favorites/remove', favoriteView.remove_favorite),
    
    # hiển thị danh sách bài đề cử
    path('songs/featured', favoriteView.get_featured_songs),
    path('songs/made-for-you', favoriteView.get_made_for_you_songs),
    #tạo nghệ sĩ
    path('artists/create', artistView.create_artist),

]
