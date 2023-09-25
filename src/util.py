
import pandas as pd
import os


def read_members_id(root_excel):
    file_path = os.path.join(root_excel, "members_id.csv")
    members_id = pd.read_csv(file_path, sep=";", encoding="latin-1").dropna().copy()
    members_id["Nombre"] = members_id["Nombre"].str.strip()
    members_id["matches"] = members_id["matches"].str.strip()
    members_id = members_id[["Nombre", "matches", "Id"]]
    return members_id


def statistics(df):
    tok_es, tok_ca, tok_ot = 0, 0, 0
    for _, row in df[df["style"] == "D3Textnormal"].iterrows():
        lang = row["lang"]
        text = row["text"]
        tokens = text.split()
        if lang == "es":
            tok_es += len(tokens)
        elif lang == "ca":
            tok_ca += len(tokens)
        else:
            tok_ot += len(tokens)
    sta = {"es": tok_es, "ca": tok_ca, "other": tok_ot}
    return sta