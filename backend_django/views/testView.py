# users/views.py
import os
import requests
from dotenv import load_dotenv
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Tải các biến môi trường từ tệp .env
load_dotenv()

CLERK_API_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_BASE_URL = "https://api.clerk.dev/v1"

# Header cho API của Clerk
headers = {
    "Authorization": f"Bearer {CLERK_API_KEY}",
    "Content-Type": "application/json"
}

def get_admin_user():
    try:
        url = f"{CLERK_BASE_URL}/users"
        response = requests.get(url, headers=headers)
        
        # Kiểm tra status code của phản hồi
        if response.status_code == 200:
            users = response.json()
            for user in users:
                if user.get("email_addresses", [{}])[0].get("email_address") == os.getenv("ADMIN_EMAIL"):
                    return user
            return None
        else:
            return None  
    except Exception as e:
        print(f"Error while fetching admin user: {str(e)}")
        return None

@csrf_exempt
def check_admin_view(request):
    if request.method != "":
        return JsonResponse({"error": "Only POST allowed"}, status=405)
    try:
        user = get_admin_user()
        if user:
            return JsonResponse({
                "admin": True,
                "message": "You are an admin",
                "user_id": user["id"],
                "email": user["email_addresses"][0]["email_address"],
                "first_name": user["first_name"],
                "last_name": user["last_name"]
            })
        else:
            return JsonResponse({"admin": False, "message": "Admin user not found"}, status=404)

    except Exception as e:
        print(f"Error in check_admin_view: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)
    
@api_view(['GET', 'OPTIONS'])
def test_cors(request):
    return Response({"message": "CORS test endpoint"})