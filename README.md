
# ParlaMint Spanish Catalan

This is the repository of the ParlaMint project for Spanish and Catalan. Here you can find the different scripts you need to get .ana and xml files. 

# Installation

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
python -m spacy download ca_core_news_trf
python -m spacy download es_core_news_sm
```

# Usage

```
usage: ParlaMint 2022 [-h] -i Docx_Files_Folder [-i INPUT]
                           -o XML_Files_Folder [-o OUTPUT] 
                           -t Script_Test [-t TEST]
required arguments:
  -i INPUT, --input INPUT
                        folder where the docx files are located 
  -o OUTPUT, --output OUTPUT
                        folder where the processed files will be saved
  -p PARAMETERS --parameters
						folder where the members excel files are located
optional arguments:
  -h, --help  show help message and exit
  -t TEST, --test TEST  input a Catalan text

```

## Creating .ana files with linguistic annotation of texts

DOCX files are stored in the docx_files folder, XML files in the xml_files folder and ANA files in the ana_files folder.

```
python src/main.py -i /PATH/ParlaMint_ES-CT/docx_files/ -o /PATH/ParlaMint_ES-CT/ana_files/ -p /PATH/ParlaMint_ES-CT/parameters/
```
Example

```
python main.py -i /mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/docx_files/ -o /mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/ana_files/ -p /mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/parameters/
```


## Testing Mode

```
python src/main.py -test catalan_text
```

Example

```
python src/main.py -test "Ras i curt, per poder començar a treballar, ja, des d'avui mateix, en la construcció d'un estat que doni respostes als enormes i urgents reptes actuals."
```

## Colab Mode

There is a file in Google Colab where you can use all the scripts in a simplified form, the Colab file is in the notebook folder


