from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from pymongo import MongoClient
import os
from datetime import datetime



@api_view(['GET'])
def protected_view(request):
    return Response({
        'message': 'This is a protected view',
        'user_id': request.user_info.get('sub')
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def public_view(request):
    return Response({
        'message': 'This is a public view'
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@csrf_exempt
def auth_callback(request):
    try:
        # Lấy thông tin người dùng từ request
        user_data = request.data
        clerk_id = user_data.get('id')
        
        if not clerk_id:
            return Response(
                {"message": "Thiếu thông tin người dùng"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Kết nối MongoDB
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client['spotify_clone']
        users_collection = db['users']

        # Kiểm tra xem người dùng đã tồn tại chưa
        existing_user = users_collection.find_one({"clerkId": clerk_id})
        
        if existing_user:
            # Cập nhật thông tin người dùng nếu cần
            users_collection.update_one(
                {"clerkId": clerk_id},
                {
                    "$set": {
                        "fullName": user_data.get('firstName', '') + ' ' + user_data.get('lastName', ''),
                        "imageUrl": user_data.get('imageUrl', ''),
                        "email": user_data.get('email', ''),
                        "updatedAt": datetime.utcnow()
                    }
                }
            )
            existing_user['_id'] = str(existing_user['_id'])
            return Response(
                {"message": "Đăng nhập thành công", "user": existing_user},
                status=status.HTTP_200_OK
            )
        else:
            # Tạo người dùng mới
            new_user = {
                "clerkId": clerk_id,
                "fullName": user_data.get('firstName', '') + ' ' + user_data.get('lastName', ''),
                "imageUrl": user_data.get('imageUrl', ''),
                "email": user_data.get('email', ''),
                "isPremium": False,
                "isAdmin": False,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
            
            result = users_collection.insert_one(new_user)
            new_user['_id'] = str(result.inserted_id)
            
            return Response(
                {"message": "Tạo tài khoản thành công", "user": new_user},
                status=status.HTTP_201_CREATED
            )

    except Exception as e:
        return Response(
            {"message": f"Lỗi: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_current_user(request):
    try:
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client['spotify_clone']
        users_collection = db['users']
        
        user = users_collection.find_one({"clerkId": request.user_info.get('sub')})
        if not user:
            return Response(
                {"message": "Không tìm thấy người dùng"},
                status=status.HTTP_404_NOT_FOUND
            )
            
        user['_id'] = str(user['_id'])
        return Response(
            {"message": "Lấy thông tin thành công", "user": user},
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        return Response(
            {"message": f"Lỗi: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def check_premium_status(request):
    try:
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client['spotify_clone']
        users_collection = db['users']
        
        user = users_collection.find_one({"clerkId": request.user_info.get('sub')})
        if not user:
            return Response(
                {"message": "Không tìm thấy người dùng"},
                status=status.HTTP_404_NOT_FOUND
            )
            
        return Response(
            {"isPremium": user.get('isPremium', False)},
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        return Response(
            {"message": f"Lỗi: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


    return JsonResponse({"error": "Method not allowed"}, status=405)

