from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..models.album import Album
from ..models.song import Song
from ..models.artist import Artist
from bson import ObjectId
import random
import json
from datetime import datetime
from bson import ObjectId
from mongoengine import Document

def serialize_document(doc):
    if isinstance(doc, Document):
        doc = doc.to_mongo().to_dict()

    serialized = {}

    for key, value in doc.items():
        if isinstance(value, ObjectId):
            serialized[key] = str(value)
        elif isinstance(value, datetime):
            serialized[key] = value.isoformat()
        elif isinstance(value, Document):
            serialized[key] = serialize_document(value)
        elif isinstance(value, list):
            serialized[key] = [
                serialize_document(item) if isinstance(item, Document)
                else str(item) if isinstance(item, ObjectId)
                else item
                for item in value
            ]
        else:
            serialized[key] = value

    return serialized

@csrf_exempt
def get_all_albums(request):
    try:
        albums = Album.objects.all()
        albums_data = []
        for album in albums:
            album_dict = album.to_mongo().to_dict()
            # Chuyển đổi _id thành string
            album_dict['_id'] = str(album_dict['_id'])
            # Xử lý trường artist
            if 'artist' in album_dict:
                try:
                    artist = album.artist.fetch()
                    album_dict['artist'] = {
                        '_id': str(artist.id),
                        'name': artist.name,
                        'imageUrl': artist.imageUrl
                    }
                except:
                    # Nếu không tìm thấy artist, sử dụng thông tin mặc định
                    album_dict['artist'] = {
                        '_id': str(album_dict['artist']),
                        'name': 'Unknown Artist',
                        'imageUrl': ''
                    }
            # Xử lý trường songs
            if 'songs' in album_dict:
                album_dict['songs'] = [str(song_id) for song_id in album_dict['songs']]
            albums_data.append(album_dict)
        return JsonResponse(albums_data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_album(request, album_id):
    try:
        album = Album.objects.get(id=ObjectId(album_id))
        album_data = serialize_document(album)
        return JsonResponse(album_data)
    except Album.DoesNotExist:
        return JsonResponse({'error': 'Album not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_featured_albums(request):
    try:
        all_albums = list(Album.objects.all())
        sampled_albums = random.sample(all_albums, min(6, len(all_albums)))

        result = []
        for album in sampled_albums:
            artist = album.artist.fetch() if album.artist else None
            result.append({
                "_id": str(album.id),
                "title": album.title,
                "artist": serialize_document(artist) if artist else None,
                "imageUrl": album.imageUrl,
                "releaseYear": album.releaseYear,
            })

        return JsonResponse(result, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def create_album(request):
    try:
        if request.method != 'POST':
            return JsonResponse({'message': 'Method not allowed'}, status=405)

        # Đọc dữ liệu JSON từ request body
        data = json.loads(request.body)

        # Lấy các trường từ dữ liệu
        title = data.get('title')
        artistId = data.get('artistId')
        releaseYear = data.get('releaseYear')
        imageUrl = data.get('imageUrl')

        # Kiểm tra nếu thiếu bất kỳ trường nào
        if not title or not artistId or not releaseYear or not imageUrl:
            return JsonResponse({'error': 'Missing required fields: title, artistId, releaseYear, imageUrl'}, status=400)

        # Tạo album
        album = Album(
            title=title,  # Lưu lại tên album vào trường 'title'
            artist=ObjectId(artistId),  # Chuyển artistId thành ObjectId nếu cần
            releaseYear=releaseYear,
            imageUrl=imageUrl
        )
        album.save()

        return JsonResponse({'message': 'Album created successfully', 'id': str(album.id)}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_album_songs(request, album_id):
    try:
        album = Album.objects.get(id=ObjectId(album_id))
        songs = Song.objects.filter(albumId=album)
        songs_data = [serialize_document(s) for s in songs]
        return JsonResponse(songs_data, safe=False)
    except Album.DoesNotExist:
        return JsonResponse({'error': 'Album not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['PUT'])
def update_album(request, album_id):
    try:
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client['spotify']
        albums_collection = db['albums']
        
        update_data = request.data
        result = albums_collection.update_one(
            {"_id": album_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return Response({"message": "Cập nhật album thành công"}, status=status.HTTP_200_OK)
        return Response({"message": "Không tìm thấy album"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def delete_album(request, album_id):
    try:
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client['spotify']
        albums_collection = db['albums']
        
        result = albums_collection.delete_one({"_id": album_id})
        
        if result.deleted_count > 0:
            return Response({"message": "Xóa album thành công"}, status=status.HTTP_200_OK)
        return Response({"message": "Không tìm thấy album"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def search_albums(request):
    try:
        query = request.GET.get('q', '')
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client['spotify']
        albums_collection = db['albums']
        
        albums = albums_collection.find({
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"artist": {"$regex": query, "$options": "i"}}
            ]
        })
        
        return Response(list(albums), status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_albums_by_artist(request, artist_id):
    try:
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client['spotify']
        albums_collection = db['albums']
        
        albums = albums_collection.find({"artist_id": artist_id})
        return Response(list(albums), status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_recently_added(request):
    try:
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client['spotify']
        albums_collection = db['albums']
        
        albums = albums_collection.find().sort("created_at", -1).limit(20)
        return Response(list(albums), status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def like_album(request, album_id):
    try:
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client['spotify']
        likes_collection = db['album_likes']
        
        likes_collection.insert_one({
            "user_id": request.user_info.get('sub'),
            "album_id": album_id,
            "created_at": datetime.utcnow()
        })
        
        return Response({"message": "Đã thích album"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def unlike_album(request, album_id):
    try:
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client['spotify']
        likes_collection = db['album_likes']
        
        result = likes_collection.delete_one({
            "user_id": request.user_info.get('sub'),
            "album_id": album_id
        })
        
        if result.deleted_count > 0:
            return Response({"message": "Đã bỏ thích album"}, status=status.HTTP_200_OK)
        return Response({"message": "Không tìm thấy lượt thích"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  