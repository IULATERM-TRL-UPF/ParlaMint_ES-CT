import xml.etree.ElementTree as ET

def to_xml_2(df, tei_ana):
  
  text = ET.Element('text')
  text.attrib['ana'] = tei_ana
  body = ET.Element('body')
  text.append(body) 
  u = ET.Element('u') #se incorpora acá para evitar errores con documentos mal marcados al comienzo 
  for i, row in df.iterrows():
    tag = row[4]
    if tag == 'div':
      div = ET.Element('div')
      div.attrib['type'] = 'debateSection'
      head = ET.Element('head')
      head.text = row[0]
      div.append(head)
      body.append(div)
    if tag == 'u':
      spk = ET.Element('note')
      spk.attrib['type'] = 'speaker'
      spk.text = row[0]
      div.append(spk)
      u = ET.Element('u')
      u.attrib['xml:id'] = row[2]
      u.attrib['who'] = row[9]
      u.attrib['ana'] = row[10]
      u.attrib['xml:lang'] = row[1]
      div.append(u)
    if tag == 'seg':
      seg = ET.Element('seg')
      seg.attrib['xml:id'] = row[3]
      seg.attrib['xml:lang'] = row[1]
      seg.text = row[0]
      u.append(seg)
    if tag == 'note' and row[12] != 'utt':
      if row[14] == 'note':
        note = ET.Element('note')
        note.text = row[0]
        u.append(note)
      else:
        note = ET.Element(row[14])
        if row[14] == 'gap':
          attrib_name = 'reason'
        else:
          attrib_name = 'type' 
        note.attrib[attrib_name] = row[15]
        desc = ET.Element('desc')
        desc.text = row[0]
        note.append(desc)
        u.append(note)
    if tag == 'note' and row[12] == 'utt':
      if row[14] == 'note':
        note = ET.Element('note')
        note.text = row[0]
        div.append(note)
      else:
        note = ET.Element(row[14])
        desc = ET.Element('desc')
        desc.text = row[0]
        note.append(desc)
        div.append(note)
  
  return text
