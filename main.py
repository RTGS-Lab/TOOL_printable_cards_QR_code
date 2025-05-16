#!/usr/bin/env python3
"""
Main script for generating printable cards with QR codes from CSV data.

To use this script:
1. Set up a virtual environment:
   ./setup.sh
2. Activate the virtual environment:
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate     # On Windows
3. Install dependencies:
   pip install -r requirements.txt
4. Run the script:
   python main.py --input your_data.csv
"""

import os
import sys
import pandas as pd
import argparse
import shutil
from pathlib import Path
import qrgen
import create_weblinks


def check_file_exists(file_path, template_content=None, description=None):
    """
    Check if a file exists and create a template if it doesn't and a template is provided.
    
    Args:
        file_path (str): Path to the file to check
        template_content (str, optional): Content to write to the file if it doesn't exist
        description (str, optional): Description of the file for output messages
    
    Returns:
        bool: True if the file exists or was created, False otherwise
    """
    if not os.path.exists(file_path):
        if template_content:
            try:
                with open(file_path, 'w') as f:
                    f.write(template_content)
                print(f"✅ Created {description} template at: {file_path}")
                return True
            except Exception as e:
                print(f"❌ Error creating {description} template: {e}")
                return False
        else:
            print(f"❌ Required file not found: {file_path}")
            return False
    return True


def validate_csv_headers(csv_path, required_headers):
    """
    Validate that a CSV file contains the required headers.
    
    Args:
        csv_path (str): Path to the CSV file
        required_headers (list): List of required header names
    
    Returns:
        bool: True if all required headers are present, False otherwise
    """
    try:
        df = pd.read_csv(csv_path)
        missing_headers = [h for h in required_headers if h not in df.columns]
        
        if missing_headers:
            print(f"❌ CSV is missing required headers: {', '.join(missing_headers)}")
            print("Required headers are: " + ", ".join(required_headers))
            # Create a template CSV with the required headers
            template_df = pd.DataFrame(columns=required_headers)
            template_path = "template_input.csv"
            template_df.to_csv(template_path, index=False)
            print(f"✅ Created a template CSV at: {template_path}")
            return False
        
        return True
    
    except Exception as e:
        print(f"❌ Error validating CSV headers: {e}")
        return False


def create_qr_codes(input_csv, qr_dir, weblinks_csv):
    """
    Generate QR codes for each entry in the input CSV.
    
    Args:
        input_csv (str): Path to input CSV with weblinks
        qr_dir (str): Directory to store QR codes
        weblinks_csv (str): Path to CSV with weblinks
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Ensure QR code directory exists
    os.makedirs(qr_dir, exist_ok=True)
    
    try:
        # Read the CSV with weblinks
        df = pd.read_csv(weblinks_csv)
        
        # Create a DataFrame to store QR code metadata
        qr_metadata = {
            'OBJECTID': [],
            'WebLink': [],
            'QR_Code_Filename': []
        }
        
        # Generate QR codes for each entry
        for _, row in df.iterrows():
            object_id = row['OBJECTID']
            weblink = row['WebLink']
            
            # Create QR code filename
            qr_filename = f"{qr_dir}/qr_{object_id}.png"
            
            # Generate the QR code
            qrgen.generate_qr_code(weblink, qr_filename)
            
            # Add to metadata
            qr_metadata['OBJECTID'].append(object_id)
            qr_metadata['WebLink'].append(weblink)
            qr_metadata['QR_Code_Filename'].append(qr_filename)
        
        # Save metadata to CSV
        metadata_df = pd.DataFrame(qr_metadata)
        metadata_csv = f"{qr_dir}/qr_metadata.csv"
        metadata_df.to_csv(metadata_csv, index=False)
        
        print(f"✅ Generated {len(metadata_df)} QR codes in directory: {qr_dir}")
        print(f"✅ Created QR code metadata file: {metadata_csv}")
        
        return True
    
    except Exception as e:
        print(f"❌ Error creating QR codes: {e}")
        return False


def create_card_markdown_files(input_csv, weblinks_csv, qr_dir, card_template_path, output_dir):
    """
    Create markdown files for each card based on the template.
    
    Args:
        input_csv (str): Path to input CSV
        weblinks_csv (str): Path to CSV with weblinks
        qr_dir (str): Directory containing QR codes
        card_template_path (str): Path to card template markdown
        output_dir (str): Directory to store output card markdown files
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Read the weblinks CSV
        df = pd.read_csv(weblinks_csv)
        
        # Read the card template
        with open(card_template_path, 'r') as f:
            template = f.read()
        
        card_files = []
        
        # Create a card file for each entry
        for _, row in df.iterrows():
            object_id = row['OBJECTID']
            
            # Create variable mapping for template
            variables = {
                '{{title}}': f"Project {object_id}",
                '{{contact_person}}': row.get('Your Name', ''),
                '{{contact}}': row.get('Your Name', ''),
                '{{description}}': row.get('Describe the opportunity', ''),
                '{{potential_funders}}': row.get('Who might be a potential funder of this work?', ''),
                '{{funders}}': row.get('Who might be a potential funder of this work?', ''),
                '{{feasibility_next_3_years}}': row.get('Is the opportunity feasible in the next 3 years?', ''),
                '{{feasible_3yr}}': row.get('Is the opportunity feasible in the next 3 years?', ''),
                '{{opportunities}}': row.get('What do you expect would go smoothly?', ''),
                '{{challenges}}': row.get('What would you expect to be challenging?', ''),
                '{{qr_code_filename}}': f"qr_{object_id}.png",
                '{{qr_code}}': f"./qr_codes/qr_{object_id}.png"
            }
            
            # Replace variables in template
            card_content = template
            for key, value in variables.items():
                card_content = card_content.replace(key, str(value) if value is not None else '')
            
            # Write card markdown file
            card_filename = f"{output_dir}/card_{object_id}.md"
            with open(card_filename, 'w') as f:
                f.write(card_content)
            
            card_files.append(card_filename)
        
        print(f"✅ Created {len(card_files)} card markdown files in directory: {output_dir}")
        return True
    
    except Exception as e:
        print(f"❌ Error creating card markdown files: {e}")
        return False


