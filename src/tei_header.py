import pandas as pd
import xml.etree.ElementTree as ET

def tei_header(df, file_name, file_date_short, file_sesion, file_meeting):
  text_list = df.loc[(df['tag'].isin(['u', 'seg'])), 'text'].astype(str).values.flatten().tolist()
  text_string = ''.join(text_list)
  words = len(text_string.split())

  utts = df.loc[(df['tag'] == 'u'), 'tag'].count()

  tags_names= pd.DataFrame(['text', 'body', 'div', 'note', 'pb', 'u' , 'seg', 'kinesic', 'vocal' , 'incident', 'gap','desc', 'time' ], columns = ['tag_name'])
  tags = df[['tag_name', 'text']].groupby(['tag_name']).count().reset_index()
  tags = pd.merge(tags_names, tags, how='left')
  tags.loc[(tags['tag_name'].isin(['text', 'body'])), 'text'] = 1
  tags['text'] = tags['text'].fillna(0)
  tags['text'] = tags['text'].astype(int)

  teiHeader = ET.Element('teiHeader')

  fileDesc = ET.Element('fileDesc')

  titleStmt = ET.Element('titleStmt')
  titles = {'Corpus Parlamentari en català ': 'ca', 'Catalan parliamentary corpus ': 'en'}
  
  for i, e in titles.items():
    title =  ET.Element('title') 
    title.attrib['type'] = "main"
    title.attrib['xml:lang'] = e
    
    title.text = i + file_name.split("_")[0] + ', '+(file_name.split("_")[1])[:10]+' '+ (file_name.split("_")[1])[11:]+ ' [ParlaMint SAMPLE]'
    titleStmt.append(title)

  legislatura = 'XI Legislatura'
  term = 11
  if file_date_short >= '2015-10-26' and file_date_short < '2017-10-27':
    legislatura = 'XI Legislatura'
    term = 11
  elif file_date_short >= '2017-10-27' and file_date_short < '2020-12-21':
    legislatura = 'XII Legislatura'
    term = 12
  elif file_date_short >= '2021-03-12' and file_date_short < '2021-06-03':
    legislatura = 'XIII Legislatura'
    term = 13
  elif file_date_short >= '2021-06-03':
    legislatura = 'XIV Legislatura'
    term = 14
    
  meetings = {'#parla.term': legislatura}
  for i,e in meetings.items():
    meeting = ET.Element('meeting')
    meeting.attrib['ana'] = i + " #PC."+str(term)
    meeting.attrib['n'] = str(term)
    meeting.text = e
    titleStmt.append(meeting)


  resps = {'Nuria Bel': 'Coordinator', 'Iván Antiba Cartazo': 'Data retrieval, first conversion to XML and to ParlaMint TEI', 'Marilina Pisani': 'Final TEI XML corpus encoding', 'Rodolfo Zevallos': 'Computational Linguistics Specialist'}
  for i,e in resps.items():
    respStmt = ET.Element('respStmt')
    
    persName = ET.Element('persName')
    persName.text = i
    respStmt.append(persName)

    resp = ET.Element('resp')
    resp.text = e
    respStmt.append(resp)
    titleStmt.append(respStmt)


  funders = {'Infraestructura de recerca CLARIN': 'ca', 'CLARIN research infrastructure': 'en'}
  funder = ET.Element('funder')
  for i, e in funders.items():
    orgName = ET.Element('orgName')
    orgName.attrib['xml:lang'] = e
    orgName.text = i
    funder.append(orgName)
  titleStmt.append(funder)

  fileDesc.append(titleStmt)

  editionStmt = ET.Element('editionStmt')
  edition = ET.Element('edition')
  edition.text = '2.0'
  editionStmt.append(edition)
  fileDesc.append(editionStmt)

  extent = ET.Element('extent')
  lst = ['speeches', 'speeches', 'words', 'words']
  lst2 = [utts, utts, words, words]
  lst3 = ['ca', 'en', 'ca', 'en']
  lst4 = ['intervencions', 'speeches', 'paraules', 'words']
  df_extent = pd.DataFrame(list(zip(lst, lst2, lst3, lst4)),
                columns =['unit', 'quantity', 'lang', 'text'])
  for i, e in df_extent.iterrows():
    measure = ET.Element('measure')
    measure.attrib['unit'] = e[0]
    measure.attrib['quantity'] = str(e[1])
    measure.attrib['xml:lang'] = e[2]
    measure.text = str(e[1]) + ' ' + e[3]
    extent.append(measure)
  fileDesc.append(extent)

  publicationStmt = ET.Element('publicationStmt')
  publisher =  ET.Element('publisher')
  publishers = {"Infraestructura d'investigació CLARIN": 'ca', 'CLARIN research infrastructure': 'en'}
  for i, e in publishers.items():
    org =  ET.Element('orgName') 
    org.attrib['xml:lang'] = e
    org.text = i
    publisher.append(org)
  ref = ET.Element('ref')
  ref.attrib['target'] = "https://www.clarin.eu/"
  ref.text = 'www.clarin.eu'
  publisher.append(ref)
  publicationStmt.append(publisher)

  idno = ET.Element('idno')
  idno.attrib['type'] = "URI"
  idno.attrib['subtype'] = "handle"
  idno.text = 'http://hdl.handle.net/11356/1388'
  publicationStmt.append(idno)

  availability = ET.Element('availability')
  availability.attrib['status'] = "free"
  licence = ET.Element('licence')
  licence.text = 'http://creativecommons.org/licenses/by/4.0/'
  availability.append(licence)
  avail_p = ET.Element('p')
  avail_p.attrib['xml:lang'] = 'en'
  avail_p.text = 'This work is licensed under the Creative Commons Attribution 4.0 International License'
  availability.append(avail_p)
  publicationStmt.append(availability)

  pubdate = ET.Element('date')
  pubdate.attrib['when'] = '2022'
  pubdate.text  = '2022'
  publicationStmt.append(pubdate)

  fileDesc.append(publicationStmt)

  sourceDesc = ET.Element('sourceDesc')
  bibl = ET.Element('bibl')
  bibl_tles = {'Parlament de Catalunya diaris de sessions de parlamentaries': 'ca', 'Parliament of Catalonia daily sessions': 'en'}
  for i, e in bibl_tles.items():
    bibl_title = ET.Element('title')
    bibl_title.attrib['type'] = 'main' 
    bibl_title.attrib['xml:lang'] = e
    bibl_title.text = i
    bibl.append(bibl_title)
  sourceDesc.append(bibl)
  bibl_idno = ET.Element('idno')
  bibl_idno.attrib['type'] = 'URI'
  bibl_idno.text = 'https://www.parlament.cat/'
  bibl.append(bibl_idno) #
  bibl_date = ET.Element('date')
  bibl_date.attrib['when'] = str(file_date_short)
  bibl_date.text = str(file_date_short)
  bibl.append(bibl_date) #

  fileDesc.append(sourceDesc)

  encodingDesc = ET.Element('encodingDesc')
  projectDesc = ET.Element('projectDesc')
  p = ET.Element('p')
  p.attrib['xml:lang'] = 'en'
  p.text = 'ParlaMint is a project that aims to (1) create a multilingual set of comparable corpora of parliamentary proceedings uniformly encoded according to the Parla-CLARIN recommendations and covering the COVID-19 pandemic from November 2019 as well as the earlier period from 2015 to serve as a reference corpus; (2) process the corpora linguistically to add Universal Dependencies syntactic structures and Named Entity annotation; (3) make the corpora available through concordancers and Parlameter; and (4) build use cases in Political Sciences and Digital Humanities based on the corpus data.'
  projectDesc.append(p)

  encodingDesc.append(projectDesc)

  tagsDecl = ET.Element('tagsDecl')
  namespace = ET.Element('namespace')
  namespace.attrib['name'] = "http://www.tei-c.org/ns/1.0"

  for i, e in tags.iterrows():
    tagUsage = ET.Element('tagUsage')
    tagUsage.attrib['gi'] = e[0]
    tagUsage.attrib['occurs'] = str(e[1])
    namespace.append(tagUsage)
  tagsDecl.append(namespace)
  encodingDesc.append(tagsDecl)

  ###profileDesc
  profileDesc = ET.Element('profileDesc')
  settingDesc = ET.Element('settingDesc')

  setting = ET.Element('setting')
  sett_lst = ['name', 'name', 'name', 'date']
  sett_lst2 = ['type', 'type', 'type', 'when']
  sett_lst3 = ['address', 'city', 'country', str(file_date_short)]
  sett_lst4 = ['Parc de la Ciutadella, s/n 08003', 'Barcelona', 'Spain', '26.10.2015']
  sett_lst5 = ['NaN', 'NaN', 'key', 'NaN']
  sett_lst6 = ['NaN', 'NaN', 'ES', 'NaN']
  df_sett = pd.DataFrame(list(zip(sett_lst, sett_lst2, sett_lst3, sett_lst4, sett_lst5,sett_lst6  )),
                columns =['tag', 'attrib', 'attrib_text', 'text', 'attrib2', 'key'])

  for i,e in df_sett.iterrows():  
    element = ET.Element(e[0])
    element.attrib[e[1]] = e[2]
    element.text = e[3]
    if e[2] == 'country':
      element.attrib[e[4]] = e[5]
    setting.append(element)
  settingDesc.append(setting)
  profileDesc.append(settingDesc)

  teiHeader.append(fileDesc)
  teiHeader.append(encodingDesc)
  teiHeader.append(profileDesc)

  return teiHeader
