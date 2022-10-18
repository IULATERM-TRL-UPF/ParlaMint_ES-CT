
import spacy_conll
import pandas as pd

import sys
import spacy
import re
import ast
import os

import lxml
import zipfile

from datetime import datetime

from df_build import df_build
from df_build_2 import df_build_2
from tei_header import tei_header
from to_xml import to_xml
from to_xml_2 import to_xml_2
from xml_parser import p_parser

#import warnings
#warnings.filterwarnings("ignore")

import xml.etree.ElementTree as ET
from xml.dom import minidom
ET.register_namespace('','http://www.tei-c.org/ns/1.0')
from copy import deepcopy


emptyline_re = re.compile('\n\s+\n')
nlp_ca = spacy.load("ca_core_news_trf")
nlp_es = spacy.load("es_core_news_sm")
nlp_ca.add_pipe("conll_formatter")
nlp_es.add_pipe("conll_formatter")
nlp_ca_lemma = spacy.load("ca_core_news_trf")
nlp_ca_lemma.remove_pipe("lemmatizer")
lemmatizer = nlp_ca_lemma.add_pipe("lemmatizer", config={"mode": "lookup", "overwrite": True})
nlp_ca_lemma.initialize()


def read_members_id(root_excel):
    members_id = pd.read_csv(os.path.join(root_excel, "members_id.csv"))
    members_id = members_id.dropna().copy()
    members_id['Nombre'] = members_id['Nombre'].str.strip()
    members_id['matches'] = members_id['matches'].str.strip()
    members_id = members_id[['Nombre', 'matches', 'Id']]
    return members_id


def read_members(root_excel,file_date):
    members = pd.read_csv(os.path.join(root_excel, "special_denominations.csv"))
    members['Alta'] =  pd.to_datetime(members['Alta'], infer_datetime_format=True)
    members['Baja'] =  pd.to_datetime(members['Baja'], infer_datetime_format=True)
    members = pd.concat([members,members_file])
    members = members.loc[(members['Alta'] <= file_date) &
                          (members['Baja'] >= file_date), ['Cargo', 'Nombre']]
    return members


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
        TEI.attrib['ana'] = "#parla.agenda " + tei_ana
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


def nlp_spacy(doc):
    rows_ner = []
    case_rare = ["a","d","p"]
    case_rare_next = ['l','ls','el','els']
    count_word = 0
    for sentid, sentence in enumerate(doc.sents):
        sent_id = sentid
        flag_del = 0
        value_case_rare = ""
        flag_add = 0
        flag_verb = 0
        for tokid, token in enumerate(sentence):
            id = token.i
            text = token.text
            doc_lemma = nlp_ca_lemma(text)
            lem = [i.lemma_ for i in doc_lemma]
            lemma = lem[0]
            pos = token.pos_
            morph = token.morph
            head = token.head
            deprel = token.dep_
            ent = token.ent_type_
            ent_cat = token.ent_iob_
            join_word = []
            if token.ent_iob_ != 'O':
                ner = token.ent_iob_ + '-' + token.ent_type_
            else:
                ner = token.ent_iob_
                
            if (text in case_rare and pos == 'DET') or (text == 'p' and pos == "ADP"):
                flag_del = 1
                value_case_rare = text
            elif text in case_rare_next and flag_del == 1:
                lemma_join = ''.join([value_case_rare,text])
                text_join = ''.join([value_case_rare,text])
                flag_del = 0
                flag_add = 1
            elif pos == 'VERB' and flag_verb == 0:
                flag_verb = 1
                value_case_rare = text
            elif flag_verb == 1 and int(text.find("-")) == 0:
                lemma_join = ''.join([value_case_rare,text])
                text_join = ''.join([value_case_rare,text])
                flag_verb = 0
                flag_add = 1
            elif flag_verb == 1 and pos != 'VERB':
                flag_verb = 0
            elif pos == 'VERB' and flag_verb == 1:
                flag_verb = 1
                value_case_rare = text
            
            if int(text.find("'")) == 0:
                if text == "'n":
                    lemma = "ne"
                    join_word.append(count_word+1)
            if text == "-lo":
                lemma = "el"
            
            if len(lemma.split(" ")) > 1:
                lemma = lemma.split(" ")[0]
            
            count_word += 1
            row_ner = {
              'word_id': count_word,
              'sent_id': sent_id,
              'token_id': id,
              'text': text,
              'lemma': lemma,
              'pos': pos,
              'morph': morph,
              'head': head,
              'deprel': deprel,
              'token_ner_type' : ner,
              'join': []
            }
            rows_ner.append(row_ner)
            df_ner = pd.DataFrame(rows_ner)
            
            if flag_add == 1:
                count_word += 1
                join_word.append(count_word-2)
                join_word.append(count_word-1)
                row_ner = {
                  'word_id': count_word,
                  'sent_id': sent_id,
                  'token_id': id,
                  'text': text_join,
                  'lemma': lemma_join,
                  'pos': pos,
                  'morph': morph,
                  'head': head,
                  'deprel': deprel,
                  'token_ner_type' : ner,
                  'join': join_word
                }
                rows_ner.append(row_ner)
                df_ner = pd.DataFrame(rows_ner)
                flag_add = 0
    df_ner['token_id'] = df_ner.groupby('sent_id')['token_id'].cumcount()+1
    det1 = ['a','d','p']
    det2 = ['l', 'ls', 'els', 'el']
    pos_def = ["ADP", "DET"]
    df_ner.loc[(df_ner['token_ner_type'] == 'O') &
           (df_ner['pos'].isin(pos_def) == True) &
           (df_ner['text'].isin(det1) == True) &
           (df_ner['text'].shift(periods=-1).isin(det2) == True), 'misc_'] = 'B-Con'
    df_ner.loc[(df_ner['token_ner_type'] == 'O') &
           (df_ner['pos'].isin(pos_def) == True) &
           (df_ner['text'].isin(det2) == True) &
           (df_ner['text'].shift(periods=1).isin(det1) == True), 'misc_'] = 'I-Con'
    df_ner['misc_'].fillna('_', inplace=True)
    return df_ner


