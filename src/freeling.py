import os
import pandas as pd
import src.morphology as morphology
import time

def nlp_freeling(command):
    rows_ner = []
    case_rare = ["a","de","p","De"]
    case_rare_next = ['l','ls','el','els']
    word_id = 1
    start_time_all = time.time()
    
    while True:
        ret = os.system(command)
        if ret == 0:
            break
        else:
            print("Error ejecutando el comando, reintentando...")
            time.sleep(5)

    end_time_all = time.time()
    elapsed_time = end_time_all - start_time_all
    #print("time freeling: ",elapsed_time)
    count_case = 0
    with open('/mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/generative_files/output.txt') as f:
        lines = f.readlines()
        sent_id = 0
        flag_del = 0
        value_case_rare = ""
        flag_add = 0
        flag_verb = 0
        token_id = 1
        df = pd.read_excel("/mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/src/tags_freeling.xlsx")
        for line in lines:
            line = " ".join(line.split()) # Uno toda la linea para luego separarlo por espacios
            if line == "":
                sent_id +=1
                token_id = 1
                continue
            category = line.split(" ")
            text = category[1]
            lemma = category[2]
            pos = category[3]
            morph = category[5]
            morph = morphology.fix_msd(morph,df)
            ner = category[6]
            head = category[9]
            deprel = category[10]
            #ent = category[8]
            join_word = []
            join_word_norm = []
            if str(lemma) == "Fz":
                continue

            #print("Palabra: ",text)
            if text in [",",".",";",":"]:
                flag_verb = 0
                  
            if pos[:2] == "NP":
                ner_len = 0
                if ner == "-":
                    ne = "PER"
                else:
                    ne = ner.split("-")[1]
                text = text.replace("de_el","del")
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
                      'lemma': n1.lower(),
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
                if value_case_rare == "De" and text != "l":
                    value_case_rare = 'D'
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