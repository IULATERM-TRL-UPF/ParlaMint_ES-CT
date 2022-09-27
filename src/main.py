import util
import argparse
import sys
from tqdm import tqdm
import os


def main():
    parser = argparse.ArgumentParser("Parlamint 2022")
    parser.add_argument("-i", "--input", help="Docx Files Folder", 
        default=None)
    parser.add_argument("-o", "--output", help="XML Files Folder", default=None)
    parser.add_argument("-t", "--test", help="test script", default=None)
    args = parser.parse_args()

    root_dataset = args.input
    root_save = args.output
    
    if args.test:
        util.process_test()
        print("Done")
    elif root_dataset and root_save:
        FILEPATH = os.path.dirname(root_dataset)
        raw_dirs = set([d for d in os.listdir(FILEPATH)])
        print(raw_dirs)
        with tqdm(total=len(raw_dirs)) as pbar:
            for a in raw_dirs:
                if '.xml' in a:
                    util.file_creation(os.path.join(root_dataset, a),os.path.join(root_save, a))
                pbar.update(1)
    else:
        print("ERROR: No path.")

if __name__ == '__main__':
    main()
