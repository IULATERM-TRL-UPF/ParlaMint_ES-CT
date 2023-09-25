
import pandas as pd
import os
import re
import numpy as np
from unicodedata import normalize

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def normalize_text(text):
    text = str(text)
    text = re.sub(
        r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1", 
        normalize( "NFD", text), 0, re.I
    )
    text = normalize( 'NFC', text)
    text = text.lower()
    text = " ".join(text.split())
    text = text.replace("’","'")
    return text
    
    
def build_fixed(df,members,date):
    df_speakers = pd.read_excel(os.path.join(ROOT_DIR, "MetadataSpeakersNB25-11.xlsx"))
    mem = {}
    cases = ["El secretari de la Mesa d’Edat","El representant de la comissió promotora"]
    for index, row in df.iterrows():
        if row['style'] == "CPresidncia":
            text = str(row['text'])
            text = normalize_text(text)
            flag_pre = 0
            for index, rows in members.iterrows():
                nombre = normalize_text(str(rows['Nombre']))
                matches = normalize_text(str(rows['matches']))
                if text.find(nombre) != -1 or text.find(matches) !=-1:
                    mem["presidente"] = str(rows['Nombre'])
                    flag_pre = 1
                    break
            if flag_pre == 0:
                for index_sp, row_sp in df_speakers.iterrows():
                    if int(date.strftime("%Y")) > 2014 and int(date.strftime("%Y"))<2018 and row_sp["rolePC1"] == "head" and row_sp["refPC1"] == "#PC":
                        mem["presidente"] = row_sp["Forename"]+" "+row_sp["Surname"]
                        break
                    if int(date.strftime("%Y")) >= 2018 and int(date.strftime("%Y"))<2021 and row_sp["rolePC2"] == "head" and row_sp["refPC2"] == "#PC":
                        mem["presidente"] = row_sp["Forename"]+" "+row_sp["Surname"]
                        break
        if row['style'] == 'D3Intervinent':
            if row['text'].find("(") != -1:
                cargo = row['text'].split(" (")[0]
                orador = (row['text'].split(" (")[1]).replace(")","")
                mem[cargo] = orador
            else: 
                for c in cases:
                    if row['text'].find(c) !=-1:
                        cargo = c
                        orador = row['text'].replace(c,"")
                        orador = " ".join(orador.split())
                        mem[cargo] = orador
    spk = []
    ta = []
    tb = []
    for index, rowt in df.iterrows():
        name = str(rowt["speaker"])
        for key, value in mem.items():
            if name.lower() in ("la presidenta","el presidente","el president","la president","la presidenta.") and key == "presidente":
                name = value
            elif normalize_text(name) == normalize_text(key):
                name = value
            elif normalize_text(name).find(normalize_text(key)) != -1:
                name = value  
        spk.append(name)
    df['speaker'] = spk
    return df
    

def get_speakers(df_sp):
    df = pd.read_excel(os.path.join(ROOT_DIR, "MetadataSpeakersNB25-11.xlsx"))
    speaker_name = []
    for index, row in df_sp.iterrows():
        name_sp = str(row["speaker"])
        name_sp = name_sp.replace("\n","")
        name_sp = normalize_text(name_sp)
        flag = 0
        if name_sp == "nan":
            continue
        #print("Buscar: ",name_sp)
        for index_t, row_t in df.iterrows():
            name = row_t["Forename"]+" "+row_t["Surname"]
            name = name.replace("\t","")
            name = normalize_text(name)
            alter_name = str(row_t["alter_name"])
            alter_name = alter_name.replace("\t","")
            if alter_name != "nan":
                if alter_name.find(";") != -1:
                    #print("op1",alter_name)
                    alter_names = alter_name.split(";")
                    for a in alter_names:
                        #print("op1.1",a)
                        a = normalize_text(a)
                        if name_sp == a:
                            #print("encontrado")
                            #print("\n")
                            flag = 1
                            break
                else:
                    alter_name = normalize_text(alter_name)
                    #print("op2",alter_name)
            #print("op3",name)
            if name_sp == name or name_sp == alter_name:
                #print("encontrado")
                #print("\n")
                flag = 1
                break
        if flag == 0:
            speaker_name.append(name_sp)
    with open('speakers_list.txt','r+') as f:
        old = f.read()
        f.seek(0)
        f.write(old)
        for names in speaker_name:
            f.write(names)
            f.write("\n")
            

