import os
import re
import random
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


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


def extract_surrounding_text(
    content: str, image_url: str, num_sentences: int = 3
) -> str:
    """
    Extracts the surrounding sentences or paragraphs from the Markdown file based on the image URL.
    """
    # Split the content into sentences
    sentences = re.split(r"(?<=[.!?])\s+", content)

    # Find the index of the sentence containing the image URL
    image_index = None
    for i, sentence in enumerate(sentences):
        if image_url in sentence:
            image_index = i
            break

    if image_index is not None:
        start_index = max(0, image_index - num_sentences)
        end_index = min(len(sentences), image_index + num_sentences + 1)
        surrounding_sentences = sentences[start_index:end_index]
        return " ".join(surrounding_sentences)
    else:
        return ""


def validate_card_content(card_content: str) -> bool:
    """
    Validates the generated card content by checking for the presence of a question, answer, image URL, and tags.
    """
    # Check if the card content contains a question and answer
    if "##" not in card_content or "%" not in card_content:
        return False

    # Check if the card content contains an image URL
    if "![" not in card_content or "](" not in card_content:
        return False

    # Check if the card content contains tags
    if "#" not in card_content:
        return False

    return True


def generate_image_cards(
    source_dir: str,
    summary_dir: str,
    target_dir: str,
    image_urls: list,
    md_file: str,
    max_retries: int = 10,  # Increased max_retries to 10
    initial_delay: float = 1.0,
    backoff_factor: float = 1.5,  # Adjusted backoff_factor to 1.5
):
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    client = OpenAI(api_key=OPENAI_API_KEY)

    system_role_content = """
    You are an AI assistant that generates Anki cards based on a given image and its associated text.
    The image and text will be provided to you, and you should generate a question and answer based on the information.
    The generated card should follow the VsCode Anki format, with the question on the front and the answer on the back.
    Always include the image on the front of the card.
    
    Pretend you are a high level academic or expert in your field. I want you to be concise, exacting, and express doubt if you are unsure of your answers. If I have a query about math, use as much latex for representing equations as possible and be diligent in explaining variables and major concepts. Write me 2 cards for each image.

    When writing latex use '$' for inline math and '$$' for multiline math.
    
    If there are any proofs or derivations please include the step by step derivation.

    Note that you can add tags separated by commas, that are period delimited going from broad topic to narrow topic. Add up to 2 periods if necessary, and make the words in-between slugified. Try to add up to 3 tags per question. Here are 3 example cards. The first card shows how to display latex and structure front and back of cards. The second shows how to create a cloze card. The card itself describes this. The last card shows how you can add extra information to the front of the card with the % sign. Now onto examples.
  
    ## A question or demand. The front side of the card
    
    ![](https://cdn.mathpix.com/cropped/2024_05_01_badd66a000da4f464b5cg-1.jpg?height=1248&width=1238&top_left_y=216&top_left_x=412)
  
    %
    
    Here is the card answer.
  
    $$
    \hat{\theta}_{\mathrm{MAP}}=\operatorname{argmax}_{\theta} p(\theta \mid \mathbf{x}_{1: n})
    $$
  
    - #algorithms, #probability.maximum-a-posteriori
  
    ## Putting extra information on front
    
    ![](https://cdn.mathpix.com/cropped/2024_05_01_badd66a000da4f464b5cg-1.jpg?height=1248&width=1238&top_left_y=216&top_left_x=412)
  
    You can add extra details here like a code block. Anything before the % sign will be on the front of the card.
  
    ```python
    x = 5
    print(x)
    ```
  
    %
  
    Then use the percent sign to indicate the start of the back of the card.
    
    ## Here is example of an image card.
    
    How would you interpret this graph?
    
    ![](https://cdn.mathpix.com/cropped/2024_05_01_badd66a000da4f464b5cg-1.jpg?height=1248&width=1238&top_left_y=216&top_left_x=412)
    
    % 
    
    The graph is a such and such and a such and such.
    
    NEVER DO THE FOLLOWING:
    - Use a header other than H2
    - Leave the tags list empty
    - Don't use the cloze syntax for creating close cards with images
    - Don't use numbers in tags
    
    %
    """

    file_path = os.path.join(source_dir, md_file)
    curr_content = get_file_content(file_path)
    if not curr_content:
        print(f"Skipping {md_file} due to empty content or read error.")
        return

    for image_url in image_urls:
        summary_file = f"page-{md_file.split('.')[0].split('-')[1]}_{image_urls.index(image_url) + 1}.md"
        summary_path = os.path.join(summary_dir, summary_file)
        summary = get_file_content(summary_path)
        if not summary:
            print(
                f"No summary found for {image_url} in {summary_file}. Skipping card generation."
            )
            continue

        # Extract surrounding text from the Markdown file
        surrounding_text = extract_surrounding_text(
            curr_content, image_url, num_sentences=3
        )

        for card_num in range(1, 3):  # Generate two cards for each image
            retry_count = 0
            retry_delay = initial_delay

            while retry_count < max_retries:
                try:
                    completion = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": system_role_content},
                            {
                                "role": "user",
                                "content": f"Generate Anki card {card_num} using the VsCode Anki format based on the following image and associated text:\n\nImage: {image_url}\n\nAssociated Text: {surrounding_text}\n\nSummary: {summary}",
                            },
                        ],
                    )
                    print("Completion generated successfully.")
                    card_content = completion.choices[0].message.content

                    # Validate the generated card content
                    if validate_card_content(card_content):
                        print("Valid card content generated successfully")
                        # Write the card to a file in the target directory
                        card_file = f"{os.path.splitext(md_file)[0]}_card_{image_urls.index(image_url) + 1}_{card_num}.md"
                        card_path = os.path.join(target_dir, card_file)

                        print(f"Saving card {card_num} to: {card_path}")

                        os.makedirs(target_dir, exist_ok=True)

                        with open(card_path, "w", encoding="utf-8") as file:
                            file.write(card_content)
                        break
                    else:
                        print(
                            f"Invalid card content generated for {md_file}, image {image_urls.index(image_url) + 1}, card {card_num}. Retrying..."
                        )
                        retry_count += 1
                        time.sleep(retry_delay)  # Add a delay between retries
                        retry_delay *= (
                            backoff_factor  # Increase the delay exponentially
                        )
                except Exception as e:
                    print(
                        f"Error generating card {card_num} for {md_file}, image {image_urls.index(image_url) + 1}: {e}. Retrying..."
                    )
                    retry_count += 1
                    time.sleep(retry_delay)  # Add a delay between retries
                    retry_delay *= backoff_factor  # Increase the delay exponentially

            if retry_count == max_retries:
                print(
                    f"Failed to generate a valid card {card_num} for {md_file}, image {image_urls.index(image_url) + 1} after {max_retries} retries. Skipping..."
                )
