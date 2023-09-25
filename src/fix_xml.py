import lxml.etree as ET


def remove_duplicate(df):
    mask = (df['text'] == df['text'].shift()) & (df['utterance_id'] == df['utterance_id'].shift())
    df_mask = df[mask]

    for idy, rowy in df_mask.iterrows():
        for idx, rowy in df.iterrows():
            if idy == idx:
                df = df.drop(idy)
                break
    grouped = df.groupby('utterance_id')
    for name, group in grouped:
        if 'seg' in group['tag'].values:
            current_number = 0
            for index, row in group.iterrows():
                if row['tag'] == 'seg':
                    new_segment_id = row['segment_id'][:row['segment_id'].rfind('.') + 1] + str(current_number)
                    df.at[index, 'segment_id'] = new_segment_id
                    current_number += 1
    filtered_df = df[df['tag'] == 'u']
    last_row_with_u = filtered_df.iloc[-1]
    number = last_row_with_u['utterance_id'].split('.')[-2]
    number = int(number)+1
    grouped = df.groupby('utterance_id')
    for name, group in grouped:
        flag = 0
        id_number = 0
        for index, row in group.iterrows():
            if row['tag'] == 'u' and flag == 0:
                flag = 1
            elif row['tag'] == 'u' and flag == 1:
                ut = row['utterance_id'].split('.')
                ut = "".join(ut[:-2])
                id_number = number
                ut = ut + "." +str(number) + ".0"
                df.at[index, 'utterance_id'] = ut
                ut = row['segment_id'].split('.')
                ut = "".join(ut[:-3])
                ut = ut + "." +str(id_number) + ".0." + str(row['segment_id'].split('.')[-1])
                df.at[index, 'segment_id'] = ut
                number += 1
            if id_number != 0:
                ut = row['utterance_id'].split('.')
                ut = "".join(ut[:-2])
                ut = ut + "." +str(id_number) + ".0"
                df.at[index, 'utterance_id'] = ut
                if row['tag'] == 'seg':
                    ut = row['segment_id'].split('.')
                    ut = "".join(ut[:-3])
                    ut = ut + "." +str(id_number) + ".0." + str(row['segment_id'].split('.')[-1])
                    df.at[index, 'segment_id'] = ut
                elif row['tag'] == 'note':
                    ut = row['segment_id'].split('.')
                    ut = "".join(ut[:-3])
                    ut = ut + "." +str(id_number) + ".0." + str(row['segment_id'].split('.')[-1])
                    df.at[index, 'segment_id'] = ut
    df['lang'] = df['lang'].apply(lambda x: 'es' if x not in ['es', 'ca'] else x)
    return df


def fix_date(file):

    # Cargar XML
    tree = ET.parse(file)
    root = tree.getroot()

    # Registrar namespace
    ns = {'ns': 'http://www.tei-c.org/ns/1.0'}
    ET.register_namespace('ns', ns['ns'])

    # Encontrar elemento <date>
    xpath = 'ns:teiHeader/ns:profileDesc/ns:settingDesc/ns:setting/ns:date'
    fecha = root.xpath(xpath, namespaces=ns)[0]

    fecha_when = fecha.get('when')
    fecha.text = fecha_when

    # Guardar XML modificado
    tree.write(file, encoding="utf-8", xml_declaration=True, pretty_print=True)



def main():
    fix_date("/mnt/d/UPF/proyecto_parlamint/ParlaMint_ES-CT/xml_files/ParlaMint-ES-CT_2021-06-17-0802.xml")


if __name__ == '__main__':
    main()