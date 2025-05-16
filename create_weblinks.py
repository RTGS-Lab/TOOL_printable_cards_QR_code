#!/usr/bin/env python3

import argparse
import pandas as pd
from pathlib import Path
import csv


def create_weblink(lat, lon, zoom=18):
    """
    Create a Google Maps URL for a given latitude and longitude with a specified zoom level.
    
    Args:
        lat (float): Latitude coordinate
        lon (float): Longitude coordinate
        zoom (int): Zoom level (default 18)
        
    Returns:
        str: Google Maps URL
    """
    return f"https://www.google.com/maps?q={lat},{lon}&t=k&z={zoom}"


def process_csv(input_file, output_file=None, zoom=18):
    """
    Process the input CSV file to create weblinks based on coordinates.
    
    Args:
        input_file (str): Path to input CSV file
        output_file (str, optional): Path to output CSV file. If not provided, will use '<input>_with_links.csv'
        zoom (int): Zoom level for the Google Maps URL (default 18)
    
    Returns:
        str: Path to the output CSV file
    """
    # Determine output filename if not provided
    if output_file is None:
        input_path = Path(input_file)
        output_file = f"{input_path.stem}_with_links{input_path.suffix}"
    
    # Read the CSV file
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"L Error reading CSV file: {e}")
        return None
    
    # Validate required columns
    if 'x' not in df.columns or 'y' not in df.columns:
        print("L Error: Input CSV must contain 'x' and 'y' columns for coordinates")
        return None
    
    # Create the weblinks column
    df['WebLink'] = df.apply(lambda row: create_weblink(row['y'], row['x'], zoom), axis=1)
    
    # Save the updated CSV
    try:
        df.to_csv(output_file, index=False)
        print(f" Generated web links and saved to: {output_file}")
        return output_file
    except Exception as e:
        print(f"L Error saving output CSV: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description='Create web links from CSV coordinates')
    parser.add_argument('input', type=str, help='Input CSV file with x,y coordinates')
    parser.add_argument('--output', '-o', type=str, help='Output CSV file (default: <input>_with_links.csv)')
    parser.add_argument('--zoom', '-z', type=int, default=18, help='Zoom level for Google Maps URLs (default: 18)')

    args = parser.parse_args()
    process_csv(args.input, args.output, args.zoom)


if __name__ == "__main__":
    main()