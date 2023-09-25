# -*- coding: utf-8 -*-

# Importamos los módulos necesarios
import src.util as util
import src.xml_file as xml_file
import src.ana_file as ana_file
import argparse
import os
from tqdm import tqdm
import time
import src.fix_xml as fix_xml

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Parlamint 2022")
    parser.add_argument("-a", "--action",
                        help="Tipo de ejecución que desea realizar (s = estadistica del corpus, p = procesamiento de los archivos)",
                        default="p")
    parser.add_argument("-i", "--input",
                        help="The directory containing the input DOCX files",
                        default= os.path.join(ROOT_DIR, "docx_files/"))
    args = parser.parse_args()
    return args


def main():
    
    args = parse_args()
    root_docx_files = args.input
    root_parameters = os.path.join(ROOT_DIR, "parameters/")
    root_ana_files = os.path.join(ROOT_DIR, "ana_files/")
    root_xml_files = os.path.join(ROOT_DIR, "xml_files/")
    
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
                start_time = time.time()
                name_xml_file, sta = util.docx_to_xml(os.path.join(root_docx_files, a),root_xml_files,root_parameters, df_parameter)
                end_time = time.time()
                elapsed_time = end_time - start_time
                print(elapsed_time)
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
        
        if not os.path.exists(root_xml_files):
            os.makedirs(root_xml_files)
        if not os.path.exists(root_ana_files):
            os.makedirs(root_ana_files)
        print(root_docx_files)
        print("Loading DOCX files")
        raw_dirs = set([d for d in os.listdir(root_docx_files)])
        print("Files to process: ", len(raw_dirs))
        print("Loading parameter files")
        #df_parameter = util.read_members_id(root_parameters)
        print("Processing")
        with tqdm(total=len(raw_dirs)) as pbar:
            for a in raw_dirs:
                print("file: ", a)
                if '.docx' in a:
                    name_xml_file = xml_file.docx_to_xml(os.path.join(root_docx_files, a),root_xml_files,root_parameters)
                    print("name_xml_file: ",name_xml_file)
                    if name_xml_file == False:
                        print("Intenta el otro metodo")
                        name_xml_file = xml_file.docx_to_xml_fixed(os.path.join(root_docx_files, a),root_xml_files,root_parameters)
                        print("name_xml_file: ",name_xml_file)
                        if name_xml_file != False:
                            file_xml = name_xml_file.split(".")[0]
                            fix_xml.fix_date(os.path.join(root_xml_files, f"{file_xml}.xml"))
                        if name_xml_file != False:
                            print("Great File "+a+" convert to xml and saved in "+root_xml_files)
                            file_ana = ana_file.xml_to_ana(os.path.join(root_xml_files, name_xml_file),os.path.join(root_ana_files, name_xml_file))
                            if file_ana != '':
                                print("File "+name_xml_file+" convert to xml and saved in "+file_ana)
                            else:
                                print("ERROR: File "+a+" not convert to ana xml")
                        else:
                            print("ERROR: File "+a)
                    else:
                        print("File "+a+" convert to xml and saved in "+root_xml_files)
                        if name_xml_file != False:
                            file_xml = name_xml_file.split(".")[0]
                            fix_xml.fix_date(os.path.join(root_xml_files, f"{file_xml}.xml"))
                        file_ana = ana_file.xml_to_ana(os.path.join(root_xml_files, name_xml_file),os.path.join(root_ana_files, name_xml_file))
                        if name_xml_file != False:
                            print("File "+name_xml_file+" convert to xml and saved in "+file_ana)
                        else:
                            print("ERROR: File "+a+" not convert to ana xml")
                pbar.update(1)
        print("Done")
    else:
        print("ERROR: No path.")
    

if __name__ == '__main__':
    main()
