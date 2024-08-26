# swanki/image_reader
# [[swanki.image_reader]]
# https://github.com/Mjvolk3/swanki/tree/main/swanki/image_reader
# Test file: tests/swanki/test_image_reader.py


import base64
import requests
from dotenv import load_dotenv
import os

load_dotenv()
import json

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# image_path = "path_to_your_image.jpg"


# # Getting the base64 string
# base64_image = encode_image(image_path)

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}",
}

payload = {
    "model": "gpt-4-vision-preview",
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What’s in this image?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://cdn.mathpix.com/cropped/2024_03_10_3e019cd1fb468e88a933g-1.jpg?height=482&width=700&top_left_y=903&top_left_x=1054",
                        "detail": "high",
                    },
                },
            ],
        }
    ],
    "max_tokens": 300,
}

response = requests.post(
    "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
)

print(response.json())

#message describing the image
message = json.loads(response.text)["choices"][0]["message"]["content"]
print(message)