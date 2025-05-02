from django.http import JsonResponse

class PreflightMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'OPTIONS':
            response = JsonResponse({})
            response["Access-Control-Allow-Origin"] = "http://localhost:3000"
            response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type"
            response["Access-Control-Allow-Credentials"] = "true"
            return response

        response = self.get_response(request)
        response["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response["Access-Control-Allow-Credentials"] = "true"
        return response
