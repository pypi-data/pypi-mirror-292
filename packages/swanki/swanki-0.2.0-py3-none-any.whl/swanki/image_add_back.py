import os
import re
import requests
from hashlib import md5
from pathlib import Path
from urllib.parse import urlparse, parse_qs

def download_image(image_url: str, save_path: str) -> None:
    response = requests.get(image_url)
    response.raise_for_status()  # Raises HTTPError for bad responses
    with open(save_path, 'wb') as f:
        f.write(response.content)

def generate_unique_filename(url: str) -> str:
    """
    Generates a unique filename for an image by hashing the URL.
    This ensures images with different parameters have unique filenames.
    """
    url_hash = md5(url.encode('utf-8')).hexdigest()
    parsed_url = urlparse(url)
    base_name = os.path.basename(parsed_url.path)
    name, ext = os.path.splitext(base_name)
    return f"{name}_{url_hash}{ext}"

def process_markdown_files(source_dir: str, target_image_dir: str, target_md_dir: str) -> None:
    md_files = [f for f in os.listdir(source_dir) if f.endswith('.md')]
    image_url_pattern = re.compile(r"!\[\]\((https://cdn.mathpix.com/[^)]+)\)")

    for md_file in md_files:
        page_number = md_file.split('-')[1].split('.')[0]
        image_dir_path = os.path.join(target_image_dir, f"page{page_number}")
        os.makedirs(image_dir_path, exist_ok=True)

        with open(os.path.join(source_dir, md_file), 'r') as file:
            content = file.read()

        new_content = content
        for image_url in set(image_url_pattern.findall(content)):
            unique_filename = generate_unique_filename(image_url)
            local_image_path = os.path.join(image_dir_path, unique_filename)
            download_image(image_url, local_image_path)
            new_content = new_content.replace(image_url, f"./images/page{page_number}/{unique_filename}")

        target_md_path = os.path.join(target_md_dir, md_file)
        os.makedirs(os.path.dirname(target_md_path), exist_ok=True)
        with open(target_md_path, 'w') as file:
            file.write(new_content)

# Example usage
source_dir = "swanki-out/clean-md-singles"
target_image_dir = "swanki-out/images"
target_md_dir = "swanki-out/image-add-back"
process_markdown_files(source_dir, target_image_dir, target_md_dir)
