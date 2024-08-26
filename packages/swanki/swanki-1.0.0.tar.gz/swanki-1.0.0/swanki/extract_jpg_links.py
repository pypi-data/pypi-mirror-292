import re
import os
import glob

def extract_jpg_links(md_file_path: str) -> list:
    # Adjusted regex to specifically target cdn.mathpix.com links
    jpg_link_pattern = r"!\[.*?\]\((https://cdn\.mathpix\.com/.*?\.jpg.*?)\)"
    with open(md_file_path, "r", encoding="utf-8") as file:
        content = file.read()
    links = re.findall(jpg_link_pattern, content)
    return links

def process_markdown_directory(source_dir: str, output_dir: str) -> None:
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for md_file in glob.glob(f"{source_dir}/page-*.md"):
        links = extract_jpg_links(md_file)
        if links:
            # Extracting file number for consistent output file naming
            base_name = os.path.basename(md_file)
            file_number = re.search(r"page-(\d+)\.md", base_name).group(1)
            output_file_path = os.path.join(output_dir, f"hyperlinks-{file_number}.txt")
            with open(output_file_path, "w", encoding="utf-8") as output_file:
                for link in links:
                    output_file.write(f"{link}\n")

if __name__ == "__main__":
    source_dir = "swanki-out/md-singles"
    output_dir = "swanki-out/image-hyperlinks"
    process_markdown_directory(source_dir, output_dir)
