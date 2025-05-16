#!/usr/bin/env python3

import os
import argparse
import pandas as pd
import subprocess
from pathlib import Path
import shutil
import jinja2


def render_template(template_path, context):
    """
    Render a Jinja2 template with the given context.
    Uses block_start_string, block_end_string, etc. to avoid conflicts with LaTeX syntax.
    
    Args:
        template_path (str): Path to the template file
        context (dict): Dictionary of variables to use in the template
    
    Returns:
        str: Rendered template content
    """
    template_dir = os.path.dirname(template_path)
    template_file = os.path.basename(template_path)
    
    # Read the template file content
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    # Set up Jinja2 environment with custom delimiters for LaTeX compatibility
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir or './'),
        block_start_string='{% ',
        block_end_string=' %}',
        variable_start_string='{{',
        variable_end_string='}}',
        comment_start_string='{#',
        comment_end_string='#}',
        # Trim whitespace for better LaTeX output
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False  # Don't escape HTML - not needed for LaTeX
    )
    
    # Get the template from the environment
    try:
        template = env.get_template(template_file)
        return template.render(**context)
    except Exception as e:
        # Fallback to direct string template if loading fails
        print(f"Warning: Using fallback template rendering method: {e}")
        template = jinja2.Template(
            template_content,
            block_start_string='{% ',
            block_end_string=' %}',
            variable_start_string='{{',
            variable_end_string='}}',
            comment_start_string='{#',
            comment_end_string='#}',
            trim_blocks=True,
            lstrip_blocks=True
        )
        return template.render(**context)


def generate_latex(cards_dir, latex_template_path, output_pdf_path, qr_codes_dir):
    """
    Generate a LaTeX document and compile it to a PDF.
    
    Args:
        cards_dir (str): Directory containing the card markdown files
        latex_template_path (str): Path to the LaTeX template
        output_pdf_path (str): Path to save the output PDF
        qr_codes_dir (str): Directory containing QR code images
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Default LaTeX template if not provided
    default_latex_template = r"""
\documentclass[a4paper]{article}
\usepackage{graphicx}
\usepackage{geometry}
\usepackage{multicol}
\usepackage{fancyhdr}
\usepackage{hyperref}
\usepackage{mdframed}

\geometry{margin=1cm}
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}

\begin{document}

{% for card in cards %}
\begin{mdframed}
  \section*{{{ card.title }}}
  \textbf{Contact:} {{ card.contact }}
  
  \textbf{Description:} {{ card.description }}
  
  \textbf{Potential Funders:} {{ card.funders }}
  
  \textbf{Feasible in next 3 years?} {{ card.feasible_3yr }}
  
  \textbf{Opportunities:} {{ card.opportunities }}
  
  \textbf{Challenges:} {{ card.challenges }}
  
  \vspace{0.5cm}
  \begin{center}
    \includegraphics[width=3cm]{{{ card.qr_code }}}
  \end{center}
\end{mdframed}

{% if not loop.last %}
\pagebreak
{% endif %}
{% endfor %}

