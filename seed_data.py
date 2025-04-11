from mongoengine import connect
from backend_django.models import Song

connect(db="spotify", host="mongodb://localhost:27017")  # hoặc dùng os.getenv nếu muốn

# Xoá hết dữ liệu cũ và tạo mới
Song.drop_collection()

song = Song(title="Blinding Lights", artist="The Weeknd")
song.save()

print("✅ Đã thêm bài hát test vào MongoDB")
