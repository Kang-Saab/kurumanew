import os
import sys
from flask import Flask, jsonify, request, send_file
import base64
from PIL import Image
import io
from flask import render_template
import requests
# from PIL import Image
# import io
# import base64
# import os

app = Flask(__name__)

# Import pyngrok for ngrok functionality
from pyngrok import ngrok

# Import your image generation code here
import torch
from diffusers import StableDiffusionPipeline
from diffusers import DPMSolverMultistepScheduler

pipe = StableDiffusionPipeline.from_pretrained("digiplay/majicMIX_realistic_v6", torch_dtype=torch.float16)
# pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16)
anime = StableDiffusionPipeline.from_pretrained("redstonehero/cetusmix_v4", torch_dtype=torch.float16)
anime = anime.to("cuda")
pipe = pipe.to("cuda")
# pipe.safety_checker = None
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
anime.scheduler = DPMSolverMultistepScheduler.from_config(anime.scheduler.config)

# Initialize ngrok when the Flask app starts
def init_ngrok():
    # Get the dev server port (defaults to 5000 for Flask)
    port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else "5000"

    # Open a ngrok tunnel to the dev server
    public_url = ngrok.connect(port).public_url
    print(f" * ngrok tunnel \"{public_url}\" -> \"http://127.0.0.1:{port}\"")

    return public_url

# Function to initialize webhooks (if needed)
def init_webhooks(base_url):
    # Update inbound traffic via APIs to use the public-facing ngrok URL
    pass

# Initialize ngrok and set up webhooks (if needed) when the app starts
ngrok_url = None
if os.environ.get("USE_NGROK", "False") == "True" and os.environ.get("NGROK_AUTHTOKEN"):
    ngrok_url = init_ngrok()
    init_webhooks(ngrok_url)

# For demonstration, I'll include a simple image generation function
def generate_images(prompt, h, w, steps, guidance, lora_weight, num_images, neg):
    # Your image generation logic goes here
    # This is where you would use your model to generate images based on the given parameters
    # For demonstration, I'll just return a placeholder image
    prompt = prompt
    h= 800
    w= 640
    steps=40
    guidance= 7.5
    lora_weight=0
    num_images= num_images
    neg = neg
    if "anime" in prompt.lower():
      images = anime(prompt, num_images_per_prompt=num_images, cross_attention_kwargs={"scale": lora_weight}, height=h, width=w, num_inference_steps=steps, guidance_scale=guidance, negative_prompt=neg).images
    else:
      images = pipe(prompt, num_images_per_prompt=num_images, cross_attention_kwargs={"scale": lora_weight}, height=h, width=w, num_inference_steps=steps, guidance_scale=guidance, negative_prompt=neg).images

    return images

@app.route('/generate_images', methods=['POST'])
def generate_and_return_images():
    # Extract parameters from the request JSON
    request_data = request.json
    prompt = request_data.get('prompt')
    h = request_data.get('h', 800)
    w = request_data.get('w', 640)
    steps = request_data.get('steps', 25)
    guidance = request_data.get('guidance', 7.5)
    lora_weight = request_data.get('lora_weight', 0)
    num_images = request_data.get('num_images', 1)
    neg = request_data.get('neg')

    # Generate images based on the parameters
    images = generate_images(prompt, h, w, steps, guidance, lora_weight, num_images, neg)

    # Convert images to base64 encoded strings
    encoded_images = []
    for image in images:
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        encoded_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
        encoded_images.append(encoded_image)

    # Return the base64 encoded images in JSON format
    return jsonify({'images': encoded_images})

imagex  = 8
# API endpoint
url = ngrok_url + 'generate_images'  # Replace with your actual API endpoint

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

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

        request_data = data
        prompt = request_data.get('prompt')
        h = request_data.get('h', 800)
        w = request_data.get('w', 640)
        steps = request_data.get('steps', 25)
        guidance = request_data.get('guidance', 7.5)
        lora_weight = request_data.get('lora_weight', 0)
        num_images = request_data.get('num_images', 1)
        neg = request_data.get('neg')

        images = generate_images(prompt, h, w, steps, guidance, lora_weight, num_images, neg)

        # Convert images to base64 encoded strings
        encoded_images = []
        for image in images:
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            encoded_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
            encoded_images.append(encoded_image)

        # Return the base64 encoded images in JSON format
        generated_image = jsonify({'images': encoded_images})

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

        # Handle successful response
        data = generated_image.json
        images_data = data.get('images', [])
        images = []
        for idx, image_data in enumerate(images_data):
            # Decode base64 image data
            decoded_image = base64.b64decode(image_data)
            img = Image.open(io.BytesIO(decoded_image))
            global imagex
            imagex =imagex+1
            img.save(f'static/generated/{imagex}.png')
            # Convert image to base64 for template (optional, can be displayed directly)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            encoded_image = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
            images.append({'id': idx + 1, 'data': encoded_image})

        return render_template('show.html', images=images, prompt=prompt,com_image_files1=com_image_files1,com_image_files2=com_image_files2,com_image_files3=com_image_files3)

if __name__ == '__main__':
    # Start the Flask app
    app.run(debug=True)
