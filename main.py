import argparse
import pdfplumber
import pandas as pd
from pathlib import Path

def parse_plan(file_path):
    """Extracts text and basic structure from a project plan PDF."""
    print(f"Reading file: {file_path}")
    data = []
    
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            # Basic extraction logic: capturing lines as individual records
            if text:
                for line in text.split('\n'):
                    data.append({"page": i + 1, "content": line})
    
    df = pd.DataFrame(data)
    return df

def main():
    parser = argparse.ArgumentParser(description="MyPlanReader10: Automated Plan Parser")
    parser.add_argument("--file", required=True, help="Path to the project plan PDF")
    parser.add_argument("--export", choices=['csv', 'json'], default='csv', help="Format to export results")
    
    args = parser.parse_args()
    file_path = Path(args.file)

    if not file_path.exists():
        print(f"Error: File {args.file} not found.")
        return

    # Parse and Display
    results_df = parse_plan(file_path)
    print("\nExtraction Preview:")
    print(results_df.head())

    # Export
    output_name = f"extracted_data.{args.export}"
    if args.export == 'csv':
        results_df.to_csv(output_name, index=False)
    else:
        results_df.to_json(output_name, orient='records', indent=4)
        
    print(f"\nSuccess! Data exported to {output_name}")

if __name__ == "__main__":
    main()
