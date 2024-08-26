import os
import subprocess
import os
import re


# def clean_markdown_files(md_folder_path: str = "swanki-out/md-singles"):
#     """
#     This function cleans markdown files using sed commands and outputs the cleaned files to
#     a new directory 'clean-md-singles'.
#     """
#     # Create a new directory for the cleaned markdown files
#     clean_md_folder_path = os.path.join(
#         os.path.dirname(md_folder_path), "clean-md-singles"
#     )
#     os.makedirs(clean_md_folder_path, exist_ok=True)

#     # List all markdown files
#     md_files = [f for f in os.listdir(md_folder_path) if f.endswith(".md")]

#     for md_file in md_files:
#         full_md_path = os.path.join(md_folder_path, md_file)
#         full_clean_md_path = os.path.join(clean_md_folder_path, md_file)
#         sed_command = f"sed -e 's/\\\\subsection{{\\(.*\\)}}/## \\1/g' -e 's/\\\\section{{\\(.*\\)}}/## \\1/g' -e 's/\\\\(/\\$/g' -e 's/\\\\)/\\$/g' -e 's/\\\\\\[/\\$\\$/g' -e 's/\\\\\\]/\\$\\$/g' {full_md_path} > {full_clean_md_path}"

#         subprocess.run(sed_command, shell=True)

import os
import re

import os
import re

def clean_markdown_files(md_folder_path: str = "swanki-out/md-singles"):
    """
    This function cleans markdown files by performing regex replacements in Python, removes lines 
    that start with a reference pattern `[number]` in the References section, and removes excessive 
    empty lines following the references. The cleaned files are output to a new directory 'clean-md-singles'.
    """
    # Create a new directory for the cleaned markdown files
    clean_md_folder_path = os.path.join(os.path.dirname(md_folder_path), "clean-md-singles")
    os.makedirs(clean_md_folder_path, exist_ok=True)

    # List all markdown files
    md_files = [f for f in os.listdir(md_folder_path) if f.endswith(".md")]

    for md_file in md_files:
        full_md_path = os.path.join(md_folder_path, md_file)
        full_clean_md_path = os.path.join(clean_md_folder_path, md_file)

        cleaned_content = ""
        references_section_found = False
        post_references_empty_line_count = 0
        with open(full_md_path, "r", encoding="utf-8") as file:
            for line in file:
                # Check if the References section has started
                if "\\section*{References}" in line:
                    references_section_found = True

                # If the References section has started, remove lines that start with the pattern [number]
                if references_section_found and re.match(r'^\[\d+\]', line):
                    continue  # Skip adding this line to cleaned_content

                # Logic to collapse multiple empty lines after references to a single empty line
                if references_section_found and line.strip() == "":
                    post_references_empty_line_count += 1
                    # Only keep one empty line
                    if post_references_empty_line_count > 1:
                        continue
                else:
                    post_references_empty_line_count = 0  # Reset counter if a non-empty line is found

                # Perform replacements for LaTeX commands to Markdown
                line = re.sub(r'\\subsection{(.*)}', r'## \1', line)
                line = re.sub(r'\\section{(.*)}', r'## \1', line)
                line = line.replace(r'\(', '$').replace(r'\)', '$')
                line = line.replace(r'\[', '$$').replace(r'\]', '$$')
                cleaned_content += line

        # Write the cleaned content to the new file
        with open(full_clean_md_path, "w", encoding="utf-8") as output_file:
            output_file.write(cleaned_content)

