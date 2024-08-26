import os
import re
import requests
from dotenv import load_dotenv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load environment variables
dotenv_path = os.path.join(os.getcwd(), '.env')
load_dotenv(dotenv_path=dotenv_path)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}",
}


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


def summarize_image(
    image_url: str, context: str, attempt: int = 0, max_attempts: int = 3
) -> str:
    """
    Summarizes the image using OpenAI's API with additional context.
    Implements exponential backoff in case of a 429 response (Too Many Requests).
    Returns a text summary of the image or an empty string if the summary cannot be generated.
    """
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Given the following contextual information from the paper, what's in this image? "
                        + context,
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url, "detail": "high"},
                    },
                ],
            }
        ],
        "max_tokens": 500,
    }

    backoff_factor = 2
    base_wait_time = 5
    fixed_delay = 2

    while attempt < max_attempts:
        try:
            time.sleep(fixed_delay)  # Fixed delay before each request
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            response_json = response.json()
            summary = (
                response_json.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )
            return summary if summary else "Image summary could not be generated."
        except requests.exceptions.RequestException as e:
            if (
                isinstance(e, requests.exceptions.HTTPError)
                and e.response.status_code == 400
            ):
                print(f"Bad Request error for {image_url}: {e}")
                print(f"Request payload: {payload}")
                attempt += 1
                time.sleep(backoff_factor**attempt)  # Exponential backoff
            elif (
                isinstance(e, requests.exceptions.HTTPError)
                and e.response.status_code == 429
            ):
                wait_time = base_wait_time * (backoff_factor**attempt)
                print(
                    f"Rate limit exceeded for {image_url}, waiting {wait_time} seconds before retrying (attempt {attempt + 1}/{max_attempts})..."
                )
                time.sleep(wait_time)
                attempt += 1
            else:
                print(f"Request failed for {image_url}: {type(e).__name__} - {str(e)}")
                attempt += 1
                time.sleep(backoff_factor**attempt)  # Exponential backoff
        except Exception as e:
            print(
                f"Unexpected error occurred for {image_url}: {type(e).__name__} - {str(e)}"
            )
            attempt += 1
            time.sleep(backoff_factor**attempt)  # Exponential backoff

    print(
        f"Failed to generate image summary for {image_url} after {max_attempts} attempts."
    )
    return "Failed to generate image summary after maximum retry attempts."


def process_images_summaries(
    source_dir: str, target_dir: str, max_retries: int = 3
) -> list:
    """
    Processes the images in the Markdown files, generates summaries, and returns a list of successful summaries.
    """
    os.makedirs(target_dir, exist_ok=True)
    md_files = sorted([f for f in os.listdir(source_dir) if f.endswith(".md")])

    successful_summaries = []

    for i, md_file in enumerate(md_files):
        file_path = os.path.join(source_dir, md_file)
        curr_content = get_file_content(file_path)
        if not curr_content:
            print(f"Skipping {md_file} due to empty content or read error.")
            continue

        prev_content = (
            get_file_content(os.path.join(source_dir, md_files[i - 1])) if i > 0 else ""
        )
        next_content = (
            get_file_content(os.path.join(source_dir, md_files[i + 1]))
            if i < len(md_files) - 1
            else ""
        )
        context = f"{prev_content}\n\n{curr_content}\n\n{next_content}"

        image_url_pattern = re.compile(r"!\[\]\((https://cdn.mathpix.com/[^)]+)\)")
        image_urls = image_url_pattern.findall(curr_content)
        if not image_urls:
            print(f"No images found in {md_file}. Skipping image summarization.")
            continue

        print(f"Found {len(image_urls)} images in {md_file}.")
        print(f"Target directory: {target_dir}")  # Added debugging statement

        page_number = md_file.split(".")[0].split("-")[
            1
        ]  # Extract the page number from the md_file name

        for j, image_url in enumerate(image_urls):
            summary_file = f"page-{page_number}_{j+1}.md"  # Use the page number in the summary file name
            summary_path = os.path.join(target_dir, summary_file)

            if not os.path.exists(summary_path):
                summary = summarize_image(image_url, context)
                if summary.startswith("Failed to generate"):
                    print(
                        f"Failed to generate summary for {image_url} in {md_file}. Skipping."
                    )
                else:
                    summary_text = f"ChatGPT figure/image summary: {summary}"
                    print(
                        f"Saving summary to: {summary_path}"
                    )  # Added debugging statement
                    try:
                        with open(
                            summary_path, "w", encoding="utf-8"
                        ) as file:  # Ensure UTF-8 encoding
                            file.write(summary_text)
                    except Exception as e:
                        print(
                            f"Error writing summary to {summary_path}: {e}"
                        )  # Added exception handling
                    print(f"Summary generated and written to {summary_file}")
                    successful_summaries.append((image_url, md_file, summary_file))
            else:
                print(
                    f"Summary already exists for {image_url} in {summary_file}. Skipping."
                )
                successful_summaries.append((image_url, md_file, summary_file))

        if len(image_urls) > 0:
            print(f"Image summaries generated for {md_file}.")

    print("Successful summaries:")  # Added debugging statement
    for summary in successful_summaries:
        print(summary)  # Added debugging statement

    return successful_summaries
