from django.contrib import admin
from django.urls import path
from .views import userView,statView,artistView,adminView,testView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Lấy danh sách bài hát
    path('api/songs/', artistView.get_all_artists),

    # Lấy tất cả user
    path('api/users/', userView.get_all_users),

    # Lấy tin nhắn giữa current user và user khác (cần đăng nhập)
    path('api/users/messages/<int:user_id>/', userView.get_messages),

    #STATS
    path('api/stats', statView.get_counts, name='get_countUserArtistsAlbumsSongs'),
    # #ADMIN
    # path('api/admin/check',adminView.checkAdmin, name='admin_check'),
    path("api/admin/songs", adminView.create_song ,name='admin_create_song'),
    path("api/admin/songs/<str:id>", adminView.update_song,name='admin_update_song'),
    # path("api/admin/artists", artistView.createArtist,name='admin_create_artist'),
    path("api/admin/songs/<str:song_id>", adminView.delete_song ,name='admin_delete_song'),
    path("api/admin/albums", adminView.createAlbum ,name='admin_create_album'),
    path("api/admin/albums/<str:album_id>", adminView.delete_album, name='admin_delete_album'),
    # path('test-upload/', testView.test_upload),

]
