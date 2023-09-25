import datetime
import pandas as pd
import sys
import os
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment
from xml.dom import minidom


def main():
    FILEPATH = os.path.dirname("/mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/xml_files/")
    raw_dirs = set([d for d in os.listdir(FILEPATH)])
    for a in raw_dirs:
        print("<xi:include xmlns:xi=\"http://www.w3.org/2001/XInclude\" href=\""+a+"\"/>")

if __name__ == '__main__':
    main()
