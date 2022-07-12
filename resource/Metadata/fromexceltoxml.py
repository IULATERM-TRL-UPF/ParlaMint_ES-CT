# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 01:06:38 2021

@author: ivanantiba
"""

#Pandas Package
import pandas as pd



df = pd.read_csv ('Parlamentaris.csv',encoding='latin-1')
pd.set_option('display.max_columns', 10)

import xml.etree.cElementTree as ET

root = ET.Element("person")
doc = ET.SubElement(root, "persName")

ET.SubElement(doc, "forename").text = df['Forename'][1]
ET.SubElement(doc, "surname").text = df['Surename'][1]

tree = ET.ElementTree(root)
tree.write("filename.xml")