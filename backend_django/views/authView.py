from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from ..models.user import User  # Đổi nếu bạn để chỗ khác

@csrf_exempt
def auth_callback(request):
    if request.method == 'POST':
        try:
            # Parse body JSON
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
