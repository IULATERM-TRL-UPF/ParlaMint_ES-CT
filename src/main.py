# -*- coding: utf-8 -*-
#import util
import util_freeling as util
import argparse
import sys
from tqdm import tqdm
import os
#import warnings
#warnings.filterwarnings("ignore")

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    parser = argparse.ArgumentParser("Parlamint 2022")
    parser.add_argument("-i", "--input", help="Docx Files Folder", 
        default=None)
    parser.add_argument("-o", "--output", help="ANA_XML Files Folder", default=None)
    parser.add_argument("-p", "--parameters", help="Members Excel Folder", default=None)
    parser.add_argument("-t", "--test", help="Docx Files Folder -- Test", default=None)
    parser.add_argument("-s", "--speaker", action='store_true', help="Gets all absent speakers")
    args = parser.parse_args()

    root_docx_files = args.input
    root_ana_files = args.output
    root_parameters = args.parameters
    root_test = args.test
    print(ROOT_DIR)
    root_xml_files = os.path.join(ROOT_DIR[:-3], "xml_files/")
    
    if root_test:
        print("Testing")
        FILEPATH = os.path.dirname(root_test)
        print("Loading DOCX files")
        raw_dirs = set([d for d in os.listdir(FILEPATH)])
        print("Files to process: ", len(raw_dirs))
        print("Loading parameter files")
        df_parameter = util.read_members_id(root_parameters)
        print("Processing")
        with open('files_no_processed.txt', 'w') as f:
            with tqdm(total=len(raw_dirs)) as pbar:
                for a in raw_dirs:
                    if '.docx' in a:
                        name_xml_file = util.docx_to_xml(os.path.join(root_test, a),root_xml_files,root_parameters, df_parameter)
                        if name_xml_file == '':
                            name_xml_file = util.docx_to_xml_fixed(os.path.join(root_test, a),root_xml_files,root_parameters, df_parameter)
                            if name_xml_file == '':
                                f.write(a)
                                f.write("\n")
                    pbar.update(1)
        print("Los archivos que no se pudieron procesar estan en el folder 'ERRORS'")
        print("Done")
    elif args.speaker:
        print("Get Speakers")
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
                    if name_xml_file == '':
                        name_xml_file = util.docx_to_xml_fixed(os.path.join(root_docx_files, a),root_xml_files,root_parameters, df_parameter)
                pbar.update(1)
        print("Done")
    elif root_docx_files and root_ana_files and root_parameters:
        FILEPATH = os.path.dirname(root_docx_files)
        print("Loading DOCX files")
        raw_dirs = set([d for d in os.listdir(FILEPATH)])
        print("Files to process: ", len(raw_dirs))
        print("Loading parameter files")
        df_parameter = util.read_members_id(root_parameters)
        print("Processing")
        with open('files_no_processed.txt', 'w') as f:
            with tqdm(total=len(raw_dirs)) as pbar:
                for a in raw_dirs:
                    if '.docx' in a:
                        name_xml_file = util.docx_to_xml(os.path.join(root_docx_files, a),root_xml_files,root_parameters, df_parameter)
                        if name_xml_file == '':
                            name_xml_file = util.docx_to_xml_fixed(os.path.join(root_docx_files, a),root_xml_files,root_parameters, df_parameter)
                            if name_xml_file != '':
                                print("File "+a+" convert to xml and saved in "+os.path.join(root_xml_files, name_xml_file))
                                name_ana_file = util.xml_to_ana(os.path.join(root_xml_files, name_xml_file),os.path.join(root_ana_files, name_xml_file))
                                if name_ana_file != '':
                                    print("File "+name_xml_file+" convert to xml and saved in "+name_ana_file)
                            else:
                                f.write(a)
                                f.write("\n")
                        else:
                            print("File "+a+" convert to xml and saved in "+os.path.join(root_xml_files, name_xml_file))
                            name_ana_file = util.xml_to_ana(os.path.join(root_xml_files, name_xml_file),os.path.join(root_ana_files, name_xml_file))
                            if name_ana_file != '':
                                print("File "+name_xml_file+" convert to xml and saved in "+name_ana_file)
                    pbar.update(1)
        print("Done")
    else:
        print("ERROR: No path.")

if __name__ == '__main__':
    main()
