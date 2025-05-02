import jwt
import requests
from django.http import HttpRequest
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

class ClerkAuthMiddleware(MiddlewareMixin):
    def process_request(self, request: HttpRequest):
        # Khởi tạo request.auth mặc định là None
        request.auth = None

        # Lấy token từ header Authorization
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return None

        try:
            payload = jwt.decode(token, options={"verify_signature": False})  # Clerk không yêu cầu verify ở client-side
            clerk_id = payload.get('sub')
            if not clerk_id:
                return None 

            clerk_api_url = f"https://api.clerk.dev/v1/users/{clerk_id}"
            headers = {
                'Authorization': f'Bearer {settings.CLERK_API_KEY}',
                'Content-Type': 'application/json'
            }
            response = requests.get(clerk_api_url, headers=headers)
            response.raise_for_status()  # Ném lỗi nếu request thất bại

            user_data = response.json()
            # Lấy email từ user_data
            # Theo tài liệu Clerk, email thường nằm trong email_addresses
            email = None
            for email_address in user_data.get('email_addresses', []):
                if email_address.get('id') == user_data.get('primary_email_address_id'):
                    email = email_address.get('email_address')
                    break

            if not email:
                # Nếu không tìm thấy email chính, lấy email đầu tiên (nếu có)
                email_addresses = user_data.get('email_addresses', [])
                email = email_addresses[0].get('email_address') if email_addresses else None

            # Tạo auth object và gắn vào request.auth
            request.auth = {
                'userId': clerk_id,
                'email': email or 'Unknown Email'
            }

        except jwt.InvalidTokenError:
            print("Invalid token")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching user from Clerk: {str(e)}")
            return None
        except Exception as e:
            print(f"Error in ClerkAuthMiddleware: {str(e)}")
            return None

        return None