def df_to_conll(df_ner):
    conll_list = []
    flag = 0
    for index, row in df_ner.iterrows():
        flag_add = ""
        if flag != int(row["sent_id"]):
            flag += 1
            flag_add = "\n"
        value= str(row["head"])
        df_new=df_ner.query("text == @value")
        heads = df_new.iloc[0]["token_id"]
        if row["text"].find("'") != -1:
            misc = "SpaceAfter=No"
        else:
            misc = "_"
        if str(row["morph"]) == "()" or str(row["morph"]) == "":
            morph = "_"
        else:
            morph = row["morph"]
        row_conll = str(row["token_id"])+"\t"+str(row["text"])+"\t"+str(row["lemma"])+"\t"+str(row["pos"])+"\t"+str(row["pos"])+"\t"+str(morph)+"\t"+ str(heads)+"\t"+str(row["deprel"])+"\t"+str("_")+"\t"+str(misc)+"\t"+str(row["token_ner_type"])+"\t"+str(row["misc_"])+"\t"+str(row["join"])+"\t"+str(row["word_id"])+"\n"
        conll_list.append(flag_add+row_conll)
    doc_final = ''.join([str(x) for x in conll_list])
    return doc_final


def to_conll(doc):
    df_nlp = nlp_spacy(doc)
    #df_nlp.to_excel("table.xlsx")
    df_nlp = fix_dataframe(df_nlp)
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

    for e in seq:
        if isinstance(e,str):
            text+=e
    text = fix_text(text)
    if seg_lang == "es":
        doc = nlp_es(text)
    elif seg_lang == "ca":
        doc = nlp_ca(text)
    else:
        doc = nlp_ca(text)
        
    seq_idx=0
    str_idx=0
    
    #Casi no debe entrar aquí
    while not isinstance(seq[seq_idx],str):
        parent.append(seq[seq_idx])
        seq_idx+=1
        if seq_idx==len(seq):
            return
    
    for sidx,sentence in enumerate(to_conll(doc).strip().split('\n\n')):
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
            elif ner=='O' and ne_cat!='O':
                s = parent_s
                ne_cat = ner
                flag_ner = 1
            
            # Este if permite crear los nodos mamá e hijas
            if len(token_12) == 2:
                comp = ET.Element('w')
                t_id_t = t_id.split(".")
                t_id = '.'.join(t_id_t[:-1])+"."+str(token_12[0])+"-"+str(token_12[1])
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
                            w.attrib['lemma']=token_comp[2]
                            #w.attrib['pos']=token_comp[3]
                            if token_comp[5] == '_' or token_comp[5] == '':
                                w.attrib['msd']='UPosTag='+token_comp[3]
                            else:
                                w.attrib['msd']='UPosTag='+token_comp[3]+"|"+token_comp[5]
                            w.attrib['join']='right'
                            w.text=token_comp[1]
                            s.append(w)
                s = parent_s
            elif token[1] in [",","."]: #and flag_ner == 0:
                pc=ET.Element('pc')
                pc.attrib['xml:id']=t_id
                #pc.attrib['pos']='PUNCT'
                pc.attrib['msd']='UPosTag=NP|PUNCT'
                pc.text=str(token[1])
                s.append(pc)
            elif flag_ner == 1:
                w=ET.Element('w')
                w.attrib['xml:id']=t_id
                w.attrib['lemma']=token[2]
                w.attrib['msd']='UPosTag=PROPN'
                w.text=token[1]
                s.append(w)
            else:
                w=ET.Element('w')
                w.attrib['xml:id']=t_id
                if str(token[1]).startswith("'") == True:
                    w.attrib['join']="left" 
                #w.attrib['pos']=token[3]
                w.attrib['lemma']=token[2]
                if token[5] == '_' or token[5] == '':
                    w.attrib['msd']='UPosTag='+token[3]
                else:
                    w.attrib['msd']='UPosTag='+token[3]+"|"+token[5]
                
                #if token[5]!='_':
                    #w.attrib['msd']+='|'+token[5]
               
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
        src_dfs.append(df) #se preservan los DF originales
        df = df_build_2(df, file_name, file_date, root_parameters, members_id)
        header = tei_header(df, file_name, file_date_short, file_sesion, file_meeting) #se crea el encabezado a partir del DataFrame, la función necesita nombre, fecha, sesión y reunión
        text = to_xml_2(df, tei_ana) #se crea el cuerpo del XML, necesita también como argumento la etiqueta de subcorpus.
        #se crea el elemento TEI y sus atributos:
        TEI = ET.Element('TEI') 
        TEI.attrib['ana'] = "#parla.agenda " + tei_ana
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
    except Exception as e:
        print(e)
        print('No se puede procesar el archivo ', file)
        return ''