import jwt
import requests
from django.conf import settings
from rest_framework import authentication, exceptions

class ClerkAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]

        try:
            # Lấy public keys từ Clerk (JWKS)
            jwks = requests.get("https://clerk.dev/.well-known/jwks.json").json()
            public_keys = {
                key["kid"]: jwt.algorithms.RSAAlgorithm.from_jwk(key)
                for key in jwks["keys"]
            }

            # Giải mã JWT
            unverified_header = jwt.get_unverified_header(token)
            key = public_keys[unverified_header["kid"]]

            decoded = jwt.decode(
                token,
                key=key,
                algorithms=["RS256"],
                audience=settings.CLERK_FRONTEND_API,  # hoặc your frontend API
                issuer="https://clerk.dev"
            )

            # Tùy chỉnh phần xử lý user
            from ..models.user import User
            user, _ = User.objects.get_or_create(
                clerkId=decoded["sub"],
                defaults={"primaryEmailAddress": decoded.get("email")}
            )

            return (user, None)

        except Exception as e:
            raise exceptions.AuthenticationFailed("Token không hợp lệ: " + str(e))
