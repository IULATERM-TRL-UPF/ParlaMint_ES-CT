import xml.etree.ElementTree as ET
import src.fix_xml as fix_xml


def to_xml_2(df, tei_ana):
    df = fix_xml.remove_duplicate(df)
    text = ET.Element("text")
    text.attrib["ana"] = tei_ana
    body = ET.Element("body")
    text.append(body)
    u = ET.Element("u")  # se incorpora acá para evitar errores con documentos mal marcados al comienz
    flag_div = 0
    for i, row in df.iterrows():
        txt = row[0].replace("’", "'").replace("»", "")
        tag = row[4]
        if tag == 'div' and flag_div == 0:
            div = ET.Element("div")
            div.attrib["type"] = "debateSection"
            head = ET.Element("head")
            head.text = txt
            div.append(head)
            body.append(div)
            flag_div = 1
        if tag == "u":
            spk = ET.Element("note")
            spk.attrib["type"] = "speaker"
            spk.text = txt
            div.append(spk)
            u = ET.Element("u")
            u.attrib["xml:id"] = row[2]
            u.attrib["who"] = "#" + row[9]
            u.attrib["ana"] = "#regular"
            u.attrib["xml:lang"] = row[1]
            div.append(u)
        if tag == "seg":
            seg = ET.Element("seg")
            seg.attrib["xml:id"] = row[3]
            seg.attrib["xml:lang"] = row[1]
            seg.text = txt
            u.append(seg)
        if tag == "note" and row[12] != "utt":
            if row[14] == "note":
                note = ET.Element("note")
                note.text = txt
                u.append(note)
            else:
                note = ET.Element(row[14])
                if row[14] == "gap":
                    attrib_name = "reason"
                else:
                    attrib_name = "type"
                note.attrib[attrib_name] = row[15]
                desc = ET.Element("desc")
                desc.text = txt
                note.append(desc)
                u.append(note)
        if tag == "note" and row[12] == "utt":
            if row[14] == "note":
                note = ET.Element("note")
                note.attrib["type"] = "narrative"
                note.text = txt
                div.append(note)
            else:
                note = ET.Element(row[14])
                desc = ET.Element("desc")
                desc.text = txt
                note.append(desc)
                div.append(note)
    return text

