from django.contrib import admin
from django.urls import path
from .views import adminView, artistView,favoriteView,userView,authView,songView # nếu có view này ở cùng cấp
from django.urls import include 
from django.http import JsonResponse

def home(request):
    return JsonResponse({"message": "Welcome to the API!"})

api_urlpatterns  = [
    path('', home),
    
    #ADMIN
    path('admin/', admin.site.urls),
    path('admin/check-admin', adminView.check_admin, name='check_admin'),

    #USER
    path('users/', userView.get_all_users),
    path('auth/callback', authView.auth_callback, name='auth_callback'),
    path('admin/users/update/<str:user_id>', adminView.update_user, name='update_user'),
    path('admin/users/delete/<str:user_id>', adminView.delete_user, name='delete_user'),
    path('users/check-premium', userView.get_user_by_user_id, name='get_user_by_user_id'),
    path('users/buy-premium', userView.buy_premium_success, name='buy_premium_success'),


    # MESSAGE
    path('users/messages/<str:clerk_id>', userView.get_messages,name='get_messages'),
    
    #FAVORITE
    path('favorites/favorite/', favoriteView.get_favorite_by_id,name='get_favorite_by_id'),
    path('favorites/add', favoriteView.add_to_favorite,name='add_to_favorite'),
    path('favorites/remove', favoriteView.remove_favorite,name='remove_favorite'),
    
    # SONG
    path('songs/', artistView.get_all_artists,name='get_all_artists'),
    path('songs/featured', favoriteView.get_featured_songs,name='get_featured_songs'),
    path('songs/trending', songView.get_trending_songs, name='get_trending_songs'),
    path('songs/made-for-you', favoriteView.get_made_for_you_songs,name='get_made_for_you_songs'),
    path('admin/songs/create/', adminView.create_song, name='create_song'),
    path('admin/songs/<str:song_id>/update', adminView.update_song, name='update_song'),
    path('admin/songs/<str:song_id>/delete', adminView.delete_song, name='delete_song'),
    
    # ARTIST
    path('artists/', artistView.get_all_artists),
    path('admin/artists/create', adminView.create_artist),
    path('admin/artists/update/<str:artist_id>', adminView.update_artist, name='update_artist'),  
    path('admin/artists/delete/<str:artist_id>', adminView.delete_artist, name='delete_artist'),

]
urlpatterns = [
    path('api/', include(api_urlpatterns)),
]
