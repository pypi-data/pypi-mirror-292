import argparse
import os
from PyPDF2 import PdfReader, PdfWriter

def cut_pdf(start_page: int, end_page: int, input_pdf: str, output_pdf: str):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    # Adjusting for 0-based index; assuming user input is 1-based
    start_page -= 1
    end_page -= 1

    for i in range(start_page, end_page + 1):
        writer.add_page(reader.pages[i])

    with open(output_pdf, 'wb') as out_pdf_file:
        writer.write(out_pdf_file)

    print(f"PDF cut from page {start_page+1} to {end_page+1} and saved to {output_pdf}")

def main():
    parser = argparse.ArgumentParser(description="Cut a PDF by page numbers.")
    parser.add_argument('-f', '--first', type=int, required=True, help="First page number to include in the cut.")
    parser.add_argument('-l', '--last', type=int, required=True, help="Last page number to include in the cut.")
    parser.add_argument('file_input', type=str, help="Input PDF file path.")
    parser.add_argument('file_output', type=str, help="Output PDF file path.")

    args = parser.parse_args()

    if not os.path.exists(args.file_input):
        print(f"Error: The file {args.file_input} does not exist.")
        return
    
    if args.first < 1 or args.last < 1 or args.last < args.first:
        print("Error: Invalid page numbers.")
        return

    cut_pdf(args.first, args.last, args.file_input, args.file_output)

if __name__ == "__main__":
    main()
