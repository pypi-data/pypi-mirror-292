import os
import re
import tiktoken


def generate_transcript_input(clean_md_dir, image_summaries_dir, output_file):
    md_files = sorted([f for f in os.listdir(clean_md_dir) if f.endswith(".md")])
    transcript_input = ""

    for md_file in md_files:
        md_file_path = os.path.join(clean_md_dir, md_file)
        with open(md_file_path, "r", encoding="utf-8") as file:
            md_content = file.read()

        # Find all image URLs in the Markdown content
        image_urls = re.findall(
            r"!\[\]\((https://cdn\.mathpix\.com/[^)]+)\)", md_content
        )

        for image_url in image_urls:
            # Find the corresponding image summary file
            page_number = md_file.split(".")[0].split("-")[1]
            image_index = image_urls.index(image_url) + 1
            summary_file = f"page-{page_number}_{image_index}.md"
            summary_path = os.path.join(image_summaries_dir, summary_file)

            if os.path.exists(summary_path):
                with open(summary_path, "r", encoding="utf-8") as file:
                    summary_content = file.read()

                # Insert the image summary below the image URL in the Markdown content
                md_content = md_content.replace(
                    image_url, f"{image_url}\n\n{summary_content}"
                )

        transcript_input += md_content + "\n\n"

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(transcript_input)

    return output_file


def generate_transcript(transcript_input_file, output_file, model="gpt-4o"):
    import os
    from dotenv import load_dotenv
    from openai import OpenAI

    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=OPENAI_API_KEY)

    with open(transcript_input_file, "r", encoding="utf-8") as file:
        transcript_input = file.read()

    # Use tiktoken to count the number of tokens in the input text
    encoding = tiktoken.get_encoding("cl100k_base")  # Explicitly specify the encoding
    input_tokens = encoding.encode(transcript_input)
    num_tokens = len(input_tokens)

    # Split the input text into chunks
    chunk_size = 4000  # Reduced chunk size
    max_tokens = 3000  # Adjusted max_tokens
    transcript_chunks = []

    for i in range(0, num_tokens, chunk_size):
        chunk = encoding.decode(input_tokens[i : i + chunk_size])
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": """You are an AI assistant that generates a transcript based on the provided technical text. The text contains mathematical equations, figures, and their summaries. Your task is to create a transcript that complements the Anki cards that are generated from the same text. The transcript should be structured in a way that is suitable for an audiobook, with each section title highlighted and the main concepts summarized, but go into detail to make concepts clear. 
                    
                    Discuss the mathematical equations in a spoken word format, making them easily digestible for an audiobook listener. This means that you should NEVER output any Latex equations. For example if you have $(E[x])$ I would want that translated to 'expectation of ' or $\int_{0}_{\infty}xdx$ would be the integral from 0 to infinity of 'x ... d x', or even simpler 'The integral over the positive reals'. If there are matrices, discuss the contents of the matrix, the matrix properties if there are any etc. You must avoid using latex at all costs. 
                    
                    Add additional context to the material being discussed and go into detail about definitions and their importance. If there are theorems and derivations discussed, give a high level overview providing main intuitive steps of the theorem and the main intuitions that drive it. Do the same for derivations. 
                    
                    For examples given in the text, give enough context to summarize the example and explain its purpose.
                    
                    We want the audio to be about intuitions, concepts, and the big picture. This includes understanding the procedures required for arriving at major conclusions. Write the transcript as if you are presenting the material to a student who is trying to understand the concepts for the first time. When you are narrating avoid saying things like 'this chapter does...', 'this part of the book says...', etc. Narrate as if you are presenting the material that is your own. Narrate in first person.
                    
                    Write at least three paragraphs for each section and try to match the sections of the input text.
                    
                    If there are exercises at the end of the text do NOT discuss them.
                    """,
                },
                {"role": "user", "content": chunk},
            ],
            max_tokens=max_tokens,
            n=1,
            temperature=0.7,
        )
        transcript_chunk = response.choices[0].message.content.strip()
        transcript_chunks.append(transcript_chunk)

    # Combine the transcript chunks
    transcript_output = "\n".join(transcript_chunks)

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(transcript_output)

    return output_file
