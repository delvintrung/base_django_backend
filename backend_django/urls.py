from django.contrib import admin
from django.urls import path, include
from .views import artistView,favoriteView,userView,albumView,songView,authView,adminView, testView, statView, playlistView

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

# api_urlpatterns = [
#     path('admin/', admin.site.urls),

#     path('test-cors/', testView.test_cors, name='test-cors'),

#     # Lấy danh sách bài hát
#     path('api/songs/featured', songView.get_featured_songs),
#     path('api/songs', songView.get_all_songs),
#     path('api/songs/create', songView.create_song),
#     path('api/songs/<str:song_id>', songView.get_song, name='get_song'),  
#     path('api/songs/delete/<str:song_id>', songView.delete_song, name='delete_song'),
#     # done

#     #user
#     # Lấy tất cả user
#     path('api/users', userView.get_all_users),
#     path('api/users/check-premium', userView.check_premium_status, name='check_premium_status'),
#     path('auth/callback', authView.auth_callback, name='auth_callback'),

#     # Lấy tin nhắn giữa current user và user khác (cần đăng nhập)
#     path('api/users/messages/<int:user_id>', userView.get_messages),
#     #favorite
#     path('favorites/favorite', favoriteView.get_favorite_by_id),
#     path('favorites/add', favoriteView.add_to_favorite),
#     path('favorites/remove', favoriteView.remove_favorite),
    
#     # playlist
#     path('api/playlist', playlistView.get_playlist_by_id),
#     # path('api/playlist', playlistView.get_playlist),
#     # path('api/playlist/create', favoriteView.create_playlist),
    
#     # hiển thị danh sách bài đề cử
    
#     # path('api/songs/made-for-you/', songView.get_made_for_you_songs),
#     # path('api/songs/trending/', favoriteView.get_trending_songs),
    
#     #album
#     path('api/albums', albumView.get_all_albums),
#     path('api/albums/<str:album_id>', albumView.get_album, name='get_album'),  

#     path('api/albums/create', albumView.create_album),
#     # done
#     # nghệ sĩ
#     path('artists', artistView.get_all_artists),
#     path('artists/create', adminViews.create_artist),
#     path('artists/update/<str:artist_id>', adminViews.update_artist, name='update_artist'),  
#     path('artists/delete/<str:artist_id>', adminViews.delete_artist, name='delete_artist'),
    
#     # path('songs/featured', artistView.get_featured_songs),
#     # path('songs/made-for-you', artistView.get_made_for_you_songs),
api_urlpatterns  = [
    path('', home),
    
    #ADMIN
    path('admin/', admin.site.urls),
    path('admin/check-admin', adminView.check_admin, name='check_admin'),

    #USER
    path('users', userView.get_all_users),
    path('auth/callback', authView.auth_callback, name='auth_callback'),
    # path('admin/users/update/<str:user_id>', adminView.update_user, name='update_user'),
    # path('admin/users/delete/<str:user_id>', adminView.delete_user, name='delete_user'),
    path('users/check-premium', userView.get_user_by_user_id, name='get_user_by_user_id'),
    path('users/buy-premium', userView.buy_premium_success, name='buy_premium_success'),

    # PLAYLIST
    path('playlist', playlistView.get_playlist_by_id, name='get_playlist_by_id'),


    # MESSAGE
    path('users/messages/<str:clerk_id>', userView.get_messages,name='get_messages'),
    
    #FAVORITE
    path('favorites/favorite', favoriteView.get_favorite_by_id,name='get_favorite_by_id'),
    path('favorites/add', favoriteView.add_to_favorite,name='add_to_favorite'),
    path('favorites/remove', favoriteView.remove_favorite,name='remove_favorite'),
    
    # SONG
    path('songs/featured', songView.get_featured_songs, name='get_featured_songs'),
    path('songs/made-for-you', songView.get_featured_songs, name='get_made_for_you_songs'),
    path('songs', songView.get_all_songs),
    path('songs/create', songView.create_song),
    path('songs/<str:song_id>', songView.get_song, name='get_song'),  
    path('songs/delete/<str:song_id>', songView.delete_song, name='delete_song'),
    
    # ARTIST
    path('artists/', artistView.get_all_artists),
    path('admin/artists/create', adminView.create_artist),
    path('admin/artists/update/<str:artist_id>', adminView.update_artist, name='update_artist'),  
    path('admin/artists/delete/<str:artist_id>', adminView.delete_artist, name='delete_artist'),

    # ALBUM
    path('albums', albumView.get_all_albums),
    path('albums/<str:album_id>', albumView.get_album, name='get_album'),  

    #STATS
    path('stats', statView.get_counts, name='get_countUserArtistsAlbumsSongs'),
    # #ADMIN
    path('admin/check',adminView.check_admin, name='admin_check'),
    path("admin/create/songs", adminView.create_song ,name='admin_create_song'),
    path("admin/songs/<str:id>", adminView.update_song,name='admin_update_song'),
    path("admin/artists",adminView.createArtist,name='admin_create_artist'),
    path("admin/songs/delete/<str:song_id>", adminView.delete_song ,name='admin_delete_song'),
    path("admin/albums", adminView.createAlbum ,name='admin_create_album'),
    path("admin/albums/<str:album_id>", adminView.delete_album, name='admin_delete_album'),
    path('check-user', testView.check_admin_view, name='check_user'),
    path("admin/playlists/<str:playlist_id>", adminView.delete_playlist, name='admin_delete_playlist'),
]


urlpatterns = [
    path('api/', include(api_urlpatterns)),
]
