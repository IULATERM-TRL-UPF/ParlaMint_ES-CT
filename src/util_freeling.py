# -*- coding: utf-8 -*-
import pandas as pd

import sys
import re
import ast
import os
import json
import lxml
import zipfile

from datetime import datetime

from df_build import df_build
from df_build_2 import df_build_2
from tei_header import tei_header
from to_xml import to_xml
from to_xml_2 import to_xml_2
from xml_parser import p_parser

import xml.etree.ElementTree as ET
from xml.dom import minidom
ET.register_namespace('','http://www.tei-c.org/ns/1.0')
from copy import deepcopy

emptyline_re = re.compile('\n\s+\n')

contador = 1


def read_members_id(root_excel):
    members_id = pd.read_csv(os.path.join(root_excel, "members_id.csv"), sep=";", encoding='latin-1')
    members_id = members_id.dropna().copy()
    members_id['Nombre'] = members_id['Nombre'].str.strip()
    members_id['matches'] = members_id['matches'].str.strip()
    members_id = members_id[['Nombre', 'matches', 'Id']]
    return members_id


def read_members(root_excel,file_date):
    members = pd.read_csv(os.path.join(root_excel, "special_denominations.csv"), sep="\t", encoding='latin-1')
    members['Alta'] =  pd.to_datetime(members['Alta'], infer_datetime_format=True)
    members['Baja'] =  pd.to_datetime(members['Baja'], infer_datetime_format=True)
    members = pd.concat([members,members_file])
    members = members.loc[(members['Alta'] <= file_date) &
                          (members['Baja'] >= file_date), ['Cargo', 'Nombre']]
    return members


def fix_parsed(df, lang):
    head = []
    deprel = []
    token = [str(row["text"]) for index, row in df.iterrows()]
    with open('tokens_vertical.txt', 'w') as f:
        for t in token:
            f.write(t)
            if t == "." or t=="?":
                f.write("\n")
            f.write("\n")
    if lang == "es":
        os.system("curl -F input=vertical -F data=@tokens_vertical.txt -F model=spanish-ancora-ud-2.10-220711 -F parser= http://lindat.mff.cuni.cz/services/udpipe/api/process > output_ud.json")
    else:
        os.system("curl -F input=vertical -F data=@tokens_vertical.txt -F model=catalan-ancora-ud-2.10-220711 -F parser= http://lindat.mff.cuni.cz/services/udpipe/api/process > output_ud.json")
    
    f = open('output_ud.json')
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
     

def docx_to_xml(file,file_save,root_parameters, members_id):
    src_dfs = []
    appended_dfs = []
    try:
        document = zipfile.ZipFile(file)
        doc_xml = document.read("word/document.xml")
        rooted = ET.fromstring(doc_xml)
        file_codes = (file.split("/")[-1]).split('.')[0]
        file_code = file_codes.split("-")[-1]
        file_mini_code = file_codes.split("-")[-2]
        file_date =  file_code[-4:] + '-' + file_code[2:4] + '-' + file_code[0:2]
        file_name = 'ParlaMint-ES-CT_' + file_date + '-' + file_mini_code
        file_date = datetime.strptime(file_date, '%Y-%m-%d')
        file_date_short = datetime.strftime(file_date, '%Y-%m-%d')
        file_sesion = int(file_mini_code[0:2]) 
        file_meeting = int(file_mini_code[2:])
        if file_date_short >= '2019-11-01':
          tei_ana = '#covid'
        else:
          tei_ana = '#reference'
        df = p_parser(rooted)
        src_dfs.append(df) #se preservan los DF originales
        df = df_build(df, file_name, file_date, root_parameters, members_id)
        header = tei_header(df, file_name, file_date_short, file_sesion, file_meeting) #se crea el encabezado a partir del DataFrame, la función necesita nombre, fecha, sesión y reunión
        text = to_xml(df, tei_ana) #se crea el cuerpo del XML, necesita también como argumento la etiqueta de subcorpus.
        #se crea el elemento TEI y sus atributos:
        TEI = ET.Element('TEI') 
        TEI.attrib['ana'] = "#parla.sitting "+tei_ana
        TEI.attrib['xmlns'] = "http://www.tei-c.org/ns/1.0"
        TEI.attrib['xml:lang'] = 'ca' #catalán
        TEI.attrib['xml:id'] = file_name
        TEI.append(header) #se adjunta el header al elemento TEI
        TEI.append(text) #se adjunta el body al elemento TEI

        xmlstr = minidom.parseString(ET.tostring(TEI)).toprettyxml(indent="   ") #se transforma el árbol a una cadena de caracteres, para imprimirla luego en un archivo nuevo
        open(os.path.join(file_save,file_name +'.xml'),'w').write(xmlstr) #se crea un archivo nuevo y se escribe el contenido de la cadena de caracteres anterior
        #print(file_name +'.xml creado')
        appended_dfs.append(df) #se adjunta el DataFrame a lista de DataFrames
        return file_name+'.xml'
    except:
        #file_name_fixed = docx_to_xml_fixed(file,file_save,root_parameters, members_id)
        return ''


