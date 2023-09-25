# -*- coding: utf-8 -*-
import pandas as pd

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
import util


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
















 

