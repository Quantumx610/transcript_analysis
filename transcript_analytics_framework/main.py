import os
import csv
from config import INPUT_CSV_PATH, INPUT_SCRIPTS_DIR
from processors.analyzer import TranscriptAnalyzer
from processors.formatter import OutputFormatter

def main():
    print("Starting Call Center Transcript Analytics Framework...")
    
    analyzer = TranscriptAnalyzer()
    formatter = OutputFormatter()
    processed_silver_records = []

    # 1. Load your standard script once
    script_path = INPUT_SCRIPTS_DIR / "mahindra_finance_script.txt"
    script_text = ""
    if script_path.exists():
        with open(script_path, 'r', encoding='utf-8') as sf:
            script_text = sf.read()
    else:
        print("Warning: Script file not found. Analysis will run without it.")

    # Check if input CSV exists
    if not INPUT_CSV_PATH.exists():
        print(f"Input CSV not found: {INPUT_CSV_PATH}")
        return

    # 2. Process transcripts from the CSV file
    with open(INPUT_CSV_PATH, mode='r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        
        # Validate that required columns exist
        if 'call_id' not in reader.fieldnames or 'transcript' not in reader.fieldnames:
            print("Error: The CSV file MUST contain 'call_id' and 'transcript' columns.")
            return

        for row in reader:
            transcript_id = row['call_id'].strip()
            transcript_text = row['transcript'].strip()
            
            # Skip empty rows
            if not transcript_id or not transcript_text:
                continue

            try:
                # 1. Analyze using 2-Prompt Architecture
                raw_results = analyzer.analyze(transcript_id, transcript_text, script_text=script_text)

                # 2. Save Layer 1: Bronze (Audit Trail)
                formatter.save_bronze(transcript_id, raw_results)

                # 3. Save Layer 2: Silver (Merged JSON)
                silver_record = formatter.save_silver(transcript_id, raw_results)
                processed_silver_records.append(silver_record)

            except Exception as e:
                print(f"Error processing {transcript_id}: {str(e)}")

    # 4. Save Layer 3: Gold (CSV for Analytics)
    if processed_silver_records:
        formatter.save_gold(processed_silver_records, batch_name="latest_analytics_batch")
        
    print("Processing complete.")

if __name__ == "__main__":
    main()