def fix_text(text):
    text = text.replace("’","'")
    return text


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


def fix_morph(morph):
    morph = morph.replace("num=singular","Number=Sing")
    morph = morph.replace("num=plural","Number=Plur")
    morph = morph.replace("gen=masculine","Gender=Masc")
    morph = morph.replace("gen=feminine","Gender=Fem")
    morph = morph.replace("type=preposition","AdpType=Prep")
    morph = morph.replace("tense=present","Tense=Pres")
    morph = morph.replace("mood=subjunctive","Mood=Sub")
    morph = morph.replace("mood=indicative","Mood=Ind")
    morph = morph.replace("person","Person")
    morph = morph.replace("type=indefinite","PronType=Ind")
    morph = morph.replace("|gen=common","")
    morph = morph.replace("type=comma","PunctType=Comm")
    morph = morph.replace("type=relative","PronType=Rel")
    morph = morph.replace("|num=invariable","")
    morph = morph.replace("type=personal","PronType=Prs")
    morph = morph.replace("|type=main","")
    morph = morph.replace("type=demonstrative","PronType=Dem")
    morph = morph.replace("type=period","PunctType=Peri")
    morph = morph.replace("|type=common","")
    morph = morph.replace("tense=future","Tense=Fut")
    morph = morph.replace("|tense=conditional","")
    morph = morph.replace("type=questionmark","PunctType=Qest")
    morph = morph.replace("punctenclose=close","PunctSide=Fin")
    morph = morph.replace("type=article","PronType=Art")
    morph = morph.replace("tense=present","Tense=Pres")
    morph = morph.replace("|type=qualificative","")
    morph = morph.replace("|type=coordinating","")
    morph = morph.replace("type=Personal","PronType=Prs")
    morph = morph.replace("|type=semiauxiliary","")
    morph = morph.replace("mood=imperative","Mood=Imp")
    morph = morph.replace("|neclass=organization","")
    morph = morph.replace("|type=proper","")
    morph = morph.replace("possessorpers","Person")
    morph = morph.replace("|possessornum=invariable","")
    morph = morph.replace("type=possessive","Poss=Yes")
    morph = morph.replace("|neclass=other","")
    morph = morph.replace("NUMr","NUM")
    morph = morph.replace("mood=participle","Mood=Par")
    morph = morph.replace("mood=infinitive","Mood=Inf")
    morph = morph.replace("|neclass=location","")
    morph = morph.replace("|type=auxiliary","")
    morph = morph.replace("|type=general","")
    morph = morph.replace("type=colon","PunctType=Colo")
    morph = morph.replace("|punctenclose=open","")
    morph = morph.replace("type=quotation","PunctType=Peri")
    morph = morph.replace("|type=subordinating","")
    morph = morph.replace("type=ordinal","NumType=Ord")
    morph = morph.replace("|neclass=Person","")
    morph = morph.replace("mood=gerund","Mood=Ger")
    morph = morph.replace("type=negative","Polarity=Neg")
    morph = morph.replace("type=semicolon","PunctType=Semi")
    morph = morph.replace("tense=imperfect","Tense=Imp")
    morph = morph.replace("type=interrogative","PronType=Int")
    morph = morph.replace("type=etc","PunctType=Comm")
    morph = morph.replace("possessorNumber=Plur","Number[psor]=Plur")
    morph = morph.replace("possessorNumber=Sing","Number[psor]=Sing")
    morph = morph.replace("polite=yes","Polite=Form")
    morph = morph.replace("case=nominative","Case=Nom")
    morph = morph.replace("case=dative","Case=Dat")
    morph = morph.replace("|type=other","")
    morph = morph.replace("INTn","INTJ")
    morph = morph.replace("case=accusative","Case=Acc")
    morph = morph.replace("|type=slash","")
    morph = morph.replace("type=hyphen","PunctType=Dash")
    morph = morph.replace("|type=currency","")
    morph = morph.replace("|type=unit","")
    morph = morph.replace("|type=percentag","")
    morph = morph.replace("type=exclamationmark","PunctType=Excl")
    morph = morph.replace("|type=slash","")
    morph = morph.replace("","")
    morph = morph.replace("","")
    return morph