def put_matches_fixed(df,file,date):
    df_speakers = pd.read_excel(os.path.join(ROOT_DIR, "MetadataSpeakersNB25-11.xlsx"))
    mat = []
    ids = []
    nombres = []
    for index, row in df.iterrows():
        if str(row["matches"]) == "nan":
            name_sp = str(row["Nombre"])
            name_sp_1 = name_sp
            name_sp = name_sp.replace("\n","")
            name_sp = normalize_text(name_sp)
            flag = 0
            for index_t, row_t in df_speakers.iterrows():
                name = row_t["Forename"]+" "+row_t["Surname"]
                name = name.replace("\t","")
                name_1 = name
                name = normalize_text(name)
                alter_name = str(row_t["alter_name"])
                alter_name = alter_name.replace("\t","")
                alter_name_1 = alter_name
                if name_sp == name:
                    nombres.append(name_sp_1)
                    mat.append(name_1)
                    ids.append(str(row_t["Person"]))
                    flag = 1
                    break
                if alter_name != "nan":
                    if alter_name.find(";") != -1:
                        alter_names = alter_name.split(";")
                        for a in alter_names:
                            a_1 = a
                            a = normalize_text(a)
                            if name_sp == a:
                                nombres.append(name_sp_1)
                                mat.append(a_1)
                                ids.append(str(row_t["Person"]))
                                flag = 1
                                break
                    else:
                        alter_name = normalize_text(alter_name)
                        if name_sp == alter_name:
                            nombres.append(name_sp_1)
                            mat.append(alter_name_1)
                            ids.append(str(row_t["Person"]))
                            flag = 1
                            break
                if normalize_text(row_t["roleName1"]) == normalize_text(row["speaker"]) or "el "+normalize_text(row_t["roleName1"]) == normalize_text(row["speaker"]):
                    nombres.append(name_sp_1)
                    mat.append(name_1)
                    ids.append(str(row_t["Person"]))
                    flag = 1
                    break
                elif normalize_text(row_t["roleName2"]) == normalize_text(row["speaker"]) or "el "+normalize_text(row_t["roleName2"]) == normalize_text(row["speaker"]):
                    nombres.append(name_sp_1)
                    mat.append(name_1)
                    ids.append(str(row_t["Person"]))
                    flag = 1
                    break
            if flag == 0:
                nombres.append(name_sp_1)
                mat.append(str(row["matches"]))
                ids.append(str("nan"))
        else:
            nombres.append(str(row["Nombre"]))
            mat.append(str(row["matches"]))
            ids.append(str(row["Id"]))
    df["Nombre"] = nombres        
    df["matches"] = mat
    df["Id"] = ids
    for index, row in df.iterrows():
        if row["Nombre"] != "nan" and row["Id"] == "nan":
            break
    return df
 


def remove_nan(df):
    matches = []
    Id = []
    speaker = []
    Nombre = []
    for index, row in df.iterrows():
        if str(row["speaker"]) == "nan":
            matches.append(np.nan)
            Id.append(np.nan)
            Nombre.append(np.nan)
            speaker.append(np.nan)
        else:
            Nombre.append(str(row["Nombre"]))
            speaker.append(str(row["speaker"]))
            matches.append(str(row["matches"]))
            Id.append(str(row["Id"]))
    df["Nombre"] = Nombre
    df["speaker"] = speaker
    df["matches"] = matches
    df["Id"] = Id
    return df
