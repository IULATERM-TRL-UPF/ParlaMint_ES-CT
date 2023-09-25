
import src.conll as conll
import re
import ast
import xml.etree.ElementTree as ET
from xml.dom import minidom
ET.register_namespace('','http://www.tei-c.org/ns/1.0')
from copy import deepcopy
import time

from lxml import etree
from io import BytesIO
from xml.dom import minidom


emptyline_re = re.compile('\n\s+\n')

contador = 1


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

    with open("/mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/generative_files/text.txt","w") as t:
        t.write(text)
    
    if seg_lang == "es":
        command = 'analyzer_client 50016  </mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/generative_files/text.txt >/mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/generative_files/output.txt'
        #command = 'analyze -f /mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/freeling/es.cfg --output conll </mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/generative_files/text.txt >/mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/generative_files/output.txt'
    elif seg_lang == "ca":
        command = 'analyzer_client 50015  </mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/generative_files/text.txt >/mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/generative_files/output.txt'
        #command = 'analyze -f /mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/freeling/ca.cfg --output conll </mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/generative_files/text.txt >/mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/generative_files/output.txt'
    else:
        #command = 'analyze -f /mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/freeling/ca.cfg --output conll </mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/generative_files/text.txt >/mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/generative_files/output.txt'
        command = 'analyzer_client 50015  </mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/generative_files/text.txt >/mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/generative_files/output.txt'

    seq_idx=0
    str_idx=0
    
    #Casi no debe entrar aquí
    while not isinstance(seq[seq_idx],str):
        parent.append(seq[seq_idx])
        seq_idx+=1
        if seq_idx==len(seq):
            return
    
    for sidx,sentence in enumerate(conll.to_conll(command, seg_lang).strip().split('\n\n')):
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
            token[7] = token[7].replace(":","_")
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
            
            t5 = token[5]
            t5 = re.sub(r'\|+', '|', t5)
            t5 = t5.replace("possessor","") if t5.endswith("possessor") else t5
            token[5] = t5[:-1] if t5.endswith('|') else t5
            

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
                if len(token[1]) == 2 and str(token[1]).endswith("'") == True:
                    w.attrib['join']="right"
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