def fix_msd(morph):
    df = pd.read_excel("tags_freeling.xlsx")
    for index, row in df.iterrows():
        if morph.find(str(row["MSD"])) != -1:
            morph = str(row["TAG"]).upper()+morph[morph.find("|"):]
            morph = fix_morph(morph)
            break
    return morph


def nlp_freeling(command):
    rows_ner = []
    case_rare = ["a","de","p"]
    case_rare_next = ['l','ls','el','els']
    word_id = 1
    os.system(command)
    count_sent = 1
    count_case = 0
    with open('output.txt') as f:
        lines = f.readlines()
        sent_id = 0
        flag_del = 0
        value_case_rare = ""
        flag_add = 0
        flag_verb = 0
        token_id = 1
        for line in lines:
            line = " ".join(line.split())
            if line == "":
                sent_id +=1
                token_id = 1
                continue
            category = line.split(" ")
            text = category[1]
            lemma = category[2]
            pos = category[3]
            morph = category[5]
            morph = fix_msd(morph)
            head = category[9]
            deprel = category[10]
            ent = category[8]
            ent_cat = category[9]
            join_word = []
            join_word_norm = []
            ner = category[6]
            
            if pos[:2] == "NP":
                ner_len = 0
                if ner == "-":
                    ne = "PER"
                else:
                    ne = ner.split("-")[1]
                for n1, n2 in zip(text.split("_"), lemma.split("_")):
                    if ner_len == 0:
                        ner_w = "B-"+str(ne)
                    else:
                        ner_w = "I-"+str(ne)
                    row_ner = {
                      'word_id': word_id,
                      'sent_id': sent_id,
                      'token_id': token_id,
                      'text': n1,
                      'lemma': n2,
                      'pos': pos,
                      'morph': morph,
                      'head': head,
                      'deprel': deprel,
                      'token_ner_type': ner_w,
                      'join': [],
                      'join_norm':[]
                    }
                    rows_ner.append(row_ner)
                    df_ner = pd.DataFrame(rows_ner)
                    word_id += 1
                    token_id += 1
                    ner_len += 1
                flag_del = 0
                flag_verb = 0
                continue
                
            if (text in case_rare and pos == 'SP') or (text == 'p' and pos == "SP"):
                flag_del = 1
                value_case_rare = text
                count_case = token_id
            elif text in case_rare_next and flag_del == 1 and (token_id-count_case)==1:
                if value_case_rare == "de" and text != "l":
                    value_case_rare = 'd'
                if value_case_rare == "a" and text != "el":
                    text = 'l'
                lemma_join = ''.join([value_case_rare,text])
                text_join = ''.join([value_case_rare,text])
                if text_join == "ael":
                    text_join = "al"
                    lemma_join = "al"
                flag_del = 0
                flag_add = 1
            elif pos[0] == 'V' and flag_verb == 0:
                flag_verb = 1
                value_case_rare = text
            elif flag_verb == 1 and int(text.find("-")) == 0:
                lemma_join = ''.join([value_case_rare,text])
                text_join = ''.join([value_case_rare,text])
                flag_verb = 0
                flag_add = 1
            elif flag_verb == 1 and pos[0] != 'V':
                flag_verb = 0
            elif pos[0] == 'V' and flag_verb == 1:
                flag_verb = 1
                value_case_rare = text
            
            if text == "n":
                lemma = "ne"
                join_word.append(word_id+1)
            if text == "-lo":
                lemma = "el"
                
            row_ner = {
              'word_id': word_id,
              'sent_id': sent_id,
              'token_id': token_id,
              'text': text,
              'lemma': lemma,
              'pos': pos,
              'morph': morph,
              'head': head,
              'deprel': deprel,
              'token_ner_type': 'O',
              'join': [],
              'join_norm':[]
            }
            word_id += 1
            token_id += 1
            rows_ner.append(row_ner)
            df_ner = pd.DataFrame(rows_ner)
            
            if flag_add == 1:
                join_word.append(word_id-2)
                join_word.append(word_id-1)
                join_word_norm.append(token_id-2)
                join_word_norm.append(token_id-1)
                row_ner = {
                  'word_id': word_id,
                  'sent_id': sent_id,
                  'token_id': token_id,
                  'text': text_join,
                  'lemma': lemma_join,
                  'pos': pos,
                  'morph': morph,
                  'head': head,
                  'deprel': deprel,
                  'token_ner_type': 'O',
                  'join': join_word,
                  'join_norm':join_word_norm
                }
                word_id += 1
                token_id += 1
                rows_ner.append(row_ner)
                df_ner = pd.DataFrame(rows_ner)
                flag_add = 0
    return df_ner


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


