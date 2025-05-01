from django.http import JsonResponse
from ..models.user import User
from ..models.message import Message

# Fake middleware to simulate req.auth.userId (bạn có thể thay bằng JWT auth sau này)
def get_fake_current_user_id(request):
    return request.GET.get('userId', 'fake_user_id')

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

def get_messages(request, user_id):
    try:
        my_id = get_fake_current_user_id(request)
        messages = Message.objects.filter(
            __raw__={
                "$or": [
                    {"senderId": user_id, "receiverId": my_id},
                    {"senderId": my_id, "receiverId": user_id},
                ]
            }
        ).order_by('createdAt')
        messages_data = [serialize_document(m) for m in messages]
        return JsonResponse(messages_data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def check_premium_status(request):
    print(request, "check_premium_status")
    return JsonResponse({"isPremium": "Chuaw có"}) 
