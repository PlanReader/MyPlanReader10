import argparse
from pathlib import Path

# Error Handler for Missing Libraries
try:
    import pdfplumber
    import pandas as pd
except ImportError as e:
    print(f"Error: Missing dependency. Please run 'pip install pandas pdfplumber'. Detail: {e}")
    exit(1)

def parse_txt(file_path):
    """Extracts data from a plain text file with error handling."""
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                clean_line = line.strip()
                if clean_line:
                    data.append({"source": "txt", "index": i + 1, "content": clean_line})
    except Exception as e:
        print(f"Error reading text file: {e}")
    return data

def parse_pdf(file_path):
    """Extracts data from a PDF file with error handling."""
    data = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    for line in text.split('\n'):
                        data.append({"source": "pdf", "index": i + 1, "content": line})
    except Exception as e:
        print(f"Error parsing PDF (the file might be corrupted or password-protected): {e}")
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

    if not data:
        print("No data could be extracted from the file.")
        return

    try:
        results_df = pd.DataFrame(data)
        print("\nExtraction Preview:")
        print(results_df.head())

        output_name = f"extracted_data.{args.export}"
        if args.export == 'csv':
            results_df.to_csv(output_name, index=False)
        else:
            results_df.to_json(output_name, orient='records', indent=4)
        print(f"\nSuccess! Data exported to {output_name}")
    except Exception as e:
        print(f"Error during data export: {e}")

if __name__ == "__main__":
    main()
