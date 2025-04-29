from django.contrib import admin
from django.urls import path, include
from .views import artistView,favoriteView,userView,adminViews,albumView,songView,sampleData,authView,adminView, testView, statView

from django.http import JsonResponse
# from .views.authView import (
#     auth_callback, 
#     get_current_user, 
#     protected_view, 
#     public_view,
#     check_premium_status,
#     check_admin_status
# )

def home(request):
    return JsonResponse({"message": "Welcome to the API!"})

urlpatterns = [
    path('admin/', admin.site.urls),
    # bài hát
    path('api/songs/', songView.get_all_songs),
    path('api/songs/create', songView.create_song), 
    path('api/songs/create-sample', songView.create_sample_songs),
    path('api/songs/<str:song_id>/', songView.get_song, name='get_song'),   
    path('api/songs/delete/<str:song_id>/', songView.delete_song, name='delete_song'),  
    path('api/songs/<str:song_id>/update', songView.update_song, name='update_song'),
    path('api/songs/search', songView.search_songs, name='search_songs'),
    path('api/songs/by-artist/<str:artist_id>/', songView.get_songs_by_artist, name='get_songs_by_artist'),
    path('api/songs/by-genre/<str:genre>/', songView.get_songs_by_genre, name='get_songs_by_genre'),
    path('api/songs/recently-played/', songView.get_recently_played, name='get_recently_played'),
    path('api/songs/<str:song_id>/like', songView.like_song, name='like_song'),
    path('api/songs/<str:song_id>/unlike', songView.unlike_song, name='unlike_song'),

    #user
    # Lấy tất cả user
    path('api/users/', userView.get_all_users),
    path('auth/callback/', authView.auth_callback, name='auth_callback'),
    # path('users/update/<str:user_id>/', adminViews.update_user, name='update_user'),
    # path('users/delete/<str:user_id>/', adminViews.delete_user, name='delete_user'),

    # Lấy tin nhắn giữa current user và user khác (cần đăng nhập)
    path('api/users/messages/<int:user_id>/', userView.get_messages),
    #favorite
    path('favorites/favorite', favoriteView.get_favorite_by_id),
    path('favorites/add', favoriteView.add_to_favorite),
    path('favorites/remove', favoriteView.remove_favorite),
    
    # playlist
    # path('api/playlist/', favoriteView.get_playlist),
    # path('api/playlist/create', favoriteView.create_playlist),
    # path('api/playlist/<str:playlist_id>/', favoriteView.get_playlist_detail),
    
    # hiển thị danh sách bài đề cử
    path('api/songs/featured/', favoriteView.get_featured_songs),
    path('api/songs/made-for-you/', favoriteView.get_made_for_you_songs),
    # path('api/songs/trending/', favoriteView.get_trending_songs),
    
    #album
    path('api/albums/', albumView.get_all_albums),
    path('api/albums/<str:album_id>/', albumView.get_album, name='get_album'),  
    path('api/albums/create', adminViews.create_album),
    path('api/albums/<str:album_id>/update', albumView.update_album, name='update_album'),
    path('api/albums/<str:album_id>/delete', albumView.delete_album, name='delete_album'),
    path('api/albums/search', albumView.search_albums, name='search_albums'),
    path('api/albums/by-artist/<str:artist_id>/', albumView.get_albums_by_artist, name='get_albums_by_artist'),
    path('api/albums/recently-added/', albumView.get_recently_added, name='get_recently_added'),
    path('api/albums/<str:album_id>/like', albumView.like_album, name='like_album'),
    path('api/albums/<str:album_id>/unlike', albumView.unlike_album, name='unlike_album'),
    path('api/albums/<str:album_id>/songs', albumView.get_album_songs, name='get_album_songs'),
    # nghệ sĩ
    path('artists/', artistView.get_all_artists),
    path('artists/create', adminViews.create_artist),
    path('artists/update/<str:artist_id>/', adminViews.update_artist, name='update_artist'),  
    path('artists/delete/<str:artist_id>/', adminViews.delete_artist, name='delete_artist'),
    
    # path('songs/featured', artistView.get_featured_songs),
    # path('songs/made-for-you', artistView.get_made_for_you_songs),

    #STATS
    path('api/stats', statView.get_counts, name='get_countUserArtistsAlbumsSongs'),
    # #ADMIN
    # path('api/admin/check',adminView.checkAdmin, name='admin_check'),
    path("api/admin/create/songs", adminView.create_song ,name='admin_create_song'),
    path("api/admin/songs/<str:id>", adminView.update_song,name='admin_update_song'),
    path("api/admin/artists",adminView.createArtist,name='admin_create_artist'),
    path("api/admin/songs/delete/<str:song_id>", adminView.delete_song ,name='admin_delete_song'),
    path("api/admin/albums", adminView.createAlbum ,name='admin_create_album'),
    path("api/admin/albums/<str:album_id>", adminView.delete_album, name='admin_delete_album'),
    path('api/check-user/', testView.check_admin_view, name='check_user'),
    path("api/admin/playlists/<str:playlist_id>", adminView.delete_playlist, name='admin_delete_playlist'),

]
