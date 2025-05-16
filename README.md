# TOOL_printable_cards_QR_code

Generate a series of cards printed front and back with unique QR codes from a CSV dataset. This tool takes a CSV file with geographical coordinates and creates cards with QR codes linking to Google Maps locations.

## Project Status

Active

## Overview

This tool creates printable cards based on CSV data, with each card containing:
- Project title and description
- Contact information
- Feasibility information
- Opportunities and challenges
- Potential funders
- QR code linking to the geographic location on Google Maps

The workflow:
1. Process CSV data to extract project information
2. Generate Google Maps links from coordinates
3. Create QR codes for each location
4. Generate individual markdown cards
5. Compile cards into a printable PDF

## Installation

1. Clone this repository:
```bash
git clone [repository-url]
cd TOOL_printable_cards_QR_code
```

2. Set up a virtual environment (recommended):
```bash
# Create and setup virtual environment
./setup.sh

# Activate the virtual environment
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
```

3. Install required dependencies:
```bash
pip install -r requirements.txt
```

4. Optional: Install pandoc for PDF generation:
```bash
# On macOS
brew install pandoc

# On Ubuntu/Debian
sudo apt-get install pandoc

# On Windows with Chocolatey
choco install pandoc
```

## Usage

### Basic Usage

Run the main script to generate QR codes and cards:

```bash
python main.py --input your_data.csv
```

This will:
- Generate Google Maps URLs from coordinates
- Create QR codes for each URL
- Generate markdown files for each card
- Attempt to compile a PDF if pandoc is installed

### All Options

```bash
python main.py --input your_data.csv \
               --card-template card_template.md \
               --output-dir output \
               --qr-dir qr_codes \
               --zoom 18 \
               --use-mapping \
               --skip-pdf
```

Options explained:
- `--input, -i`: Path to the input CSV file
- `--card-template`: Path to the card markdown template (default: card_template.md)
- `--output-dir`: Directory for all output files (default: output)
- `--qr-dir`: Directory for QR code images (default: qr_codes)
- `--zoom`: Zoom level for Google Maps URLs (default: 18)
- `--use-mapping`: Use header_mapping.json to map CSV headers
- `--skip-pdf`: Skip PDF generation step (useful if pandoc is not installed)

### Input CSV Format

The input CSV must contain the following columns:
- `OBJECTID`: Unique identifier for each entry
- `Your Name`: Name of the contact person
- `Your Organization`: Organization of the contact person
- `Describe the opportunity`: Description of the opportunity
- `Is the opportunity feasible in the next 3 years?`: Feasibility of the opportunity
- `What do you expect would go smoothly?`: Expected smooth aspects
- `What would you expect to be challenging?`: Expected challenges
- `Who might be a potential funder of this work?`: Potential funders
- `x`: Longitude coordinate
- `y`: Latitude coordinate

### Individual Components

You can also run individual components separately:

1. Create weblinks from coordinates:
```bash
python create_weblinks.py input.csv --output links.csv --zoom 18
```

2. Generate QR codes:
```bash
python qrgen.py "https://www.google.com/maps?q=lat,lon&t=k&z=18" qr_codes/qr.png
```

3. Create cards from markdown:
```bash
python create_cards.py --cards-dir output/cards --latex-template layout_template.tex --output-pdf output/printable_cards.pdf
```

### Testing

You can run the test script to verify that all components are working correctly:

```bash
python test.py
```

This will test the weblink creation and QR code generation without external dependencies.

## Project Structure

```
TOOL_printable_cards_QR_code/
├── main.py                 # Main script to run the entire workflow
├── create_weblinks.py      # Creates Google Maps links from coordinates
├── qrgen.py                # Generates QR codes from URLs
├── create_cards.py         # Creates printable cards from markdown files
├── card_template.md        # Template for card content
├── layout_template.tex     # LaTeX template for PDF layout
├── setup.sh                # Script to setup virtual environment
├── test.py                 # Script to test core functionality
├── qr_codes/               # Directory for generated QR codes
├── output/                 # Directory for output files
│   ├── cards/              # Generated card markdown files
│   └── printable_cards.pdf # Final PDF with printable cards
└── requirements.txt        # Python dependencies
```

## Customization

### Card Template

You can modify the `card_template.md` file to change the content and layout of the cards. The template uses variables in double curly braces (e.g., `{{title}}`) that will be replaced with data from the CSV.

Available template variables:
- `{{title}}`: Project title
- `{{contact_person}}`: Contact person name
- `{{contact}}`: Contact person name (duplicate)
- `{{description}}`: Project description
- `{{potential_funders}}`: Potential funding sources
- `{{funders}}`: Potential funding sources (duplicate)
- `{{feasibility_next_3_years}}`: Feasibility assessment
- `{{feasible_3yr}}`: Feasibility assessment (duplicate)
- `{{opportunities}}`: Expected smooth aspects
- `{{challenges}}`: Expected challenging aspects
- `{{qr_code_filename}}`: QR code filename
- `{{qr_code}}`: QR code file path

### LaTeX Template

The `layout_template.tex` file controls the final PDF layout. You can customize this file to change the appearance of the printed cards.

The template uses Jinja2 syntax for variables and loops:
- `{% for card in cards %}` ... `{% endfor %}`: Loop through all cards
- `{{ card.title }}`: Insert card title
- Other variables: `card.contact`, `card.description`, `card.funders`, etc.

## Troubleshooting

### PDF Generation

If PDF generation fails or is skipped, there are several options:

1. **Check if pandoc is installed**:
   ```bash
   pandoc --version
   ```
   If not installed, follow the installation instructions in the Installation section.

2. **Check if LaTeX is installed**:
   Pandoc requires a LaTeX distribution to generate PDFs. Install one of these:
   - macOS: `brew install --cask mactex-no-gui` or `brew install --cask basictex`
   - Ubuntu/Debian: `sudo apt-get install texlive-xetex`
   - Windows: Install MiKTeX or TeX Live

3. **Skip PDF generation**:
   If you don't want to install pandoc or LaTeX, use the `--skip-pdf` flag:
   ```bash
   python main.py --input your_data.csv --skip-pdf
   ```

4. **Generate PDF separately**:
   After running the main script with `--skip-pdf`, you can generate PDFs manually:
   ```bash
   python create_cards.py --cards-dir output/cards --output-pdf output/printable_cards.pdf
   ```

5. **Alternative PDF generation**:
   You can also use other tools to generate PDFs from the markdown or LaTeX files in the output directory.

### QR Code Generation

If QR code generation fails, ensure that the required libraries are installed:
```bash
pip install qrcode[pil] Pillow
```

### CSV Format Issues

If the script reports missing headers, you have several options:

1. Modify your CSV file to use the exact header names required by the tool.

2. Use the header mapping feature:
   - When the script detects missing headers, it will offer to create a mapping file
   - Follow the prompts to map your existing headers to the required ones
   - Run the script again with the `--use-mapping` flag:
   ```bash
   python main.py --input your_data.csv --use-mapping
   ```

3. The tool also automatically handles minor differences like trailing spaces or case changes.

**Example mapping process:**
```
❌ CSV is missing required headers: Describe the opportunity
Would you like to create a header mapping file to resolve this issue? (y/n)
y
Enter the corresponding header in your CSV for 'Describe the opportunity' (or leave blank to skip):
Describe the opportunity 
✅ Header mapping saved to 'header_mapping.json'
Run the script again with the --use-mapping flag to use this mapping
```

## License

See the LICENSE file for details.

## Contributors

- RTGS Lab