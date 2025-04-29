import os
import requests
from django.http import JsonResponse
from dotenv import load_dotenv

load_dotenv()

CLERK_API_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_BASE_URL = "https://api.clerk.dev/v1"

# Header cho API của Clerk
headers = {
    "Authorization": f"Bearer {CLERK_API_KEY}",
    "Content-Type": "application/json"
}
def protect_route(request):
    try:
        url = f"{CLERK_BASE_URL}/users"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return JsonResponse({ "message": "Failed to fetch users from Clerk"}, status=response.status_code)

        users = response.json()
        if not users:
            return JsonResponse({ "message": "Unauthorized - you must be logged in"}, status=401)

        return JsonResponse({ "message": "You are an admin"}, status=200)

    except requests.RequestException as e:
        return JsonResponse({ "message": f"Error connecting to Clerk: {str(e)}"}, status=500)


def require_admin(request):
    try:
        url = f"{CLERK_BASE_URL}/users"
        response = requests.get(url, headers=headers)
        
        # Kiểm tra status code của phản hồi
        if response.status_code == 200:
            users = response.json()
            for user in users:
                if not user.get("email_addresses", [{}])[0].get("email_address") == os.getenv("ADMIN_EMAIL"):
                    return JsonResponse({ "message": "Unauthorized - you must be logged in"}, status=401)
        else:
            return None  
    except Exception as e:
        print(f"Error while fetching admin user: {str(e)}")
        return None
    