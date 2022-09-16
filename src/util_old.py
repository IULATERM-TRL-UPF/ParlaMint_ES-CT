import stanza
import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom
ET.register_namespace('','http://www.tei-c.org/ns/1.0')
from copy import deepcopy
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
stanza.download('ca')

tokenizer_ca = AutoTokenizer.from_pretrained("projecte-aina/roberta-base-ca-cased-ner")
model_ca = AutoModelForTokenClassification.from_pretrained("projecte-aina/roberta-base-ca-cased-ner")
tokenizer_es = AutoTokenizer.from_pretrained("mrm8488/bert-spanish-cased-finetuned-ner")
model_es = AutoModelForTokenClassification.from_pretrained("mrm8488/bert-spanish-cased-finetuned-ner")

nlp = None
pro_next_verb = ["se","me","le","lo"]

def load_stanza_nlp(cachedir=None):
    global nlp_es
    global nlp_ca
    global nlp_ner_es
    global nlp_ner_ca
    nlp_ner_es = pipeline('ner', model=model_es, tokenizer=tokenizer_es, grouped_entities=True)
    nlp_ner_ca = pipeline('ner', model=model_ca, tokenizer=tokenizer_ca, grouped_entities=True)
    if cachedir:
        nlp_es = stanza.Pipeline(lang='es', dir=cachedir)
        nlp_cat = stanza.Pipeline(lang='ca', dir=cachedir)
    else:
        nlp_es = stanza.Pipeline(lang='es')
        nlp_cat = stanza.Pipeline(lang='ca')

def process_test(stanza_cachedir=None):
    
    if not nlp:
        load_stanza_nlp(stanza_cachedir)
    
    text= "Nosotros creemos que España hay que reformarla, pero no romperla."
    doc = nlp_es(text)
    rows_nlp = nlp_stanza(doc)
    ner_spanish(text)
    

def nlp_stanza(doc):
    rows_nlp = []
    for sent in doc.sentences:
        for word in sent.words:
            print(word)
            id = word.id
            text = word.text
            lemma = word.lemma
            pos = word.upos
            if word.feats:
                morph = word.feats
            else:
                morph = 0
            row_ner = {
                      'token_id': id,
                      'text': text,
                      'lemma': lemma,
                      'pos': pos,
                      'morph': morph
                      }
            rows_nlp.append(row_ner)
    return rows_nlp
    
    
def ner_spanish(sentence):
    result = nlp_ner_es(sentence)
    print(result)
    for token in result:
        type_ner = token["entity_group"]
        '''
            if token.ent_iob_ != 'O':
              ner = token.ent_iob_ + '-' + token.ent_type_
            else:
              ner = token.ent_iob_ 
        '''