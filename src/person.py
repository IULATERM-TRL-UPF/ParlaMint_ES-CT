import datetime
import pandas as pd
import sys
import os
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment
from xml.dom import minidom
ET.register_namespace('','http://www.tei-c.org/ns/1.0')


def fix_birth(b):
    year = str(b)
    if year == "-":
        year = ""
    elif len(year.split("-")) > 1:
        year = year.split("-")[0]
    return year
    
def fix_date(b):
    if str(type(b)) == "<class 'float'>":
        date = str(b)
    elif str(b) == "now":
        date = "Now"
    elif str(type(b)) == "<class 'datetime.datetime'>":    
        date = b.strftime('%Y-%m-%d')
    elif str(type(b)) == "<class 'str'>":
        date = b
    else:
        date_time_obj = b.to_pydatetime()
        date = str(date_time_obj)
    if len(date.split(" ")) > 1:
        date = date.split(" ")[0]
    return date

def main():
    df = pd.read_excel("MetadataSpeakersNB25-11.xlsx")
    df_name = df["Person"]
    pe = []
    LP = Element('listPerson')
    LP.attrib['xmlns'] = "http://www.tei-c.org/ns/1.0"
    
    for index, row in df.iterrows():
        PE = SubElement(LP,'person')
        person = " ".join(str(row["Person"]).split())
        if len(person.split(" ")) > 1:
            person = person.split(" ")[0]
        PE.attrib['xml:id'] = person
        PN = SubElement(PE,'persName')
        surname = " ".join(str(row["Surname"]).split())
        for a in surname.split(" "):
            if a == "i":
                NL = SubElement(PN,'nameLink')
                NL.text = a
            else:
                SN = SubElement(PN,'surname')
                SN.text = a
        forename = " ".join(str(row["Forename"]).split())
        for n in forename.split(" "):
            FN = SubElement(PN,'forename')
            FN.text = n
        SX = SubElement(PE,'sex')
        SX.attrib['value'] = row["Sex"]
        if str(fix_birth(row["Birth"])) not in (""," ","nan","Nan"):
            BR = SubElement(PE,'birth')
            BR.attrib['when'] = fix_birth(row["Birth"])
        
        if str(row["refparty"]) not in ("nan"):
            AFF = SubElement(PE,'affiliation')
            AFF.attrib['ref'] = str(row["refparty"])
            AFF.attrib['role'] = "member"
        
        for x in range(3):
            if str(row["PG"+str(x+1)+"ref"]) == "nan":
                continue
            AF = SubElement(PE,'affiliation')
            AF.attrib['role'] = str(row["role"+str(x+1)]) 
            AF.attrib['ref'] = str(row["PG"+str(x+1)+"ref"])
        
        for i in range(5):
            if str(row["refPC"+str(i+1)]) == "nan":
                continue
                
            AF = SubElement(PE,'affiliation')
            AF.attrib['ref'] = str(row["refPC"+str(i+1)])
            
            if str(row["rolePC"+str(i+1)]).lower() == "member":
                AF.attrib['role'] = "member"
            elif str(row["rolePC"+str(i+1)]).lower() == "chair":
                AF.attrib['role'] = "head"
            else:
                AF.attrib['role'] = str(row["rolePC"+str(i+1)]).lower()
            AF.attrib['from'] = fix_date(row["from"+str(i+1)])
            if fix_date(row["to"+str(i+1)]) == "Now":
                AF.attrib['to'] = "2022-11-06"
            else:
                AF.attrib['to'] = fix_date(row["to"+str(i+1)])    
                
                
                
    xmlstr = minidom.parseString(ET.tostring(LP)).toprettyxml(indent="   ")
    with open("ParlaMint-ES-CT-listPerson.xml", "w") as f:
        f.write(xmlstr)

if __name__ == '__main__':
    main()
