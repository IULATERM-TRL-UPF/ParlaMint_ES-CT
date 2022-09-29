import pandas as pd

def p_parser(rooted):
  list_p=[]
  list_p2=[]
  list_p3=[]
  list_p4=[]
  list_p5=[]
  for elements in rooted.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'): #cada p es un segmento o párrafo
    try:
      list_r = []
      list_pPr = []
      list_rPr = []
      list_rStyle = []
      r = ''
      rPr = ''
      rStyle = '' 
      pPr = ''
      for p in elements: 
        type_ = ''
        
        for child in p: 
          
          if p.tag == '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r': #r contiene todos los segmentos de texto
            if child.tag == '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t': #t es un segmento de texto
              list_r.append(child.text)
              r = ''.join(list_r)
            if child.tag == '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rPr': #contiene el estilo de r
              for lang in child.findall('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}lang'): #indica el idioma
                list_rPr.append(lang.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val'))
                rPr = list_rPr[0] #obtenemos el primer valor de la lista
              for b in child.findall('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}b'): #indica si es bold
                type_ = 'bold'
              for c in child.findall('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rStyle'): #indica si es cursiva
                list_rStyle.append(c.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val'))
                rStyle = list_rStyle[0] #obtenemos el primer valor de la lista
          
          if p.tag == '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pPr':  #indica el estilo de p
            if child.tag == '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pStyle':
              list_pPr.append(child.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')) 
              pPr = list_pPr[0] #obtenemos el primer valor de la lista

      list_p5.append(rStyle)
      list_p4.append(type_)
      list_p3.append(rPr)    
      list_p2.append(pPr)       
      list_p.append(r)
    except:
      print('Error en' + p)
      continue
  df = pd.DataFrame(list(zip(list_p, list_p2, list_p3, list_p4, list_p5)),
               columns =['text', 'style', 'lang', 'bold', 'curs'])
  return df
