from flask import Flask, render_template, request, jsonify
import requests
from PIL import Image
import io
import base64
import os
app = Flask(__name__)

image  = 8
# API endpoint
url = 'https://ddd0-35-240-227-205.ngrok-free.app/generate_images'  # Replace with your actual API endpoint

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/show')
def show():
    return render_template('show.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/community_show', methods=['GET','POST'])
def community_show():
    com_image_folder = 'static/generated'
    com_image_files = [filename for filename in os.listdir(com_image_folder) if filename.endswith(('.png', '.jpg', '.jpeg'))]
    com_image_files.reverse()
    com_image_files1 = com_image_files[::3]  # Start from index 0, take every 3rd element
    com_image_files2 = com_image_files[1::3] # Start from index 1, take every 3rd element
    com_image_files3 = com_image_files[2::3] # Start from index 2, take every 3rd element
    com_image_files1 = com_image_files1[:8]
    com_image_files2 = com_image_files2[:8]
    com_image_files3 = com_image_files3[:8]
    if request.method == 'GET':
        return render_template('community_show.html',com_image_files1=com_image_files1,com_image_files2=com_image_files2,com_image_files3=com_image_files3)
    else:
        sendimg = request.form['showimage']
        return render_template('community_show.html', sendimg=sendimg,com_image_files1=com_image_files1,com_image_files2=com_image_files2,com_image_files3=com_image_files3)

@app.route('/generate', methods=['GET', 'POST'])
def image_generation():
    if request.method == 'GET':
        return render_template('create2.html')
    else:
        # User input from form
        prompt = request.form['prompt']
        # height = int(request.form['height'])
        # width = int(request.form['width'])
        # steps = int(request.form['steps'])
        # guidance = float(request.form['guidance'])
        # lora_weight = float(request.form['lora_weight'])
        num_images = int(request.form['num_images'])
        neg = request.form['negprompt']

        # Prepare request data
        data = {
            "prompt": prompt,
            "h": "",
            "w": "width",
            "steps": "steps",
            "guidance": "guidance",
            "lora_weight": "lora_weight",
            "num_images": num_images,
            "neg": neg
        }
        com_image_folder = 'static/generated'
        com_image_files = [filename for filename in os.listdir(com_image_folder) if filename.endswith(('.png', '.jpg', '.jpeg'))]
        com_image_files.reverse()
        com_image_files1 = com_image_files[::3]  # Start from index 0, take every 3rd element
        com_image_files2 = com_image_files[1::3] # Start from index 1, take every 3rd element
        com_image_files3 = com_image_files[2::3] # Start from index 2, take every 3rd element
        com_image_files1 = com_image_files1[:8]
        com_image_files2 = com_image_files2[:8]
        com_image_files3 = com_image_files3[:8]
        # Make the POST request
        response = requests.post(url, json=data)

        if response.status_code == 200:
            # Handle successful response
            data = response.json()
            images_data = data.get('images', [])
            images = []
            for idx, image_data in enumerate(images_data):
                # Decode base64 image data
                decoded_image = base64.b64decode(image_data)
                img = Image.open(io.BytesIO(decoded_image))
                global image
                image =image+1
                img.save(f'static/generated/{image}.png')
                # Convert image to base64 for template (optional, can be displayed directly)
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG')
                encoded_image = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
                images.append({'id': idx + 1, 'data': encoded_image})

            return render_template('show.html', images=images, prompt=prompt,com_image_files1=com_image_files1,com_image_files2=com_image_files2,com_image_files3=com_image_files3)
        else:
            # Handle error response
            error_message = f"Failed to generate images. Error: {response.json()}"
            return render_template('error.html', error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)
