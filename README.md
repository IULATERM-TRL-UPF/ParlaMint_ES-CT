
# ParlaMint Spanish Catalan

This is the repository of the ParlaMint project for Spanish and Catalan. This repository contains the Python code for processing Parliament 2022 documents. Here you can find the different scripts you need to get .ana and xml files. 
Our Python code offers two functionalities:

Corpus Statistics (-a s): This mode analyzes the corpus and provides statistics on the number of tokens in each language (Spanish, Catalan, and others).
Document Processing (-a p): This mode processes DOCX files and converts them to XML and ANA files. It also attempts to fix date formatting issues in the resulting XML files.

## Installation

In order to clone this repository:
```
git clone https://github.com/IULATERM-TRL-UPF/ParlaMint_ES-CT
```

After, create a virtualenvironment and install all the requirements
```
python -m venv venv
source venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
```

## Usage

The main script is `main.py`. It accepts the following arguments:

- `-a, --action`: Action to perform. Possible values:
  - `s`: Get corpus statistics
  - `p`: Process DOCX files to generate XML and ANA

- `-i, --input`: Directory containing the input DOCX files. Default `docx_files/`.

Examples:

```bash
# Get statistics
python main.py -a s
```

This script will obtain the number of words, sentences processed for each language used (Spanish or Catalan).

```bash
# Process files
python main.py -a p -i docx_files/
```

This script will process the DOCX files in the input directory and generate the XML files in xml_files/ and the ANA files in ana_files/.


## Project structure

* `main.py`: Entry point. Parses arguments and calls other modules.

* `src/util.py`: Utility functions. 

* `src/xml_file.py`: Functions to convert DOCX to XML.

* `src/ana_file.py`: Functions to convert XML to ANA.

* `src/fix_xml.py`: Functions to fix issues in generated XML.

* `docx_files/`: Directory containing input DOCX files.

* `parameters/`: Parameters needed for processing.

* `xml_files/`: Directory where generated XML files are saved.

* `ana_files/`: Directory where generated ANA files are saved.


## **Contact**

For any questions or suggestions contact:

* **nuria.bel@upf.edu**
* **rodolfojoel.zevallos@upf.edu**

