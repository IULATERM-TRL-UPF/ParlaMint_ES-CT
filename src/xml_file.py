
import os

from src.df_build import df_build
from src.df_build_2 import df_build_2
from src.tei_header import tei_header
from src.to_xml import to_xml
from src.to_xml_2 import to_xml_2
from src.xml_parser import p_parser
import zipfile
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
ET.register_namespace('','http://www.tei-c.org/ns/1.0')



def docx_to_xml(file_path,save_path,root_parameters):
    try:
        with zipfile.ZipFile(file_path) as document:
            doc_xml = document.read("word/document.xml")
            rooted = ET.fromstring(doc_xml)

        file_codes = os.path.splitext(os.path.basename(file_path))[0]
        file_code = file_codes.split("-")[-1]
        file_mini_code = file_codes.split("-")[-2]
        file_date =  file_code[-4:] + '-' + file_code[2:4] + '-' + file_code[0:2]
        file_name = f"ParlaMint-ES-CT_{file_date}-{file_mini_code}"
        file_date = datetime.strptime(file_date, '%Y-%m-%d')
        file_date_short = file_date.strftime('%Y-%m-%d')
        file_sesion = int(file_mini_code[0:2]) 
        file_meeting = int(file_mini_code[2:])
        tei_ana = '#covid' if file_date_short >= '2019-11-01' else '#reference'
        df = p_parser(rooted)
        df = df_build(df, file_name, file_date, root_parameters)
        header = tei_header(df, file_name, file_date_short, file_sesion, file_meeting)
        text = to_xml(df, tei_ana)
        TEI = ET.Element('TEI') 
        TEI.attrib['ana'] = "#parla.sitting "+tei_ana
        TEI.attrib['xmlns'] = "http://www.tei-c.org/ns/1.0"
        TEI.attrib['xml:lang'] = 'ca' #catalán
        TEI.attrib['xml:id'] = file_name
        TEI.append(header)
        TEI.append(text)
        xmlstr = minidom.parseString(ET.tostring(TEI)).toprettyxml(indent="   ")
        with open(os.path.join(save_path, f"{file_name}.xml"), "w") as xml_file:
            xml_file.write(xmlstr)

        return file_name+".xml"
    except Exception as e:
        return False


def docx_to_xml_fixed(file_path, save_path, root_parameters):
    try:
        # Extract docx file
        with zipfile.ZipFile(file_path) as document:
            doc_xml = document.read("word/document.xml")
            rooted = ET.fromstring(doc_xml)

        # Generate file name
        file_codes = os.path.splitext(os.path.basename(file_path))[0]
        file_code = file_codes.split("-")[-1]
        file_mini_code = file_codes.split("-")[-2]
        file_date = file_code[-4:] + '-' + file_code[2:4] + '-' + file_code[0:2]
        file_name = f'ParlaMint-ES-CT_{file_date}-{file_mini_code}'

        # Extract metadata
        file_date = datetime.strptime(file_date, '%Y-%m-%d')
        file_date_short = file_date.strftime('%Y-%m-%d')
        file_sesion = int(file_mini_code[:2])
        file_meeting = int(file_mini_code[2:])
        tei_ana = '#covid' if file_date_short >= '2019-11-01' else '#reference'

        # Convert docx to TEI format
        df = p_parser(rooted)
        df = df_build_2(df, file_name, file_date, root_parameters)
        header = tei_header(df, file_name, file_date_short, file_sesion, file_meeting)
        text = to_xml_2(df, tei_ana)
        TEI = ET.Element('TEI')
        TEI.attrib['ana'] = f"#parla.sitting {tei_ana}"
        TEI.attrib['xmlns'] = "http://www.tei-c.org/ns/1.0"
        TEI.attrib['xml:lang'] = 'ca'
        TEI.attrib['xml:id'] = file_name
        TEI.append(header)
        TEI.append(text)

        # Write TEI file
        xmlstr = minidom.parseString(ET.tostring(TEI)).toprettyxml(indent="   ")
        with open(os.path.join(save_path, f'{file_name}.xml'), 'w') as f:
            f.write(xmlstr)
        return file_name+".xml"
    except Exception as e:
        return False