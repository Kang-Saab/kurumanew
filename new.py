import streamlit as st
import requests
from PIL import Image
import io
import base64

st.title("Image Generation App")

# API endpoint
url = 'https://0041-35-234-173-97.ngrok-free.app/generate_images'

# User input fields
prompt = st.text_input("Enter a prompt (e.g., 'a cat riding a bike'):")
height = st.number_input("Enter image height (pixels):", 800)
width = st.number_input("Enter image width (pixels):", 1200)
steps = st.number_input("Enter number of steps:", 25)
guidance = st.number_input("Enter guidance value:", 7.5)
lora_weight = st.number_input("Enter lora weight:", 0)
num_images = st.number_input("Enter number of images to generate:", 3)
neg = st.text_input("Enter negative prompts (comma-separated):", "easynegative, human, lowres, bad anatomy")

if st.button("Generate Images"):
    # Prepare request data
    data = {
        "prompt": prompt,
        "h": height,
        "w": width,
        "steps": steps,
        "guidance": guidance,
        "lora_weight": lora_weight,
        "num_images": num_images,
        "neg": neg
    }

    # Make the POST request
    response = requests.post(url, json=data)

    if response.status_code == 200:
        # Handle successful response
        data = response.json()
        images_data = data.get('images', [])

        for idx, image_data in enumerate(images_data):
            # Decode base64 image data
            decoded_image = base64.b64decode(image_data)
            img = Image.open(io.BytesIO(decoded_image))

            # Display the image in Streamlit
            st.image(img, caption=f"Generated Image {idx+1}")

        st.success("Images generated successfully!")
    else:
        # Handle error response
        st.error(f"Failed to generate images. Error: {response.json()}")
