import os
import sys
from flask import Flask, jsonify, request, send_file
import base64
from PIL import Image
import io

app = Flask(__name__)

# Import pyngrok for ngrok functionality
from pyngrok import ngrok

# Import your image generation code here
import torch
from diffusers import StableDiffusionPipeline
from diffusers import DPMSolverMultistepScheduler

pipe = StableDiffusionPipeline.from_pretrained("digiplay/majicMIX_realistic_v6", torch_dtype=torch.float16)
pipe = pipe.to("cuda")
pipe.safety_checker = None
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)

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
    steps=25
    guidance= 7.5
    lora_weight=0
    num_images= num_images
    neg = neg

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

if __name__ == '__main__':
    # Start the Flask app
    app.run(debug=True)
