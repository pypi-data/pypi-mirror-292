import argparse
import os
import os.path as osp
import re
import subprocess
from swanki import (
    generate_text_cards,
    recombine_md_files,
    count_tokens_in_md_file,
    combine_mds,
    convert_pdf_to_markdown,
    clean_markdown_files,
    split_pdf_into_pages,
    process_images_summaries,
    generate_image_cards,
    generate_transcript_input,
    generate_transcript,
    clean_transcript,
)


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


def main():
    parser = argparse.ArgumentParser(
        description="Swanki: A CLI tool for managing markdown files for Anki card generation."
    )
    parser.add_argument(
        "-f", "--file", help="The path to the PDF file to be processed."
    )
    parser.add_argument(
        "-n",
        "--num-cards",
        type=int,
        help="Number of Anki cards to generate.",
        default=3,
    )
    parser.add_argument(
        "-w",
        "--window-size",
        type=int,
        help="Window size for recombining markdown files.",
        default=2,
    )
    parser.add_argument(
        "-s",
        "--skip",
        type=int,
        help="Number of files to skip in each iteration.",
        default=1,
    )
    args = parser.parse_args()

    # Ensure skip is never larger than window size
    args.skip = min(args.skip, args.window_size)

    if args.file:
        ## Transcript Testing
        pdf_path = args.file
        split_pdf_into_pages(pdf_path)
        if osp.exists("swanki-out/clean-md-singles"):
            print("Markdown files already cleaned. Skipping.")
        else:
            convert_pdf_to_markdown()
            clean_markdown_files()

        successful_summaries = []
        if osp.exists("swanki-out/image-summaries"):
            print("image summaries already generated. Skipping.")
        else:
            source_dir = "swanki-out/clean-md-singles"
            target_dir = "swanki-out/image-summaries"
            successful_summaries = process_images_summaries(source_dir, target_dir)

        # Check if all image summaries were generated successfully
        md_files = sorted([f for f in os.listdir(source_dir) if f.endswith(".md")])
        total_images = sum(
            len(
                re.findall(
                    r"!\[\]\((https://cdn.mathpix.com/[^)]+)\)",
                    get_file_content(osp.join(source_dir, md_file)),
                )
            )
            for md_file in md_files
        )
        if len(successful_summaries) != total_images:
            print("Not all image summaries were generated successfully. Exiting.")
            return
        
        # Generate image cards only for the successfully generated summaries
        summary_dir = "swanki-out/image-summaries"
        target_dir = "swanki-out/anki-image-cards"
        if successful_summaries:
            # Group summaries by md_file
            summaries_by_md_file = {}
            for image_url, md_file, summary_file in successful_summaries:
                if md_file not in summaries_by_md_file:
                    summaries_by_md_file[md_file] = []
                summaries_by_md_file[md_file].append((image_url, summary_file))

            for md_file, summaries in summaries_by_md_file.items():
                image_urls = [summary[0] for summary in summaries]
                generate_image_cards(
                    source_dir, summary_dir, target_dir, image_urls, md_file
                )
        else:
            print("No successful image summaries found. Skipping card generation.")

        # Generate text cards from the cleaned Markdown files
        clean_md_dir = "swanki-out/clean-md-singles"
        for md_file in os.listdir(clean_md_dir):
            if md_file.endswith(".md"):
                md_file_path = os.path.join(clean_md_dir, md_file)
                generate_text_cards(md_file_path, num_cards=args.num_cards)

        # Combine the generated Markdown files
        combine_mds(
            text_cards_dir="swanki-out/gen-md",
            image_cards_dir="swanki-out/anki-image-cards",
            output_dir="swanki-out",
            output_filename="swanki-out.md",
        )

        # Clean up inline LaTeX in the combined Markdown file
        combined_file_path = osp.join("swanki-out", "combined.md")
        subprocess.run(
            [
                "sed",
                "-i",
                "s/\\\\\\\\( /$/g; s/ \\\\\\\\)/$/g; s/\\\\mu/\\\\mu/g",
                combined_file_path,
            ]
        )
        print(f"Cleaned up inline LaTeX in {combined_file_path}")
        ##

        ## Audio Transcirpt
        # Generate the transcript input by combining clean-md-singles and image-summaries
        clean_md_dir = "swanki-out/clean-md-singles"
        image_summaries_dir = "swanki-out/image-summaries"
        transcript_input_file = "swanki-out/transcript-input.md"
        generate_transcript_input(
            clean_md_dir, image_summaries_dir, transcript_input_file
        )

        # Generate the transcript using the OpenAI API
        transcript_output_file = "swanki-out/transcript-output.md"
        generate_transcript(transcript_input_file, transcript_output_file)

        print(f"Transcript generated and saved to {transcript_output_file}")

        # # Generate the transcript using the OpenAI API
        transcript_output_file = "swanki-out/transcript-output.md"
        # generate_transcript(transcript_input_file, transcript_output_file)
        ###
        
        ### Clean Transcript
        # Clean and refine the generated transcript
        clean_output_file = "swanki-out/transcript-clean-output.md"
        clean_transcript(transcript_output_file, clean_output_file)

        print(f"Clean transcript generated and saved to {clean_output_file}")
        ###
        
    else:
        print("No file provided. Exiting.")
        return


if __name__ == "__main__":
    main()
