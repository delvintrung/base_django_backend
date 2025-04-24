from django.contrib import admin
from django.urls import path, include
from .views import artistView,favoriteView,userView,adminViews,authView,albumView,songView # nếu có view này ở cùng cấp

from django.http import JsonResponse
from .views.authView import (
    auth_callback, 
    get_current_user, 
    protected_view, 
    public_view,
    check_premium_status,
    check_admin_status
)

def home(request):
    return JsonResponse({"message": "Welcome to the API!"})

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    # bài hát
    path('api/songs/', artistView.get_all_artists),
    path('api/songs/create', songView.create_song),
    path('api/songs/<str:song_id>/', songView.get_song, name='get_song'),  
    path('api/songs/delete/<str:song_id>/', songView.delete_song, name='delete_song'),

    #user
    # Lấy tất cả user
    path('api/users/', userView.get_all_users),
    path('auth/callback/', authView.auth_callback, name='auth_callback'),
    path('users/update/<str:user_id>/', adminViews.update_user, name='update_user'),
    path('users/delete/<str:user_id>/', adminViews.delete_user, name='delete_user'),

    # Lấy tin nhắn giữa current user và user khác (cần đăng nhập)
    path('api/users/messages/<int:user_id>/', userView.get_messages),
    #favorite
    path('favorites/favorite', favoriteView.get_favorite_by_id),
    path('favorites/add', favoriteView.add_to_favorite),
    path('favorites/remove', favoriteView.remove_favorite),
    
    # playlist
    path('api/playlist/', favoriteView.get_playlist),
    path('api/playlist/create', favoriteView.create_playlist),
    path('api/playlist/<str:playlist_id>/', favoriteView.get_playlist_detail),
    
    # hiển thị danh sách bài đề cử
    path('api/songs/featured/', favoriteView.get_featured_songs),
    path('api/songs/made-for-you/', favoriteView.get_made_for_you_songs),
    path('api/songs/trending/', favoriteView.get_trending_songs),
    
    #album
    path('api/albums/', albumView.get_all_albums),
    path('api/albums/<str:album_id>/', albumView.get_album, name='get_album'),  
    path('api/albums/create', adminViews.create_album),
    path('api/songs/made-for-you', albumView.get_all_albums),
    path('api/albums/<str:album_id>/songs', albumView.get_album_songs, name='get_album_songs'),
    # nghệ sĩ
    path('artists/', artistView.get_all_artists),
    path('artists/create', adminViews.create_artist),
    path('artists/update/<str:artist_id>/', adminViews.update_artist, name='update_artist'),  
    path('artists/delete/<str:artist_id>/', adminViews.delete_artist, name='delete_artist'),
    
    # path('songs/featured', artistView.get_featured_songs),
    # path('songs/made-for-you', artistView.get_made_for_you_songs),

    
]
