from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from pymongo import MongoClient
import os
import json
from ..models.user import User
from datetime import datetime
from django.conf import settings



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
    if request.method == 'POST':
        try:
            
            data = json.loads(request.body)

            clerk_id = data.get("id")
            first_name = data.get("firstName", "")
            last_name = data.get("lastName", "")
            image_url = data.get("imageUrl", "")

            if not clerk_id or not image_url:
                return JsonResponse({"success": False, "message": "Missing required fields"}, status=400)

            full_name = f"{first_name} {last_name}".strip()

            # Kiểm tra tồn tại
            user = User.objects(clerkId=clerk_id).first()
            print(user)

            if not user:
                # Tạo mới nếu chưa có
                User(
                    clerkId=clerk_id,
                    fullName=full_name,
                    imageUrl=image_url
                ).save()

            return JsonResponse({"success": True}, status=200)

        except Exception as e:
            print("Error in auth_callback:", e)
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)


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


@csrf_exempt
# @api_view(['GET'])
def check_admin(request):
    try:
        email= request.auth.get('email')
        # Kiểm tra xem email của người dùng có trùng với email admin không
        is_admin = settings.ADMIN_EMAIL == email
        if not is_admin:
            return JsonResponse({
                'admin': False,
                'message': 'Unauthorized - bạn phải là admin'
            }, status=403)

        return JsonResponse({
            'admin': True,
            'message': 'Bạn là admin'
        })

    except User.DoesNotExist:
        return JsonResponse({
            'admin': False,
            'message': 'Không tìm thấy người dùng'
        }, status=404)

    except Exception as e:
        return JsonResponse({
            'admin': False,
            'message': str(e)
        }, status=500)

