import glob
import spacy_conll
import pandas as pd

import sys
import spacy
import re

import xml.etree.ElementTree as ET
from xml.dom import minidom
ET.register_namespace('','http://www.tei-c.org/ns/1.0')
from copy import deepcopy

emptyline_re = re.compile('\n\s+\n')
nlp_ca = spacy.load("ca_core_news_trf")
nlp_es = spacy.load("es_core_news_sm")
nlp_ca.add_pipe("conll_formatter")
nlp_es.add_pipe("conll_formatter")

def fix_text(text):
    text = text.replace("’","'")
    return text
  
def process_test(): 
    lang = "cat"
    text= "Volem un estat perquè creiem en l’estat del benestar i beneficiar-lo’n"
    
    text = fix_text(text)
    doc = nlp_ca(text)
    df_nlp = nlp_spacy(doc)
    print(df_nlp)
    df_to_conll_new(df_nlp)


def nlp_spacy(doc):
    rows_ner = []
    case_rare = ["a","d","p"]
    case_rare_next = ['l','ls','el','els']
    for sentid, sentence in enumerate(doc.sents):
        sent_id = sentid
        flag_del = 0
        value_case_rare = ""
        flag_add = 0
        flag_verb = 0
        for tokid, token in enumerate(sentence):
            id = token.i
            text = token.text 
            lemma = token.lemma_
            pos = token.pos_
            morph = token.morph
            head = token.head
            deprel = token.dep_
            ent = token.ent_type_
            ent_cat = token.ent_iob_
            join = '_'
            if token.ent_iob_ != 'O':
                ner = token.ent_iob_ + '-' + token.ent_type_
            else:
                ner = token.ent_iob_
            print('token', text)
            print(text.find("-"))
            print('flag_verb', flag_verb)
            if (text in case_rare and pos == 'DET') or (text == 'p' and pos == "ADP"):
                flag_del = 1
                value_case_rare = text
            elif text in case_rare_next and flag_del == 1:
                lemma_join = ''.join([value_case_rare,text])
                text_join = ''.join([value_case_rare,text])
                flag_del = 0
                flag_add = 1
            elif pos == 'VERB' and flag_verb == 0:
                print('verb')
                flag_verb = 1
                value_case_rare = text
            elif flag_verb == 1 and int(text.find("-")) == 0:
                print('compuesto')
                lemma_join = ''.join([value_case_rare,text])
                text_join = ''.join([value_case_rare,text])
                flag_verb = 0
                flag_add = 1
            elif flag_verb == 1:
                print('flag_verb a 0')
                flag_verb = 0
            
            if int(text.find("'")) == 0:
                if text == "'n":
                    lemma = "ne"
                    join = "yes"
            if text == "-lo":
                lemma = "el"
            
            if len(lemma.split(" ")) > 1:
                lemma = lemma.split(" ")[0]
            
            row_ner = {
              'sent_id': sent_id,
              'token_id': id,
              'text': text,
              'lemma': lemma,
              'pos': pos,
              'morph': morph,
              'head': head,
              'deprel': deprel,
              'token_ner_type' : ner,
              'join': join
            }
            rows_ner.append(row_ner)
            df_ner = pd.DataFrame(rows_ner)
            
            if flag_add == 1:
                row_ner = {
                  'sent_id': sent_id,
                  'token_id': id,
                  'text': text_join,
                  'lemma': lemma_join,
                  'pos': pos,
                  'morph': morph,
                  'head': head,
                  'deprel': deprel,
                  'token_ner_type' : ner,
                  'join': 'yes'
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


def df_to_conll_new(df_ner):
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
        if str(row["morph"]) == "()":
            morph = "_"
        else:
            morph = row["morph"]
        row_conll = str(row["token_id"])+"\t"+str(row["text"])+"\t"+str(row["lemma"])+"\t"+str(row["pos"])+"\t"+str(row["pos"])+"\t"+str(morph)+"\t"+ str(heads)+"\t"+str(row["deprel"])+"\t"+str("_")+"\t"+str(misc)+"\t"+str(row["token_ner_type"])+"\t"+str(row["misc_"])+"\n"
        conll_list.append(flag_add+row_conll)
    doc_final = ''.join([str(x) for x in conll_list])
    return doc_final


def to_conll(doc):
    df_nlp = nlp_spacy(doc)
    nlp_conll = df_to_conll_new(df_nlp)
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
        print(e)
        if isinstance(e,str):
            text+=e
    print("lang: ", seg_lang)
    text = fix_text(text)
    if seg_lang == "es":
        print("Procensando en es")
        doc = nlp_es(text)
    elif seg_lang == "ca":
        print("Procensando en ca")
        doc = nlp_ca(text)
    
    seq_idx=0
    str_idx=0
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
        cont_cat = '_' #nuevo
        parent_s = s
        tokens = sentence.split('\n') #we separate the tokens from the sentences
        dependencies=[] #a list to save the dependecies
        for tidx,token in enumerate(tokens):
            print(token)
            if token.startswith('#'):
                continue
            token=token.split('\t') #we separate the token's attributes 
            t_id=s_id+'.'+token[0] 
            if token[6]=='0': #we check if the token is root
                dependencies.append(('ud-syn:'+token[7],'#'+s_id+' #'+t_id)) #if the token is root, the target is the sentence id
            else:
                dependencies.append(('ud-syn:'+token[7],'#'+s_id+'.'+token[6]+' #'+t_id)) #if the token is not root, the target is composed with the dependency number
            new_str_idx = seq[seq_idx].find(token[1],str_idx)
            while new_str_idx == -1:
                seq_idx+=1
                #print("error: ", seq[seq_idx])
                while not isinstance(seq[seq_idx],str):
                    if tidx+1 == len(tokens):
                        parent.append(seq[seq_idx])
                    else:
                        s.append(seq[seq_idx])
                    seq_idx+=1
                    if seq_idx==len(seq):
                        return
                str_idx=0
                new_str_idx = seq[seq_idx].find(token[1],str_idx)
            str_idx = new_str_idx+len(token[1])
            ner = token[10] 
            if ner.startswith('B-'): #if it's the beginning of an entity
                if ne_cat!='O': 
                    s = parent_s
                name = ET.Element('name') #we create an XML element
                name.attrib['type'] = {'B-PER':'PER','B-LOC':'LOC','B-ORG':'ORG','B-MISC':'MISC'}[ner] #which attribute will be the value according to the dictionary specified for the ner value  
                s.append(name) #we append the new element to the sentence
                s = name
                ne_cat = ner #variable del anterior para el proximo token
            elif ner=='O' and ne_cat!='O': #ne_cat.startswith('B-')
                s = parent_s
                ne_cat = ner
            #nuevo
            cont = token[11] 
            if cont.startswith('B-'): #if it's the beginning of an entity
                if cont_cat!='_': 
                    s = parent_s
                name2 = ET.Element('w') #we create an XML element
                name2.attrib['xml:id'] = t_id + '-' + str(tidx+2) #which attribute will be the value according to the dictionary specified for the ner value  
                s.append(name2) #we append the new element to the sentence
                s = name2
                cont_cat = cont
            elif cont == '_' and cont_cat!='_':# cont_cat.startswith('B-')
                s = parent_s
                cont_cat = cont
            #fin de lo nuevo
            if token[3]=='PUNCT':
                pc=ET.Element('pc',attrib={'xml:id':t_id})
                pc.attrib['msd']='UPosTag=PUNCT'
                pc.attrib['ana']='mte:'+token[4]
                pc.text=token[1]
                if 'SpaceAfter=No' in token[9]:
                    pc.attrib['join']='right'
                s.append(pc)
            else:
                w=ET.Element('w',attrib={'xml:id':t_id})
                w.attrib['msd']='UPosTag='+token[3]
                if token[5]!='_':
                    w.attrib['msd']+='|'+token[5]
                w.attrib['ana']='mte:'+token[4]
                w.attrib['lemma']=token[2]
                w.text=token[1]
                if 'SpaceAfter=No' in token[9]:
                    w.attrib['join']='right'
                s.append(w)
        linkGrp=ET.Element('linkGrp',attrib={'type':'UD-SYN','targFunc':'head argument'})
        parent_s.append(linkGrp)
        for dep in dependencies:
            linkGrp.append(ET.Element('link',attrib={'ana':dep[0],'target':dep[1]}))
    seq_idx+=1
    while seq_idx!=len(seq):
        parent.append(seq[seq_idx])
        seq_idx+=1

 
def file_creation(file):
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
    open(file[:-4]+'.ana.xml','w').write(xmlstr)