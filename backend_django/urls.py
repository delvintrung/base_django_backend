from django.contrib import admin
from django.urls import path, include
from .views import artistView,favoriteView,userView,albumView,songView,authView,adminView, testView, statView, playlistView,adminPlusView, genreView

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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

api_urlpatterns  = [
    path('', home),
    
    

    #USER
    path('users', userView.get_all_users),
    path('auth/callback', authView.auth_callback, name='auth_callback'),
    # path('admin/users/update/<str:user_id>', adminView.update_user, name='update_user'),
    # path('admin/users/delete/<str:user_id>', adminView.delete_user, name='delete_user'),
    path('users/check-premium', userView.get_user_by_user_id, name='get_user_by_user_id'),
    path('users/get-csrf-token', userView.get_csrf_token, name='get_csrf_token'),
    path('users/buy-premium', userView.buy_premium_success, name='buy_premium_success'),

    # PLAYLIST

    path('playlist', playlistView.get_playlist_by_clerki_id, name='get_playlist_by_id'),
    path('playlist/<str:playlist_id>', playlistView.get_playlist_by_id, name='get_playlist_by_id'),
    path('playlists/create', playlistView.create_playlist, name='create_playlist'),
    path('playlists/add_song', playlistView.add_song_to_playlist, name='add_song_to_playlist'),

    # GENRE
    path('genres', genreView.get_all_genres, name='get_all_genres'),

    # MESSAGE
    path('users/messages/<str:clerk_id>', userView.get_messages,name='get_messages'),
    path('users/messages/send/', csrf_exempt(userView.send_message)),
    #FAVORITE
    path('favorites/favorite', favoriteView.get_favorite_by_id,name='get_favorite_by_id'),
    path('favorites/add', favoriteView.add_to_favorite,name='add_to_favorite'),
    path('favorites/remove', favoriteView.remove_favorite,name='remove_favorite'),
    
    # SONG
    path('songs/featured', songView.get_featured_songs, name='get_featured_songs'),
    path('songs/made-for-you', songView.get_featured_songs, name='get_made_for_you_songs'),
    path('songs', songView.get_all_songs),
    path('songs/<str:song_id>', songView.get_song, name='get_song'),  
    path('songs/delete/<str:song_id>', songView.delete_song, name='delete_song'),
    
    # # ARTIST
    path('artists', artistView.get_all_artists),
    path('admin/artists/create', adminPlusView.create_artist),
    path('admin/artists/update/<str:artist_id>', adminPlusView.update_artist, name='update_artist'),  
    path('admin/artists/delete/<str:artist_id>', adminPlusView.delete_artist, name='delete_artist'),

    # ALBUM
    path('albums', albumView.get_all_albums),
    path('albums/<str:album_id>', albumView.get_album, name='get_album'),  

    #STATS
    path('stats', statView.get_counts, name='get_countUserArtistsAlbumsSongs'),

    # Admin
    path('admin/check-admin',authView.check_admin, name='admin_check'),
    path('admin/playlists/<str:playlist_id>/update', playlistView.update_playlist, name='update_playlist'),


    # #ADMIN
    path("admin/create/songs", adminView.create_song ,name='admin_create_song'),
    path("admin/songs/<str:id>", adminView.update_song,name='admin_update_song'),
    path("admin/artists",adminView.createArtist,name='admin_create_artist'),
    path("admin/songs/delete/<str:song_id>", adminView.delete_song ,name='admin_delete_song'),
    path("admin/albums", adminView.createAlbum ,name='admin_create_album'),
    path("admin/albums/update/<str:album_id>", adminView.update_albumadmin ,name='adminupdatealbum'),
    path("admin/albums/<str:album_id>", adminView.delete_album, name='admin_delete_album'),
    path('check-user', testView.check_admin_view, name='check_user'),
    path("admin/playlists/<str:playlist_id>", adminView.delete_playlist, name='admin_delete_playlist'),
    path("admin/playlists/update/<str:playlist_id>", adminView.update_playlist, name='admin_update_playlist'),
]


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_urlpatterns)),
]