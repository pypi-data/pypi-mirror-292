# ../Swanki/swanki/token_count
# [[...Swanki.swanki.token_count]]
# https://github.com/Mjvolk3/swanki/tree/main/../Swanki/swanki/token_count
# Test file: ../Swanki/tests/swanki/test_token_count.py


from openai import OpenAI
from dotenv import load_dotenv
import os
import tiktoken

dotenv_path = os.path.join(os.getcwd(), '.env')
load_dotenv(dotenv_path=dotenv_path)

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def count_tokens_in_md_file(file_path: str = "swanki-out/combined.md", encoding_name: str = "cl100k_base") -> int:
    """
    Reads the content of a markdown file and returns the number of tokens
    based on the specified encoding (model).

    Args:
        file_path (str): The path to the markdown file.
        encoding_name (str): The name of the encoding (model) to use for tokenization.

    Returns:
        int: The number of tokens in the markdown file content.
    """
    # Read the markdown file content
    with open(file_path, "r", encoding="utf-8") as md_file:
        file_content = md_file.read()

    # Get the encoding for the specified model
    encoding = tiktoken.get_encoding(encoding_name)

    # Tokenize the file content and return the token count
    num_tokens = len(encoding.encode(file_content))
    return num_tokens
