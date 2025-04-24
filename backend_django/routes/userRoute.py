from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models.user import User
from ..models.message import Message

@api_view(['GET'])
def get_all_users(request):
    users = User.objects.all().values("id", "username")  # tuỳ field bạn có
    return Response(list(users))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages(request, user_id):
    messages = Message.objects.filter(
        sender_id=request.user.id, receiver_id=user_id
    ).values("id", "content", "created_at")

    return Response(list(messages))
