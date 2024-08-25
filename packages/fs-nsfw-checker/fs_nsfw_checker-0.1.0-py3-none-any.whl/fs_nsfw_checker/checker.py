import requests
from PIL import Image
import io

def checkNSFW(garment: Image.Image, model: Image.Image, result: Image.Image, description: str, category: str):
    # Step 1: Get upload URLs
    upload_response = requests.post('https://api.fitsnap.io/nsfw-checker/upload')
    upload_data = upload_response.json()
    
    # Step 2: Upload images
    for image_type, image in [('garment', garment), ('model', model), ('image', result)]:
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        requests.put(upload_data[image_type], data=img_byte_arr, headers={'Content-Type': 'image/png'})
    
    # Step 3: Initiate check
    check_data = {
        'id': upload_data['id'],
        'description': description,
        'category': category
    }
    requests.post('https://api.fitsnap.io/nsfw-checker/check', json=check_data)
    
    # Function returns immediately without waiting for the result
    return
