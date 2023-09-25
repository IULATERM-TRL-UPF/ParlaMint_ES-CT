
import os
import src.freeling as freeling
import json
import ast
import time


def to_conll(command, lang):
    start_time_all = time.time()
    df_nlp = freeling.nlp_freeling(command)
    df_nlp.to_csv("/mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/generative_files/df_nlp_b.csv", index=False)
    df_nlp = fix_dataframe(df_nlp)
    df_nlp.to_csv("/mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/generative_files/df_nlp_a.csv", index=False)
    df_nlp = put_sintax(df_nlp, lang)
    df_nlp = fix_punct(df_nlp)
    nlp_conll = df_to_conll(df_nlp)
    end_time_all = time.time()
    elapsed_time = end_time_all - start_time_all
    #print("time conll: ",elapsed_time)
    return nlp_conll


def df_to_conll(df_ner):
    conll_list = []
    flag = 0
    for index, row in df_ner.iterrows():
        flag_add = ""
        if flag != int(row["sent_id"]):
            flag += 1
            flag_add = "\n"
        if row["text"].find("'") != -1:
            misc = "SpaceAfter=No"
        else:
            misc = "_"
        if str(row["morph"]) == "()" or str(row["morph"]) == "":
            morph = "_"
        else:
            morph = row["morph"]
        row_conll = str(row["token_id"])+"\t"+str(row["text"])+"\t"+str(row["lemma"])+"\t"+str(row["pos"])+"\t"+str(row["pos"])+"\t"+str(morph)+"\t"+ str(row["head_new"])+"\t"+str(row["deprel_new"])+"\t"+str("_")+"\t"+str(misc)+"\t"+str(row["token_ner_type"])+"\t"+str(row["token_ner_type"])+"\t"+str(row["join"])+"\t"+str(row["word_id"])+"\t"+str(row["join_norm"])+"\t"+str(row["punct"])+"\n"
        conll_list.append(flag_add+row_conll)
    doc_final = ''.join([str(x) for x in conll_list])
    return doc_final


def fix_punct(df):
    punct = []
    for index, row in df.iterrows():
        if row["deprel_new"] != "punct":
            id_find = row["word_id"]
            flag_all = 0
            for indexs, rows in df.iterrows():
                if int(id_find)+1 == int(rows["word_id"]):
                    if rows["deprel_new"] == "punct":
                        punct.append(1)
                    else:
                        punct.append(0)
                    flag_all = 1
                    break
            if flag_all == 0:
                punct.append(0)
        else:
            punct.append(0)
    df["punct"] = punct
    return df


def put_sintax(df, lang):
    head = []
    deprel = []
    token = [str(row["text"]) for index, row in df.iterrows()]
    with open('/mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/generative_files/tokens_vertical.txt', 'w') as f:
        for t in token:
            f.write(t)
            if t == "." or t=="?" or t == "!":
                f.write("\n")
            f.write("\n")
    
    while True:
        try:
            if lang == "es":
                os.system("curl -F input=vertical -F data=@/mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/generative_files/tokens_vertical.txt -F model=spanish-ancora-ud-2.10-220711 -F parser= http://lindat.mff.cuni.cz/services/udpipe/api/process > /mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/generative_files/output_ud.json")
            else:
                os.system("curl -F input=vertical -F data=@/mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/generative_files/tokens_vertical.txt -F model=catalan-ancora-ud-2.10-220711 -F parser= http://lindat.mff.cuni.cz/services/udpipe/api/process > /mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/generative_files/output_ud.json")
            lenght = os.path.getsize('/mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/generative_files/output_ud.json')
            #print("len: ",lenght)
            if lenght != 0:
                break
        except Exception as e:
            print(e)
            
    f = open('/mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/generative_files/output_ud.json')
    data = json.load(f)
    result = data["result"]
    result = result.replace("# generator = UDPipe 2, https://lindat.mff.cuni.cz/services/udpipe\n# udpipe_model = catalan-ancora-ud-2.10-220711\n# udpipe_model_licence = CC BY-NC-SA\n# newdoc\n# newpar\n# ","")
    result = result.replace("# generator = UDPipe 2, https://lindat.mff.cuni.cz/services/udpipe\n# udpipe_model = spanish-ancora-ud-2.10-220711\n# udpipe_model_licence = CC BY-NC-SA\n# newdoc\n# newpar\n# ","")
    result = result.replace("\n\n","\n")
    result = result.replace("# ","")
    results = result.split("sent_id = ")
    results = [s for s in results if s != '']
    flag = 1
    for r in results:
        text_1 = "sent_id = "+str(flag)+"\n"
        text_2 = "# sent_id = "+str(flag)+"\n"
        r = r.replace(text_2,"")
        r = r.replace(text_1,"")
        r = r.replace("\n\n","\n")
        flag += 1
        rs = r.split("\n")
        rs = [s for s in rs if s != ""]
        rs = rs[1:]
        for a in rs:
            if a == "#":
                continue
            p = a.split("\t")
            head.append(p[6])
            deprel.append(p[7])
    df["head_new"] = head
    df["deprel_new"] = deprel
    return df
     

def fix_dataframe(df):
    for index, row in df.iterrows():
        jo = str(row["join"])
        token_join = ast.literal_eval(jo)
        if len(token_join) > 0:
            for indexs, rows in df.iterrows():
                if int(rows["word_id"]) in token_join:
                    for t_j in token_join:
                        if int(rows["word_id"]) == t_j:
                            df.at[(t_j-1),'join']="[0]"                   
    return df