
import sys
import os
import shutil


def main():
    root_ana_files = "/mnt/d/UPF/proyecto_parlamint/DATA_TOTAL/"
    root_doc_files = "/mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/docx_files/"
    FILEPATH_ANA = os.path.dirname(root_ana_files)
    raw_dirs_ana = set([d for d in os.listdir(FILEPATH_ANA)])
    FILEPATH = os.path.dirname(root_doc_files)
    raw_dirs = set([d for d in os.listdir(FILEPATH)])
    files = []
    for a in raw_dirs_ana:
        code_ana = (a.split("-")[5]).split(".")[0]
        year_ana = (a.split("-")[2]).split("_")[1]
        for b in raw_dirs:
            code = b.split("-")[1]
            year = (b.split("-")[2]).split(".")[0]
            year = year[-4:]
            if code_ana == code and year_ana == year:
                files.append(b)
    for c in list(set(files)):
        shutil.move(FILEPATH+"/"+c, "/mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/docx_files_test/"+c)
if __name__ == '__main__':
    main()
