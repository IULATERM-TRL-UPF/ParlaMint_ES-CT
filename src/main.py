from util import process
import argparse
import pandas as pd
import sys
from tqdm import tqdm
import os


def main():
    parser = argparse.ArgumentParser("Parlamint 2022")
    parser.add_argument("-i", "--input", help="Docx Files Folder", 
        default=None)
    parser.add_argument("-o", "--output", help="XML Files Folder", default=None)
    args = parser.parse_args()

    root_dataset = args.input
    root_translate = args.output


    elif root_dataset and root_translate:
        FILEPATH = os.path.dirname(root_dataset)
        raw_dirs = set([convert(d) for d in os.listdir(RAW_PATH)])
        lad_translations = []
        with tqdm(total=translate_iter) as pbar:
            for a in translate_iter:
                lad_translations.append(process(file))
                pbar.update(1)
        df[CSV_LADINO_TAG] = lad_translations
        df.to_csv(root_translate, sep='\t', index=False)
    else:
        print("ERROR: No sentence or dataset given.")

if __name__ == '__main__':
    main()
