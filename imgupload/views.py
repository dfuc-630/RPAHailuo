from django.shortcuts import render

import os
import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view
from urllib.parse import urlparse

@api_view(['POST'])
def upload_image_from_url(request):
    image_url = request.data.get('image_url')
    callback_url = request.data.get('callback_url')

    if not image_url:
        return JsonResponse({'error': 'No image URL provided'}, status=400)

    try:
        # Tải ảnh
        response = requests.get(image_url, stream=True)
        if response.status_code != 200:
            return JsonResponse({'error': 'Failed to download image'}, status=400)

        # Tên file
        parsed_url = urlparse(image_url)
        filename = os.path.basename(parsed_url.path)

        # Lưu file
        save_dir = r'D:\Intern\ImageToVideo\imgvideo\dev\img'
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, filename)

        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

        # Gửi callback nếu có
        if callback_url:
            try:
                callback_data = {
                    'status': 'success',
                    'filename': filename,
                    'path': save_path
                }
                cb_response = requests.post(callback_url, json=callback_data)
                cb_response.raise_for_status()
            except Exception as cb_err:
                return JsonResponse({'warning': 'Image saved but callback failed', 'error': str(cb_err)}, status=207)

        return JsonResponse({'message': 'Image downloaded and saved', 'filename': filename})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
