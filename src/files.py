import pandas as pd
import os

def main():

    path = "resource/files_tr/"
    corpus_id = []
    src_1 = []
    src_2 = []
    trg = []
    dataset = pd.read_csv("resource/dataset_tr.csv", sep="\t")
    for root, dirs, files in os.walk(path):
        for file in files:
            print(file)
            if file.find(".csv") != -1:
                df = pd.read_csv(path+file, sep="\t")
                corpus_id = df["Source"]
                src_1 = df["Turkish"]
                src_2 = df["Spanish"]
                trg = df["Ladino"]
                p = {"corpus-id": corpus_id, "src_1": src_1, "src_2": src_2, "trg": trg}
                data = pd.DataFrame(p)
                dataset = pd.concat([dataset, data], axis=0)

    dataset.to_csv("dataset_tr.csv", sep='\t', index=False)


if __name__ == '__main__':
    main()