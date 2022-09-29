import util
import argparse
import sys
from tqdm import tqdm
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    parser = argparse.ArgumentParser("Parlamint 2022")
    parser.add_argument("-i", "--input", help="Docx Files Folder", 
        default=None)
    parser.add_argument("-o", "--output", help="ANA_XML Files Folder", default=None)
    parser.add_argument("-p", "--parameters", help="Members Excel Folder", default=None)
    parser.add_argument("-t", "--test", help="test script", default=None)
    args = parser.parse_args()

    root_docx_files = args.input
    root_ana_files = args.output
    root_parameters = args.parameters
    text = args.test
    print(ROOT_DIR)
    root_xml_files = os.path.join(ROOT_DIR[:-3], "xml_files/")
    
    if text:
        print("Testing")
        util.process_test(text)
        print("Done")
    elif root_docx_files and root_ana_files and root_parameters:
        FILEPATH = os.path.dirname(root_docx_files)
        print("Loading DOCX files")
        raw_dirs = set([d for d in os.listdir(FILEPATH)])
        print("Files to process: ", len(raw_dirs))
        print("Loading parameter files")
        df_parameter = util.read_members_id(root_parameters)
        print("Processing")
        with tqdm(total=len(raw_dirs)) as pbar:
            for a in raw_dirs:
                if '.docx' in a:
                    name_xml_file = util.docx_to_xml(os.path.join(root_docx_files, a),root_xml_files,root_parameters, df_parameter)
                    print("File "+a+" convert to xml and saved in "+os.path.join(root_xml_files, name_xml_file))
                    name_ana_file = util.xml_to_ana(os.path.join(root_xml_files, name_xml_file),os.path.join(root_ana_files, name_xml_file))
                    print("File "+name_xml_file+" convert to xml and saved in "+name_ana_file)
                pbar.update(1)
        print("Done")
    else:
        print("ERROR: No path.")

if __name__ == '__main__':
    main()
