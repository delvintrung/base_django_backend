import cloudinary
from cloudinary.uploader import upload
from django.http import JsonResponse
from ..models.song import Song
from ..models.artist import Artist
from ..models.user import User
from django.views.decorators.csrf import csrf_exempt
from ..models.album import Album
import json
from django.core.files.uploadedfile import UploadedFile

# Function to upload files to Cloudinary
@csrf_exempt
def upload_to_cloudinary(file: UploadedFile, folder="songs/source"):
    try:
        result = cloudinary.uploader.upload(
            file,
            resource_type="auto",  # Automatically detect the resource type (image, video, etc.)
            folder=folder  # Set the folder for the upload
        )
        # Return the secure URL of the uploaded file
        print(result.get("secure_url"))
        return result.get("secure_url")
    except Exception as e:
        print("Error uploading to Cloudinary:", e)
        return None
    
# Endpoint for testing the file upload
@csrf_exempt
def test_upload(request):
    if request.method == 'POST':
        file = request.FILES.get('file')  # The key is 'file' from the form data
        if not file:
            return JsonResponse({'message': 'No file uploaded'}, status=400)

        # Call the upload function to Cloudinary
        url = upload_to_cloudinary(file)
        
        if url:
            return JsonResponse({'message': 'Upload successful', 'url': url}, status=200)
        else:
            return JsonResponse({'message': 'Upload failed'}, status=500)