def to_conll(command, lang):
    df_nlp = nlp_freeling(command)
    df_nlp = fix_dataframe(df_nlp)
    df_nlp = fix_parsed(df_nlp, lang)
    #df_nlp.to_excel("df_nlp.xlsx")
    df_nlp = fix_punct(df_nlp)
    nlp_conll = df_to_conll(df_nlp)
    return nlp_conll

def generate_tei(seq,parent):
    seq=deepcopy(seq)
    attrib=deepcopy(parent.attrib)
    parent.clear()
    parent.attrib=attrib
    seg_id=attrib['{http://www.w3.org/XML/1998/namespace}id']
    seg_lang=attrib['{http://www.w3.org/XML/1998/namespace}lang']
    text=''
    command = ''
    for e in seq:
        if isinstance(e,str):
            text+=e
    text = fix_text(text)
    
    with open("text.txt","w") as t:
        t.write(text)
    
    if seg_lang == "es":
        #command = 'analyzer_client devel-trl.s.upf.edu:50022  <text.txt >output.txt'
         command = 'analyze -f /mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/freeling/es.cfg --output conll <text.txt >output.txt'
    elif seg_lang == "ca":
        #command = 'analyzer_client devel-trl.s.upf.edu:50021  <text.txt >output.txt'
        command = 'analyze -f /mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/freeling/ca.cfg --output conll <text.txt >output.txt'
    else:
        #command = 'analyzer_client devel-trl.s.upf.edu:50021  <text.txt >output.txt'
         command = 'analyze -f /mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/freeling/ca.cfg --output conll <text.txt >output.txt'
    seq_idx=0
    str_idx=0
    
    #Casi no debe entrar aquí
    while not isinstance(seq[seq_idx],str):
        parent.append(seq[seq_idx])
        seq_idx+=1
        if seq_idx==len(seq):
            return
    
    for sidx,sentence in enumerate(to_conll(command, seg_lang).strip().split('\n\n')):
        s_id=seg_id+'.'+str(sidx+1)
        s = ET.Element('s',attrib={'xml:id':s_id, 'xml:lang': seg_lang})
        parent.append(s)
        ne_cat='O' 
        parent_s = s
        tokens = sentence.split('\n')
        dependencies=[] 
        
        for tidx,token in enumerate(tokens):
            if token.startswith('#'):
                continue
            token=token.split('\t')
            token_12 = ast.literal_eval(token[12])
            
            
            t_id=s_id+'.'+token[0]
            if token[6]=='0':
                dependencies.append(('ud-syn:'+token[7],'#'+s_id+' #'+t_id)) 
            else:
                dependencies.append(('ud-syn:'+token[7],'#'+s_id+'.'+token[6]+' #'+t_id))
            
            new_str_idx = seq[seq_idx].find(token[1],str_idx)

            if len(token_12) != 2:
                str_idx = new_str_idx+len(token[1])

            if len(token_12) == 1:
                continue
                
            ner = token[10]
            flag_ner = 0
            
            
            
            # Este if es para los named entity (NER)
            if ner.startswith('B-'):
                if ne_cat!='O': 
                    s = parent_s
                name = ET.Element('name')
                name.attrib['type'] = {'B-PER':'PER','B-LOC':'LOC','B-ORG':'ORG','B-MISC':'MISC'}[ner]
                s.append(name)
                s = name
                ne_cat = ner
                flag_ner = 1
            elif ner.startswith('I-') and ne_cat != 'O':      
                flag_ner = 1
            elif ner == ('O') and ne_cat!='O':
                s = parent_s
                ne_cat = ner
                flag_ner = 0
            
            # Este if permite crear los nodos mamá e hijas
            token_14 = ast.literal_eval(token[14])
            if len(token_12) == 2:
                comp = ET.Element('w')
                #t_id_t = t_id.split(".")
                #t_id = '.'.join(t_id_t[:-1])+"."+str(token_14[0])+"-"+str(token_14[1])
                comp.attrib['xml:id'] = t_id
                comp.text=token[1]
                s.append(comp)
                s = comp
                for ridx in token_12:
                    for cidx,tokens_comp in enumerate(tokens):
                        token_comp = tokens_comp.split('\t')
                        if int(ridx) == int(token_comp[13]):
                            w=ET.Element('w')
                            w.attrib['xml:id']=s_id+'.'+token_comp[0]
                            #w.attrib['ana']=''+token_comp[3]
                            w.attrib['msd']="UPosTag="+token_comp[5]
                            w.attrib['norm']=token_comp[1]
                            w.attrib['lemma']=token_comp[2]
                            s.append(w)
                s = parent_s
            elif token[1] in [",","."]: #and flag_ner == 0:
                pc=ET.Element('pc')
                pc.attrib['xml:id']=t_id
                #pc.attrib['ana']=''+token[3]
                pc.attrib['msd']="UPosTag="+token[5]
                pc.text=str(token[1])
                s.append(pc)
            elif flag_ner == 1:
                w=ET.Element('w')
                w.attrib['xml:id']=t_id
                #w.attrib['ana']=''+token[3]
                w.attrib['msd']="UPosTag="+token[5]
                w.attrib['lemma']=token[2]
                w.text=str(token[1])
                s.append(w)
            else:
                w=ET.Element('w')
                w.attrib['xml:id']=t_id
                #w.attrib['ana']=""+token[3]
                w.attrib['msd']="UPosTag="+token[5]
                w.attrib['lemma']=token[2]
                if str(token[1]).startswith("'") == True:
                    w.attrib['join']="right"
                if str(token[15]) == "1":
                    w.attrib['join']="right"
                w.text=token[1]
                s.append(w)
        linkGrp=ET.Element('linkGrp',attrib={'type':'UD-SYN','targFunc':'head argument'})
        parent_s.append(linkGrp)
        for dep in dependencies:
            linkGrp.append(ET.Element('link',attrib={'ana':dep[0],'target':dep[1]}))
    seq_idx+=1
    while seq_idx!=len(seq):
        parent.append(seq[seq_idx])
        seq_idx+=1


