from django.contrib import admin
from django.urls import path
from .views import artistView  # nếu có view này ở cùng cấp
from .views import userView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Lấy danh sách bài hát
    path('api/songs/', artistView.get_all_artists),

    # Lấy tất cả user
    path('api/users/', userView.get_all_users),

    # Lấy tin nhắn giữa current user và user khác (cần đăng nhập)
    path('api/users/messages/<int:user_id>/', userView.get_messages),
]
