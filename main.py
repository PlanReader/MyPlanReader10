import argparse
import pdfplumber
import pandas as pd
from pathlib import Path

def parse_txt(file_path):
    """Extracts data from a plain text file."""
    data = []
    with open(file_path, 'r') as f:
        for i, line in enumerate(f):
            clean_line = line.strip()
            if clean_line:
                data.append({"source": "txt", "index": i + 1, "content": clean_line})
    return data

def parse_pdf(file_path):
    """Extracts data from a PDF file."""
    data = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                for line in text.split('\n'):
                    data.append({"source": "pdf", "index": i + 1, "content": line})
    return data

def main():
    parser = argparse.ArgumentParser(description="MyPlanReader10: Automated Plan Parser")
    parser.add_argument("--file", required=True, help="Path to the project plan (PDF or TXT)")
    parser.add_argument("--export", choices=['csv', 'json'], default='csv', help="Export format")
    
    args = parser.parse_args()
    file_path = Path(args.file)

    if not file_path.exists():
        print(f"Error: File {args.file} not found.")
        return

    # Determine parser based on extension
    if file_path.suffix.lower() == '.pdf':
        data = parse_pdf(file_path)
    elif file_path.suffix.lower() == '.txt':
        data = parse_txt(file_path)
    else:
        print("Unsupported file format. Please use .pdf or .txt")
        return

    results_df = pd.DataFrame(data)
    print("\nExtraction Preview:")
    print(results_df.head())

    output_name = f"extracted_data.{args.export}"
    if args.export == 'csv':
        results_df.to_csv(output_name, index=False)
    else:
        results_df.to_json(output_name, orient='records', indent=4)
        
    print(f"\nSuccess! Data exported to {output_name}")

if __name__ == "__main__":
    main()
