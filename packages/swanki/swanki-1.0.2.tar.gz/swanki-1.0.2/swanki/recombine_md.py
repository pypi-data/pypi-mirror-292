import os

def recombine_md_files(window_size: int = 2, base_dir: str = "swanki-out"):
    md_dir = os.path.join(base_dir, "clean-md-singles")
    output_dir = os.path.join(base_dir, "recombined-md")
    os.makedirs(output_dir, exist_ok=True)  # Create output directory if it doesn't exist

    # Get a sorted list of all Markdown files
    md_files = sorted([f for f in os.listdir(md_dir) if f.endswith(".md")])
    num_files = len(md_files)

    # Loop through the markdown files based on the window size
    for i in range(num_files):
        combined_content = ""
        # Loop with wrap-around using modulo for circular behavior
        for j in range(window_size):
            # Use modulo to wrap around the file list
            file_index = (i + j) % num_files
            with open(os.path.join(md_dir, md_files[file_index]), "r") as md_file:
                combined_content += md_file.read() + "\n\n"

        # Define the output filename based on where the chunking starts
        output_filename = f"page-{i+1}.md"

        # Save the combined content to the new file
        with open(os.path.join(output_dir, output_filename), "w") as output_file:
            output_file.write(combined_content)