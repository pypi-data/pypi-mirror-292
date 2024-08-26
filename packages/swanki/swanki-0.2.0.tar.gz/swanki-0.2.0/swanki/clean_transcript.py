import os
import tiktoken
from openai import OpenAI


def clean_transcript(transcript_output_file, clean_output_file, model="gpt-4o"):
    import os
    from dotenv import load_dotenv
    import tiktoken

    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=OPENAI_API_KEY)

    with open(transcript_output_file, "r", encoding="utf-8") as file:
        transcript_output = file.read()

    # Use tiktoken to count the number of tokens in the transcript output
    encoding = tiktoken.get_encoding("cl100k_base")  # Explicitly specify the encoding
    output_tokens = encoding.encode(transcript_output)
    num_tokens = len(output_tokens)

    # Split the transcript output into smaller chunks
    chunk_size = 1400  # Increased chunk size to generate longer transcript
    clean_transcript_chunks = []
    cleaned_transcript = ""

    for i in range(0, num_tokens, chunk_size):
        chunk = encoding.decode(output_tokens[i : i + chunk_size])

        # Find the last complete sentence in the chunk
        last_sentence_end = chunk.rfind(".")
        if last_sentence_end != -1:
            chunk = chunk[: last_sentence_end + 1]

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": """You are an AI assistant that reviews a generated transcript to ensure it adheres to the specified guidelines and maintains a consistent style throughout the document. The transcript should:
                    1. Minimize the use of LaTeX equations. Describe equations in plain English when possible, spelling out the pronunciation of Greek letters. This includes no inline math or variables. For example, NEVER INCLUDE '\(' and or '\)' in the output message. NEVER USE '\mathbf{}' etc. NO LATEX or Latex related symbols! This is VERY important. 
                    2. Provide additional context and detailed explanations for definitions and their importance.
                    3. Give high-level overviews of theorems and derivations, focusing on the main intuitions behind them and by walking through the major steps involved.
                    4. Explain the main purpose of examples given in the original text by providing enough context to understand the problem and its solution.
                    5. Focus on intuitions, concepts, and the big picture, as if presenting the material to a student for the first time.
                    6. Avoid referencing the original text (e.g., "this chapter does...", "this part of the book says..."). Instead, narrate as if presenting your own material. Make sure all text is in the present tense.
                    7. Omit any exercises or problems at the end of chapters.
                    8. When encountering subscripts or superscripts, write them out in plain English (e.g., "Mu sub a" instead of "Mu_a", "Sigma squared" instead of "Sigma^2").
                    9. Add a "Section: " at the beginning of each section header to make the transcript easier to review. We do not need any special markdown formatting for this. Do not bold, or apply headers and it disturbs the audio model.
                    10. Make sure that each section is at least 3 paragraphs long and try to use the sections 
                    11. Do not use any markdown formatting except for numbered lists or bullet points when necessary.
                    12. Section headers should never just say "Summary." Try to be as descriptive as possible in section headers.
                    13. Do not repeat yourself. If you have already explained a concept, do not explain it again unless there is a new angle or insight to add.
                    14. Avoid Making lists of keys takeaways or bullet points. Instead, summarize the key points in a few sentences.
                    15. Translate math into spoken language. e.g. f(x) to 'f of x', x^2 to 'x squared', 'x^4' to 'x to the power of 4', > to 'greater than', < to 'less than', etc. Same with greater than or equal to, less than or equal to, etc. Symbols like λ, ∇ should be spelled out as 'lambda', 'nabla', etc. 
                    16. Again don't use '\(' or to bookend math '\)' just use symbols that can be spoken.
                    17. Do Not includes sections on references or acknowledgments.

                    Please review the provided transcript chunk and ensure it adheres to these guidelines. Maintain a consistent style throughout the transcript, taking into account the existing audio transcript provided. It is essential to preserve the original content as much as possible while adhering to the guidelines. Do not reduce the size of the transcript. If necessary, you may slightly expand the content to ensure clarity and coherence.""",
                },
                {"role": "assistant", "content": cleaned_transcript},
                {"role": "user", "content": f"Current chunk to be cleaned and added to the transcript:\n\n{chunk}\n\nThis is the current audio transcript (for reference to maintain consistency and avoid duplication):\n\n{cleaned_transcript}\n\n Here is the Chunk to be cleaned and added to the transcript:\n\n{chunk}\n\n"},
            ],
            max_tokens=4096,  # Set max_tokens to the maximum allowed by the model
            n=1,
            temperature=0.7,
        )
        clean_transcript_chunk = response.choices[0].message.content.strip()
        clean_transcript_chunks.append(clean_transcript_chunk)

        # Update cleaned_transcript with the latest cleaned chunk
        cleaned_transcript += clean_transcript_chunk + "\n\n"

    # Combine the clean transcript chunks
    clean_transcript_output = "\n".join(clean_transcript_chunks)

    # Generate a brief summary of the entire cleaned transcript
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": """You are an AI assistant that summarizes the main points of a given text. The text is an audio transcript for technical material from either a textbook or an academic paper.The summary should: 
                1. Don't use any markdown formatting except for numbered lists and bullet points when necessary. The summary should start with 'Section: Chapter Summary' or if it is a paper 'Section: Paper Summary'. Do not use bolding, headers, or italics markdown formatting.
                2. Don't list more that 12 items in the summary list. You can list fewer items if necessary. Choose the most important points to include in the summary.
                """,
            },
            {
                "role": "user",
                "content": f"Please provide a brief summary of the main points covered in the following audio transcript:\n\n{clean_transcript_output}",
            },
        ],
        max_tokens=4096,  # Adjust the max_tokens for the summary as needed
        n=1,
        temperature=0.7,
    )
    summary = response.choices[0].message.content.strip()

    # Append the summary to the cleaned transcript output
    clean_transcript_output += f"\n\n{summary}"

    with open(clean_output_file, "w", encoding="utf-8") as file:
        file.write(clean_transcript_output)

    return clean_output_file