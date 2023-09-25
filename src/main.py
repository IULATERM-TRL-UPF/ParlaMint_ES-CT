# -*- coding: utf-8 -*-

import util_freeling as util
import argparse
import sys
from tqdm import tqdm
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIRs = os.path.abspath(os.curdir)
print(ROOT_DIR)
print(ROOT_DIRs)


def parse_arguments():
    parser = argparse.ArgumentParser("Parlamint 2022")
    parser.add_argument("-a", "--action", help="Processing Type: s-statistics, p-process", default=None)
    parser.add_argument("-i", "--input", help="Docx Files Folder", default=None)
    parser.add_argument("-o", "--output", help="ANA_XML Files Folder", default=None)
    parser.add_argument("-p", "--parameters", help="Members Excel Folder", default=None)
    parser.add_argument("-s", "--speaker", action='store_true', help="Gets all absent speakers")
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    root_docx_files = args.input
    root_ana_files = args.output
    root_parameters = args.parameters
    root_xml_files = os.path.join(ROOT_DIR[:-3], "xml_files/")
    
    if args.action == "s":
    
        print("Corpu's Statistics")
        FILEPATH = os.path.dirname(root_docx_files)
        print("Loading DOCX files")
        raw_dirs = set([d for d in os.listdir(FILEPATH)])
        print("Files to process: ", len(raw_dirs))
        print("Loading parameter files")
        df_parameter = util.read_members_id(root_parameters)
        print("Processing")
        tokens_spanish = 0
        tokens_catalan = 0
        tokens_other = 0
        for a in raw_dirs:
            if '.docx' in a:
                name_xml_file, sta = util.docx_to_xml(os.path.join(root_docx_files, a),root_xml_files,root_parameters, df_parameter)
                if name_xml_file == '':
                    name_xml_file, sta = util.docx_to_xml_fixed(os.path.join(root_docx_files, a),root_xml_files,root_parameters, df_parameter)
                for key, value in sta.items():
                   if key == "es":
                      tokens_spanish += value
                   if key == "ca":
                      tokens_catalan += value
                   if key == "other":
                      tokens_other += value
        print("Done")
        print("Total tokens_spanish: ",tokens_spanish)
        print("Total tokens_catalan: ",tokens_catalan)
        print("Total tokens_other: ",tokens_other)
        print("Total tokens: ", (tokens_catalan+tokens_spanish+tokens_other))
        
    elif args.action == "p":
    
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
                    name_xml_file, sta = util.docx_to_xml(os.path.join(root_docx_files, a),root_xml_files,root_parameters, df_parameter)
                    if name_xml_file == '':
                        name_xml_file, sta = util.docx_to_xml_fixed(os.path.join(root_docx_files, a),root_xml_files,root_parameters, df_parameter)
                        if name_xml_file != '':
                            print("File "+a+" convert to xml and saved in "+os.path.join(root_xml_files, name_xml_file))
                            name_ana_file = util.xml_to_ana(os.path.join(root_xml_files, name_xml_file),os.path.join(root_ana_files, name_xml_file))
                            if name_ana_file != '':
                                print("File "+name_xml_file+" convert to xml and saved in "+name_ana_file)
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