def xml_to_ana(file,file_save):
    tree = ET.parse(file)
    root = tree.getroot()
    i=0
    for seg in root.iter('{http://www.tei-c.org/ns/1.0}seg'):
        i+=1
        seg_seq=[]
        if seg.text!=None:
            seg_seq.append(seg.text)
        for i,e in enumerate(seg):
            tail=e.tail
            e.tail=None
            seg_seq.append(e)
            if tail!=None and tail.strip()!='':
                if len(seg_seq)>1:
                    if seg_seq[-2][-1]!=' ' and tail[0]!=' ':
                        tail=' '+tail
                seg_seq.append(tail)
        generate_tei(seg_seq,seg)
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    xmlstr = emptyline_re.sub('\n',xmlstr)
    open(file_save[:-4]+ '.ana.xml','w').write(xmlstr)
    ana_file_fixed(file_save[:-4]+ '.ana.xml')
    return file_save[:-4]+'.ana.xml'
    

def docx_to_xml_fixed(file,file_save,root_parameters, members_id):
    src_dfs = []
    appended_dfs = []
    try:
        document = zipfile.ZipFile(file)
        doc_xml = document.read("word/document.xml")
        rooted = ET.fromstring(doc_xml)
        file_codes = (file.split("/")[-1]).split('.')[0]
        file_code = file_codes.split("-")[-1]
        file_mini_code = file_codes.split("-")[-2]
        file_date =  file_code[-4:] + '-' + file_code[2:4] + '-' + file_code[0:2]
        file_name = 'ParlaMint-ES-CT_' + file_date + '-' + file_mini_code
        file_date = datetime.strptime(file_date, '%Y-%m-%d')
        file_date_short = datetime.strftime(file_date, '%Y-%m-%d')
        file_sesion = int(file_mini_code[0:2]) 
        file_meeting = int(file_mini_code[2:])
        if file_date_short >= '2019-11-01':
          tei_ana = '#covid'
        else:
          tei_ana = '#reference'
        df = p_parser(rooted)
        src_dfs.append(df)
        df = df_build_2(df, file_name, file_date, root_parameters, members_id)
        header = tei_header(df, file_name, file_date_short, file_sesion, file_meeting)
        text = to_xml_2(df, tei_ana)
        TEI = ET.Element('TEI')
        TEI.attrib['ana'] = "#parla.sitting "+tei_ana
        TEI.attrib['xmlns'] = "http://www.tei-c.org/ns/1.0"
        TEI.attrib['xml:lang'] = 'ca'
        TEI.attrib['xml:id'] = file_name
        TEI.append(header)
        TEI.append(text)
        xmlstr = minidom.parseString(ET.tostring(TEI)).toprettyxml(indent="   ")
        open(os.path.join(file_save,file_name +'.xml'),'w').write(xmlstr)
        appended_dfs.append(df)
        return file_name+'.xml'
    except Exception as e:
        print(e)
        print('No se puede procesar el archivo ', file)
        return ''
        

def ana_file_fixed(file):
    mytree = ET.parse(file)
    myroot = mytree.getroot()

    for a, b in (myroot.attrib).items():
      if a == "{http://www.w3.org/XML/1998/namespace}id":
        name = b + ".ana"
        myroot.attrib[a] = name
      if a == "ana":
        ana = b.replace("#parla.agenda ","")
        myroot.attrib[a] = ana
    

    for titles in myroot[0]:
      for a in titles:
        for b in a:
          if b.tag == "{http://www.tei-c.org/ns/1.0}title":
            new_title = b.text
            new_title = new_title.replace(new_title[new_title.find("[")-1:new_title.find("[")+1],".ana [")
            new_title = new_title.replace("[ParlaMint SAMPLE]", "[ParlaMint.ana SAMPLE]")
            b.text = str(new_title)
        
    xmlstr = minidom.parseString(ET.tostring(myroot)).toprettyxml(indent="   ")
    xmlstr = emptyline_re.sub('\n',xmlstr)
    open(file,'w').write(xmlstr)