def display_welcome():
    """Display a welcome message with basic usage instructions"""
    welcome = """
╔═══════════════════════════════════════════════════════════════╗
║                   TOOL Printable Cards QR Code                ║
║                                                               ║
║  Generate cards with QR codes linking to geographic locations ║
╚═══════════════════════════════════════════════════════════════╝

Basic usage:
  python main.py --input your_data.csv

All options:
  --input, -i       Input CSV file with activity data
  --card-template   Card markdown template (default: card_template.md)
  --output-dir      Directory for output files (default: output)
  --qr-dir          Directory for QR code images (default: qr_codes)
  --zoom            Zoom level for Google Maps URLs (default: 18)

For more information, see README.md
"""
    print(welcome)


def main():
    # Show welcome message if no arguments are provided
    if len(sys.argv) == 1:
        display_welcome()
        return True

    parser = argparse.ArgumentParser(description='Generate printable cards with QR codes')
    parser.add_argument('--input', '-i', type=str, default='20250107_Activity_1_0.csv',
                        help='Input CSV file with activity data')
    parser.add_argument('--card-template', type=str, default='card_template.md',
                        help='Card markdown template')
    parser.add_argument('--output-dir', type=str, default='output',
                        help='Directory for output files')
    parser.add_argument('--qr-dir', type=str, default='qr_codes',
                        help='Directory for QR code images')
    parser.add_argument('--zoom', type=int, default=18,
                        help='Zoom level for Google Maps URLs (default: 18)')
    
    args = parser.parse_args()
    
    # Create output directories
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.qr_dir, exist_ok=True)
    
    # 1. Validate required files
    if not check_file_exists(args.card_template):
        print("Please create a card template file and try again.")
        return False
    
    # 2. Validate CSV has required headers
    required_headers = ['OBJECTID', 'Your Name', 'Your Organization', 'Describe the opportunity',
                       'Is the opportunity feasible in the next 3 years?', 
                       'What do you expect would go smoothly?', 'What would you expect to be challenging?',
                       'Who might be a potential funder of this work?', 'x', 'y']
    
    if not validate_csv_headers(args.input, required_headers):
        return False
    
    # 3. Create links to web resource
    weblinks_csv = create_weblinks.process_csv(args.input, None, args.zoom)
    if not weblinks_csv:
        return False
    
    # 4. Create QR Codes
    if not create_qr_codes(args.input, args.qr_dir, weblinks_csv):
        return False
    
    # 5. Create card markdown files
    cards_dir = os.path.join(args.output_dir, 'cards')
    if not create_card_markdown_files(args.input, weblinks_csv, args.qr_dir, args.card_template, cards_dir):
        return False
    
    print(f"✅ Workflow completed successfully!")
    print(f"Output files are in: {args.output_dir}")
    print(f"QR codes are in: {args.qr_dir}")
    
    return True


if __name__ == "__main__":
    main()