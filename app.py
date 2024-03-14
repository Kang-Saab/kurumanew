import requests
from PIL import Image
import io
import base64

# API endpoint
url = 'https://8dc4-34-32-235-222.ngrok-free.app/generate_images'

# Request data
data = {
    "prompt": "the beach view,no humans, from the top view, wideangle, realistic, 8K, masterpiece, ultradetailed",
    "h": 800,
    "w": 1200,
    "steps": 25,
    "guidance": 7.5,
    "lora_weight": 0,
    "num_images": 3,
    "neg": "easynegative, human, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worstquality, low quality, normal quality, jpegartifacts, signature, watermark, username, blurry, bad feet, cropped, poorly drawn hands, poorly drawn face, mutation, deformed, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, extra fingers, fewer digits, extra limbs, extra arms,extra legs, malformed limbs, fused fingers, too many fingers, long neck, cross-eyed,mutated hands, polar lowres, bad body, bad proportions, gross proportions, text, error, missing fingers, missing arms, missing legs, extra digit, extra arms, extra leg, extra foot,"
}

# Make a POST request to the Flask API
response = requests.post(url, json=data)

# Check the response status code
if response.status_code == 200:
    # Handle successful response
    data = response.json()
    images_data = data.get('images', [])
    
    # Loop through each image data
    for idx, image_data in enumerate(images_data):
        # Decode base64 image data
        decoded_image = base64.b64decode(image_data)
        
        # Open the image using PIL
        img = Image.open(io.BytesIO(decoded_image))
        
        # Save the image
        img.save(f'image_{idx}.png')
    
    print("Images saved successfully!")
else:
    # Handle error response
    print("Failed to generate images. Error:", response.json())
