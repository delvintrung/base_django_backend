from django.http import JsonResponse
from django.conf import settings
import requests
from ..models.user import User
from ..models.message import Message

# Hàm đọc session hoặc header chứa token xác thực Clerk
def get_clerk_token(request):
    return request.headers.get('Authorization')  # Bearer <token>

def get_me(request):
    try:
        # Lấy token từ header Authorization
        token = get_clerk_token(request)
        if not token:
            return JsonResponse({'message': 'Not authenticated'}, status=401)

        # Clerk API endpoint để lấy user info
        clerk_user_url = "https://api.clerk.dev/v1/me"

        # Gửi request đến Clerk API
        response = requests.get(
            clerk_user_url,
            headers={
                "Authorization": token,
                "Content-Type": "application/json",
            }
        )

        if response.status_code != 200:
            return JsonResponse({'message': 'Failed to fetch user info from Clerk'}, status=response.status_code)

        user = response.json()

        return JsonResponse({
            "id": user.get("id"),
            "firstName": user.get("first_name"),
            "lastName": user.get("last_name"),
            "imageUrl": user.get("image_url"),
            "emailAddress": user.get("primary_email_address", {}).get("email_address"),
        }, status=200)

    except Exception as e:
        return JsonResponse({'message': str(e)}, status=500)

# Fake middleware to simulate req.auth.userId (bạn có thể thay bằng JWT auth sau này)
def get_fake_current_user_id(request):
    clerk_id = request.auth.get('userId') 
    if not clerk_id:
        raise ValueError("Missing clerkId in request URL")
    
    user = User.objects(clerkId=clerk_id).first()
    if not user:
        raise ValueError("User not found with provided clerkId")
    
    return str(user.id)


def serialize_document(doc):
    """Chuyển đổi Document MongoEngine sang dict và ép _id thành string"""
    d = doc.to_mongo().to_dict()
    if '_id' in d:
        d['_id'] = str(d['_id'])
    return d

def get_all_users(request):
    try:
        current_user_id = get_fake_current_user_id(request)
        users = User.objects(clerkId__ne=current_user_id)
        # Sử dụng helper để serialize
        users_data = [serialize_document(u) for u in users]
        return JsonResponse(users_data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_messages(request, clerk_id):
    try:
        my_id = get_fake_current_user_id(request)

        # Tìm user_id tương ứng với clerk_id của người đối thoại
        target_user = User.objects(clerkId=clerk_id).first()
        if not target_user:
            return JsonResponse({'error': 'Target user not found with provided clerkId'}, status=404)

        target_user_id = str(target_user.id)

        messages = Message.objects.filter(
            __raw__={
                "$or": [
                    {"senderId": target_user_id, "receiverId": my_id},
                    {"senderId": my_id, "receiverId": target_user_id},
                ]
            }
        ).order_by('createdAt')

        messages_data = [serialize_document(m) for m in messages]
        return JsonResponse(messages_data, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_user_by_user_id(request):
    try:
        user_id = request.auth.get('userId')  # Assuming the userId is retrieved from auth middleware
         # Assuming the userId is retrieved from auth middleware
        user = User.objects.filter(clerkId=user_id).first()
        
        if not user:
            return JsonResponse({'message': 'User not found'}, status=404)
        
        user_data = {
            'id': str(user.id),
            'fullName': user.fullName,
            'imageUrl': user.imageUrl,
            'clerkId': user.clerkId,
            'createdAt': user.createdAt,
            'updatedAt': user.updatedAt,
            'isPremium': user.isPremium if user.isPremium else False,
            # Add more fields as needed
        }
        
        return JsonResponse(user_data, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



def buy_premium_success(request):
    try:
        user_id = request.user.id  # Assuming the userId is retrieved from auth middleware

        if user_id:
            user = User.objects.filter(clerkId=user_id).first()

            if not user:
                return JsonResponse({'message': 'User not found'}, status=404)

            # Update premium status
            user.isPremium = True
            user.save()

            return JsonResponse({'message': 'Premium status updated', 'userId': str(user.id)}, status=200)

        return JsonResponse({'message': 'User not authenticated'}, status=400)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def check_premium_status(request):
    print(request, "check_premium_status")
    return JsonResponse({"isPremium": "Chuaw có"}) 