\end{document}
"""
    
    try:
        # If template file doesn't exist, create it with the default template
        if not os.path.exists(latex_template_path):
            with open(latex_template_path, 'w') as f:
                f.write(default_latex_template)
            print(f"✅ Created default LaTeX template at: {latex_template_path}")
        
        # Get list of card markdown files
        card_files = sorted([f for f in os.listdir(cards_dir) if f.endswith('.md')])
        
        # Extract card data from markdown files
        cards_data = []
        for card_file in card_files:
            card_path = os.path.join(cards_dir, card_file)
            
            # Parse the markdown file
            with open(card_path, 'r') as f:
                content = f.read()
            
            # Extract front matter
            front_matter = {}
            if content.startswith('---'):
                _, front_matter_str, _ = content.split('---', 2)
                for line in front_matter_str.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        front_matter[key.strip()] = value.strip()
            
            # Get QR code path
            qr_filename = front_matter.get('qr_code_filename', '')
            qr_path = os.path.join(qr_codes_dir, qr_filename)
            
            # Check if QR code exists; use placeholder if it doesn't
            if not os.path.exists(qr_path):
                print(f"⚠️ QR code image not found: {qr_path}")
                qr_path = qr_filename  # Just use the filename and let LaTeX handle missing files

            # Clean text fields by removing pipe characters from YAML block style
            def clean_text(text):
                if text:
                    return text.replace('|', '').strip()
                return ''

            # Create card data structure
            card_data = {
                'title': front_matter.get('title', f"Card {card_file}"),
                'contact': front_matter.get('contact', ''),
                'description': clean_text(front_matter.get('description', '')),
                'funders': front_matter.get('funders', ''),
                'feasible_3yr': front_matter.get('feasible_3yr', ''),
                'opportunities': clean_text(front_matter.get('opportunities', '')),
                'challenges': clean_text(front_matter.get('challenges', '')),
                'qr_code': qr_path
            }
            
            cards_data.append(card_data)
        
        # Prepare context for LaTeX template
        context = {'cards': cards_data}
        
        # Render the LaTeX template
        latex_content = render_template(latex_template_path, context)
        
        # Write the LaTeX file
        output_dir = os.path.dirname(output_pdf_path)
        os.makedirs(output_dir, exist_ok=True)
        
        latex_output_path = os.path.join(output_dir, 'printable_cards.tex')
        with open(latex_output_path, 'w') as f:
            f.write(latex_content)
        
        print(f"✅ Generated LaTeX file: {latex_output_path}")
        
        # Compile LaTeX to PDF using pandoc
        try:
            # Check if pandoc is installed
            subprocess.run(['pandoc', '--version'], check=True, capture_output=True)
            
            # Run pandoc
            print(f"Running pandoc to generate PDF...")
            
            # First, try using pdflatex directly for better error messages
            try:
                print("Trying direct LaTeX compilation first...")
                latex_cmd = ['pdflatex', '-interaction=nonstopmode', '-output-directory', os.path.dirname(output_pdf_path), latex_output_path]
                latex_result = subprocess.run(latex_cmd, check=False, capture_output=True, text=True)
                
                # If successful, we'll have a PDF with the same base name as the .tex file
                pdf_from_latex = os.path.splitext(latex_output_path)[0] + '.pdf'
                if os.path.exists(pdf_from_latex):
                    # Rename to the desired output path if they're different
                    if pdf_from_latex != output_pdf_path:
                        shutil.move(pdf_from_latex, output_pdf_path)
                    print(f"✅ Generated PDF file with pdflatex: {output_pdf_path}")
                    return True
                else:
                    # Print LaTeX errors for debugging
                    if latex_result.stderr:
                        print(f"LaTeX errors: {latex_result.stderr}")
                    print("Direct LaTeX compilation failed, trying pandoc...")
            except Exception as e:
                print(f"LaTeX compilation attempt failed: {e}")
                print("Falling back to pandoc...")
            
            # Fall back to pandoc if direct LaTeX compilation failed
            try:
                pandoc_cmd = [
                    'pandoc', 
                    latex_output_path, 
                    '-o', output_pdf_path,
                    '--pdf-engine=xelatex'
                ]
                
                # Execute pandoc with verbose output
                result = subprocess.run(pandoc_cmd, check=False, capture_output=True, text=True)
                
                # Check if the PDF was created
                if os.path.exists(output_pdf_path):
                    print(f"✅ Generated PDF file with pandoc: {output_pdf_path}")
                    return True
                
                # Print stdout if available
                if result.stdout:
                    print(f"Pandoc output: {result.stdout}")
                    
                # Print any errors
                if result.stderr:
                    print(f"Pandoc warnings/errors: {result.stderr}")
                    
                # If we've reached here, both methods failed
                print("❌ PDF generation failed with both LaTeX and pandoc.")
                print("The LaTeX file was generated successfully and is available at:")
                print(f"  {latex_output_path}")
                print("You can try to compile it manually with: pdflatex -interaction=nonstopmode", latex_output_path)
                return False
                
            except FileNotFoundError:
                print("❌ Error: pandoc not found. Please install pandoc to generate PDFs.")
                print("The LaTeX file was generated successfully and is available at:")
                print(f"  {latex_output_path}")
                return False
            except Exception as e:
                print(f"❌ Error running pandoc: {e}")
                print("The LaTeX file was generated successfully and is available at:")
                print(f"  {latex_output_path}")
                return False
            print(f"✅ Generated PDF file: {output_pdf_path}")
            
        except FileNotFoundError:
            print("⚠️ Pandoc is not installed. Please install pandoc to generate the PDF.")
            print(f"LaTeX file was generated at: {latex_output_path}")
            return True  # Return true anyway since the LaTeX was generated
        
        return True
    
    except Exception as e:
        print(f"❌ Error generating LaTeX/PDF: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Create card PDFs from markdown files')
    parser.add_argument('--cards-dir', type=str, required=True,
                        help='Directory containing card markdown files')
    parser.add_argument('--latex-template', type=str, default='layout_template.tex',
                        help='LaTeX template file')
    parser.add_argument('--output-pdf', type=str, default='output/printable_cards.pdf',
                        help='Output PDF file path')
    parser.add_argument('--qr-codes-dir', type=str, default='qr_codes',
                        help='Directory containing QR code images')
    
    args = parser.parse_args()
    
    # Generate LaTeX and compile to PDF
    if generate_latex(args.cards_dir, args.latex_template, args.output_pdf, args.qr_codes_dir):
        print("✅ Card creation completed successfully!")
    else:
        print("❌ Card creation failed.")


if __name__ == "__main__":
    main()