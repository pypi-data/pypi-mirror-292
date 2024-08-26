import os
import re

def get_file_content(file_path: str) -> str:
    """
    Returns the content of a file if it exists, otherwise returns an empty string.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:  # Ensure UTF-8 encoding
            return file.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return ""

def process_markdown_files(source_dir: str, summary_dir: str, target_dir: str):
    os.makedirs(target_dir, exist_ok=True)
    md_files = sorted([f for f in os.listdir(source_dir) if f.endswith('.md')])
    image_url_pattern = re.compile(r"!\[\]\((https://cdn.mathpix.com/[^)]+)\)")

    for md_file in md_files:
        file_path = os.path.join(source_dir, md_file)
        curr_content = get_file_content(file_path)
        if not curr_content:
            print(f"Skipping {md_file} due to empty content or read error.")
            continue

        image_urls = image_url_pattern.findall(curr_content)
        if not image_urls:
            print(f"No images found in {md_file}. Skipping summary insertion.")
            with open(os.path.join(target_dir, md_file), 'w', encoding="utf-8") as file:  # Ensure UTF-8 encoding
                file.write(curr_content)
            continue

        new_content = curr_content
        for j, image_url in enumerate(image_urls):
            summary_file = f"{os.path.splitext(md_file)[0]}_{j+1}.md"
            summary_path = os.path.join(summary_dir, summary_file)
            summary = get_file_content(summary_path)
            if summary:
                new_content = new_content.replace(image_url, f"{image_url}\n\n{summary}")
            else:
                print(f"No summary found for {image_url} in {summary_file}.")

        with open(os.path.join(target_dir, md_file), 'w', encoding="utf-8") as file:  # Ensure UTF-8 encoding
            file.write(new_content)

# Example usage
source_dir = "swanki-out/clean-md-singles"
summary_dir = "swanki-out/image-summaries"
target_dir = "swanki-out/md-with-summaries"
process_markdown_files(source_dir, summary_dir, target_dir)