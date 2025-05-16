# Specification

# Inputs
- CSV of:
```
OBJECTID	Your Name	Your Organization	Describe the opportunity 	Is the opportunity feasible in the next 3 years?	How easy will it be to get going on this opportunity? 1-5 (1: very easy, 5: very hard)	What do you expect would go smoothly?	What would you expect to be challenging?	Who might be a potential funder of this work?	GlobalID	CreationDate	Creator	EditDate	Editor	x	y
6	Bennett Myhran	City of Wayzata	Invasive species management in remnant Big Woods 	Ongoing	3	Funding 	Success	City of Wayzata	0d71c6c3-fb2e-43e0-8062-5e36a4592521	4/28/25 14:15	runcklab_UMN	4/28/25 14:15	runcklab_UMN	-93.4983819	44.97368603
```
- Card markdown template (default name: `card_template.md`)
- Latex layout template (default name: `layout_template.tex`)

# Outputs
- Folder with: 1) qr_codes, 2) card markdown files.
- PDF of `printable_cards.pdf` with arbitrary size (defined in `output_config`) to be printed front an back with `n` cards on each page.


# Workflow
`main.py` runs the workflow.

1. Validate required files present. If not, provide templates for Latex and/or Card.
2. Validate CSV has required header. If not, return message to user with an output csv template.
3. Create links to web resource `create_weblinks.py`; to start, it will take the x and y from the csv and create a weblink to a google maps location of form: https://www.google.com/maps?q=<lat>,<lon>&t=k&z=<zoom> with zoom of 18.
3. Create QR Codes using `qrgen.py` and place into `qr_codes` directory. QR codes should be labeled by the ObjectID. Create a `qr_metadata.csv` summarizing all of the QR codes in the directory.
4. `create_cards.py`. This file uses the `card_template.md`, the CSV of inputs, latex tempalte, and the QR codes to generate inputs and run pandoc.
5. Output the final pdf for printing. 


