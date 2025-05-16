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
    
    Args:
        template_path (str): Path to the template file
        context (dict): Dictionary of variables to use in the template
    
    Returns:
        str: Rendered template content
    """
    template_dir = os.path.dirname(template_path)
    template_file = os.path.basename(template_path)
    
    # Set up Jinja2 environment
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir or './'))
    template = env.get_template(template_file)
    
    # Render the template
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
            
            # Create card data structure
            card_data = {
                'title': front_matter.get('title', f"Card {card_file}"),
                'contact': front_matter.get('contact', ''),
                'description': front_matter.get('description', '').replace('|', '').strip(),
                'funders': front_matter.get('funders', ''),
                'feasible_3yr': front_matter.get('feasible_3yr', ''),
                'opportunities': front_matter.get('opportunities', '').replace('|', '').strip(),
                'challenges': front_matter.get('challenges', '').replace('|', '').strip(),
                'qr_code': os.path.join(qr_codes_dir, front_matter.get('qr_code_filename', ''))
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
            pandoc_cmd = [
                'pandoc', 
                latex_output_path, 
                '-o', output_pdf_path,
                '--pdf-engine=xelatex'
            ]
            
            subprocess.run(pandoc_cmd, check=True)
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