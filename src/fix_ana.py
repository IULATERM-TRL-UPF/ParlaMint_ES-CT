import datetime
import pandas as pd
import sys
import os
import lxml.etree as ETs
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment
from xml.dom import minidom
ET.register_namespace('','http://www.tei-c.org/ns/1.0')


def fix(file):
    tree = ETs.parse(file)
    subtree = tree.xpath('/TEI')
    print(subtree)
    for next_item in subtree:
        print(next_item)
        for item in next_item.findall('s'):
            Id = item.attrib.get('xml:id')
            print(Id)
    #xmlstr = minidom.parseString(ET.tostring(myroot)).toprettyxml(indent="   ")
    #xmlstr = emptyline_re.sub('\n',xmlstr)
    #open(file,'w').write(xmlstr)


def main():
    fix("ParlaMint-ES-CT_2018-01-17-0101.ana.xml")

if __name__ == '__main__':
    main()
