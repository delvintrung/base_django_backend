from django.contrib import admin
from django.urls import path
from .views import artistView,favoriteView,userView,adminViews # nếu có view này ở cùng cấp

from django.http import JsonResponse

def home(request):
    return JsonResponse({"message": "Welcome to the API!"})

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    # bài hát
    path('api/songs/', artistView.get_all_artists),
    

    #user
    # Lấy tất cả user
    path('api/users/', userView.get_all_users),
    path('users/update/<str:user_id>/', adminViews.update_user, name='update_user'),
    path('users/delete/<str:user_id>/', adminViews.delete_user, name='delete_user'),

    # Lấy tin nhắn giữa current user và user khác (cần đăng nhập)
    path('api/users/messages/<int:user_id>/', userView.get_messages),
    #favorite
    path('favorites/favorite', favoriteView.get_favorite_by_id),
    path('favorites/add', favoriteView.add_to_favorite),
    path('favorites/remove', favoriteView.remove_favorite),
    
    # hiển thị danh sách bài đề cử
    path('songs/featured', favoriteView.get_featured_songs),
    path('songs/made-for-you', favoriteView.get_made_for_you_songs),
    
    # nghệ sĩ
    path('artists/', artistView.get_all_artists),
    path('artists/create', adminViews.create_artist),
    path('artists/update/<str:artist_id>/', adminViews.update_artist, name='update_artist'),  
    path('artists/delete/<str:artist_id>/', adminViews.delete_artist, name='delete_artist'),
    
    # path('songs/featured', artistView.get_featured_songs),
    # path('songs/made-for-you', artistView.get_made_for_you_songs),

]
