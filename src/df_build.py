import cld3
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")

def df_build(df, file_name, file_date, root_parameters, members_id):
  intervinent_len = 100
  not_notes = ['D3Intervinent', 'D3IntervinentObertura', 'D3Textnormal', 'CSessi', 'CPresidncia', 'Crgan']
  interv_style = ['D3Intervinent', 'D3IntervinentObertura']
  
  df['text'] = df['text'].str.strip()
  df['style'] = df['style'].str.replace("/ ", "", regex=True) #errores en ParlaMint-ES-CT_2019-10-10-3902 y ParlaMint-ES-CT_2020-07-07-5701
  df['style'] = df['style'].str.replace(" ", "", regex=True) #errores en ParlaMint-ES-CT_2019-10-10-3902 y ParlaMint-ES-CT_2020-07-07-5701
  df['len'] = df['text'].str.len()
  df['lang'] = df['lang'].str[:2]
  df['file'] = file_name
  df['date'] = file_date
  df.loc[(df['style'] == 'D3Textnormal') &
        (df['len'] < intervinent_len) & 
        (df['bold'] == 'bold') , "style"] = 'D3Intervinent'

  df.loc[(df['style'].isin(interv_style)) &
        (df['len'] >= intervinent_len) &
        ((df['bold'] == 'bold') | (df['curs'] == 'ECNegreta')) 
        , 'style'] = 'D3Textnormal'

  df.loc[(df['style'].isin(interv_style)) &
          (df['text'].str.startswith('»')) #por errores especificos en algunos docs
          , "style"] = 'D3Textnormal'
  
  df.loc[(df['style'].isin(interv_style)) &
          (df['text'].str.startswith('Nota de rectificació')) #por errores especificos en algunos docs
          , "style"] = 'D3Acotacicva'
        
  df.loc[(df['style'].isin(interv_style)) &
          ((df['bold'] == 'bold') | (df['curs'] == 'ECNegreta'))   &
          (df['text'].str.endswith('.')) #por errores especificos en algunos docs
          , 'style'] = 'D3Textnormal' 

  df.loc[(df['style'] == 'D3Textnormal') &
                  (df['curs'].isin(['Refdenotaalpie', 'ECCursiva', 'nfasis', 'st1'])), 'text'] = df['text'].str.replace("(", "|(", regex=True)
  df.loc[(df['style'] == 'D3Textnormal') &
                  (df['curs'].isin(['Refdenotaalpie', 'ECCursiva', 'nfasis', 'st1'])), 'text'] = df['text'].str.replace(")", ")|", regex=True)

  df['text'] = df["text"].str.split("|", n = -1, expand = False)

  df = df.explode('text')
  df = df.reset_index(drop=True)

  df['text'] = df['text'].str.strip()
  df['len'] = df['text'].str.len()

  df = df.drop(df[(df.len == 0) & (df.curs == 'ECCursiva')].index)

  df.loc[(df['text'].str.startswith('(')) &
          (df['text'].str.endswith(')')), 'style'] = 'D3Acotacicva'

  df.loc[(df['style'].isin(interv_style))
          , "speaker"] = df['text'] #en la utterance, el speaker se encuentra en el texto

  df.loc[(df['style'].isin(interv_style)) &
          (df['text'].str.endswith(')')), 'speaker'] = df['speaker'].astype(str).apply(lambda st: st[st.find("(")+1:st.find(")")] ) #indicamos orador en caso de que se encuentre entre paréntesis

  #df['speaker'] = df['speaker'].str.replace("’", "'", regex=True)
  #df['speaker'] = df['speaker'].str.replace(".", "", regex=True)
  #df['speaker'] = df['speaker'].str.replace("  ", " ", regex=True)

  df['speaker'] = df['speaker'].fillna(method='ffill') #llenamos los speakers nulos con el valor anterior

  
  members_file = df.loc[(df['style'].isin(interv_style)) &
                  (df['text'].str.endswith(')')), ['text','speaker', 'date']]
  members_file['text'] = members_file['text'].str.replace(r"\([^()]*\)", "", regex=True) #guardamos los miembros que aparecen con su descripción para añadirlos a los metadatos para el file
  members_file[['Alta', 'Baja']] = file_date #añadimos la fecha del archivo para que solo se haga la coincidencia dentro de él
  members_file['Legislatura'] = ''
  members_file = members_file.rename(columns={"speaker": "Nombre", "text": "Cargo"})
  members_file['Cargo'] = members_file['Cargo'].str.rstrip()

  #lectura de la tabla de referencia confeccionada previamente 
  members = pd.read_csv(os.path.join(root_parameters, "special_denominations.csv"))
  members['Alta'] =  pd.to_datetime(members['Alta'], infer_datetime_format=True)
  members['Baja'] =  pd.to_datetime(members['Baja'], infer_datetime_format=True)
  members = pd.concat([members,members_file]) #append the members_file table

  members = members.loc[(members['Alta'] <= file_date) &
                          (members['Baja'] >= file_date), ['Cargo', 'Nombre']] #filtramos por la fecha del archivo

  df = pd.merge(df, members, how='left', left_on = 'speaker'
                    , right_on = 'Cargo').drop(['Cargo'], axis=1) #obtenemos el nombre de quienes son marcados por su rol

  df.loc[(df['Nombre'].isnull()), 'Nombre' ] = df['speaker'] #copiamos los nombres de quienes son marcados por su nombre

  df = pd.merge(df, members_id, how='left', left_on = 'Nombre' #buscamos el ID segun nombre
                  , right_on = 'Nombre')

  df.loc[df['speaker'].isin(['La presidenta', 'El president']), 'role'] = 'chair' #forzamos chair/member rol
  df.loc[~df['speaker'].isin(['La presidenta', 'El president']), 'role'] = 'member' #forzamos chair/member rol

  ####
  df.loc[df['style'].isin(interv_style), 'u_flag'] = 0 #u_flag va a indicar si se trata de un orador o texto de un discurso
  df.loc[df['style'] == 'D3Textnormal', 'u_flag'] = 1

  df.loc[(df['style'].isin(interv_style)) &
        ((df['u_flag'].shift(periods=-1) == 1) |
        (df['style'].shift(periods=-1) == 'D3Acotacicva')), "u_id"] = 0 #si es orador y lo que sigue es texto de discurso, identificamos con 0 el inicio

  df.loc[(df['style'] == 'D3Textnormal') & 
        ((df['u_flag'].shift(periods=1) == 0) |
        (df['style'].shift(periods=1) == 'D3Acotacicva')), "u_id"] = 1 #si es texto normal y lo que está antes es un orador, lo identificamos como parte del discurso

  df['u_id'] = df['u_id'].fillna(method='ffill') #llenamos los nulos con el valor anterior

  s = df['u_id'].eq(1) 
  df['utt_id'] = (s&s.ne(s.shift())).cumsum().where(s, 1) #iniciamos un incremental solo cuando u_id es 1, este va a ser nuestro id

  df.loc[~df['style'].isin([interv_style, 'D3Textnormal']), 'utt_id'] = 0 #identificamos con 0 lo que es no es parte de la utterance
  df.loc[df['u_id'].isnull(), 'utt_id'] = 0 #identificamos con 0 lo que es no es parte de la utterance

  df['seg_id'] = df.groupby(['utt_id']).cumcount() #creamos un id de segmento incremental agrupando las utterance por numeros

  df.loc[(df['style'].isin(interv_style)) , "utt_id"] = pd.NA
  df['utt_id'] = df['utt_id'].fillna(method='bfill')

  df.loc[(df['utt_id'] == 0) , "utt_id"] = pd.NA
  df['utt_id'] = df['utt_id'].fillna(method='bfill')

  #df[['text', 'style', 'curs', 'u_flag', 'u_id', 'utt_id', 'seg_id']]

  df['utterance_id'] = df['file'] + '.' + df['utt_id'].astype(str)
  df['segment_id'] = df['file'] + '.' + df['utt_id'].astype(str) + '.' + df['seg_id'].astype(str)

  df.loc[(df['style'].isin(interv_style)) &
        (df['len'] > 0), "tag"] = 'u' 

  df.loc[(df['Nombre'].notna()) &
        (df['style'] == "D3Textnormal") &
        (df['len'] > 0) , "tag"] = 'seg'

  df.loc[(df['tag'] != 'u') &
        (~df['style'].isin(not_notes)) & 
        (df['len'] > 0) , "tag"] = 'note'  

  df.loc[(df['tag'] == 'note') &
          (df['style'].isin(['D2Davantal', 'D2Ordredia', 
                            'D2Davantal-Sessio', 'D2Ordredia-Ttol', 
                            'D3Acotacihorria'])) , "tag_type"] = 'utt' #a nivel de utterance

  df.loc[(df['tag'] == 'note') &
        (df['style'] == 'D3Acotacicva') & 
        (df['curs'].isin(['Refdenotaalpie', 'ECCursiva', 'nfasis', 'st1'])) , "tag_type"] = 'seg' #a nivel de segmento

  df.loc[((df['text'].str.upper().str.startswith('SESSI')) 
          & (~df['style'].isin(not_notes))), "tag"]  = 'div' 
          
  df.loc[(df['style'] == 'D3Acotacicva') & 
                 (df['text'].str.lower().str.contains('aplaudiments') == True), 'tag_name'] = 'kinesic_applause'
  
  df.loc[(df['style'] == 'D3Acotacicva') & 
                 (df['text'].str.lower().str.contains('senyal acústic') == True), 'tag_name'] = 'incident_sound'
    
  df.loc[(df['style'] == 'D3Acotacicva') & 
                 (df['text'].str.lower().str.contains('veus de fons') == True), 'tag_name'] = 'vocal_murmuring'

  df.loc[(df['style'] == 'D3Acotacicva') & 
                 (df['text'].str.lower().str.contains('remor de veus') == True), 'tag_name'] = 'vocal_murmuring'

  df.loc[(df['style'] == 'D3Acotacicva') & 
                 (df['text'].str.lower().str.contains('rialles') == True), 'tag_name'] = 'vocal_laughter'
  
  df.loc[(df['style'] == 'D3Acotacicva') & 
                 (df['text'].str.lower().str.contains('riu') == True), 'tag_name'] = 'vocal_laughter' 
  
  df.loc[(df['style'] == 'D3Acotacicva') & 
                 (df['text'].str.lower().str.contains('quedat enregistrats ') == True), 'tag_name'] = 'gap_inaudible'

  df[['tag_name', 'note_type']] = df['tag_name'].str.split('_', n=1, expand=True)

  df.loc[(df['tag_name'].isna()), 'tag_name'] = df['tag']

  df['lang'] = df['lang'].str[:2]

  df['lang_cld3'] = df['text'].apply(lambda x: cld3.get_language(x)) #aplicamos la función de reconocimiento sobre la columna que contiene el texto
  df['lang_inf'] = df['lang_cld3'].str[0] #como el resultado de la función es una lista, obtenemos el primer elemento, que indica el idioma
  df['lang_inf_pb'] = df['lang_cld3'].str[2] #obtenemos el segundo elemento, que indica la probabilidad de la inferencia
  df = df.drop(columns='lang_cld3') #eliminamos la columna con el resultado de la función, que ya no necesitamos

  df.loc[(df['style'] == 'D3Textnormal') &
                (df['lang'] == '') & 
                (df['lang_inf'].isin(['ca', 'es'])) &
                (df['lang_inf_pb'] == True) &
                (df['len'] > 200) , "lang"] = df['lang_inf']

  lang_check = df.loc[(df['tag'] == 'seg'), ['utterance_id','speaker', 'lang', 'text']].groupby(['utterance_id','speaker', 'lang']).count().unstack()
  lang_check = lang_check.droplevel(axis=1, level=0).reset_index()
  lang_check['max'] = lang_check.iloc[:,2:].idxmax(axis=1) #calcula el máximo a partir de la tercera columna

  lang_check2 = lang_check.groupby('speaker').sum().reset_index()
  lang_check2['max'] = lang_check2.iloc[:,1:].idxmax(axis=1)
  lang_check2.loc[(lang_check2['max'] == ''), "max"] = 'ca' #finalmente, si no hay max, forzaremos el catalán

  df = pd.merge(df, lang_check, how='left', left_on = 'utterance_id'
                  , right_on = 'utterance_id')

  df = pd.merge(df, lang_check2, how='left', left_on = 'speaker_x'
                  , right_on = 'speaker')

  df.loc[(df['lang'] == '') & 
                (df['tag'].isin(['u', 'seg'])), "lang"] = df['max_x'] 

  df.loc[(df['lang'] == '') & 
                (df['tag'].isin(['u', 'seg'])), "lang"] = df['max_y']
  
  df.loc[(df['lang'] == ''), "lang"] = 'ca' #forzamos si quedan vacíos

  df['Id'] = df['Id'].fillna(' ')
  df['lang'] = df['lang'].fillna(' ')
  df['tag_type'] = df['tag_type'].fillna('none')

  df = df[['text','lang','utterance_id', 'segment_id', 'tag', 'len', 'style', 'curs', 'bold' , 'Id', 'role', 'file', 'tag_type', 'Nombre', 'tag_name', 'note_type', 'date']]
  return df
