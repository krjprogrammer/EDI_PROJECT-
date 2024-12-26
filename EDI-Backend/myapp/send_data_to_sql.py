import pyodbc
import json
def send_data_to_serever(pivot_df_data):
    connection = pyodbc.connect(
        'DRIVER={SQL Server};SERVER=PROGRAMMER\SQLEXPRESS;DATABASE=EDI834Database;Trusted_Connection=yes;'
    )
    cursor = connection.cursor()
    insert_query = '''
        INSERT INTO EDI_834_Data (
            BGN, DMG, DTP, GS, HD, INS, ISA, N1, N3, N4, NM1, PER, REF, ST, CreatedDate
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        '''
    for item in pivot_df_data:
            try:
                cursor.execute(insert_query, (
                    str(item['BGN']), str(item['DMG']), str(item['DTP']), str(item['GS']), str(item['HD']), str(item['INS']), str(item['ISA']),
                    str(item['N1']), str(item['N3']), str(item['N4']), str(item['NM1']), str(item['PER']), str(item['REF']), str(item['ST'])
                ))
                connection.commit()
            except Exception as e:
                print(e)
    connection.close()


def send_data_in_json_form(pivot_df_data):
    subfield_mappings = {
        "ISA": ["ISA01", "ISA02", "ISA03", "ISA04", "ISA05", "ISA06", "ISA07", "ISA08", "ISA09", "ISA10", "ISA11", "ISA12", "ISA13", "ISA14", "ISA15", "ISA16"],
        "GS": ["GS01", "GS02", "GS03", "GS04", "GS05", "GS06", "GS07", "GS08"],
        "ST": ["ST01", "ST02", "ST03"],
        "BGN": ["BGN01", "BGN02", "BGN03", "BGN04", "BGN05", "BGN06", "BGN07", "BGN08", "BGN09"],
        "REF": ["REF01", "REF02", "REF03", "REF04"],
        "DTP": ["DTP01", "DTP02", "DTP03"],
        "N1": ["N101", "N102", "N103", "N104", "N105", "N106"],
        "N3": ["N301", "N302"],
        "N4": ["N401", "N402", "N403", "N404", "N405", "N406"],
        "NM1": ["NM101", "NM102", "NM103", "NM104", "NM105", "NM106", "NM107", "NM108", "NM109", "NM110", "NM111"],
        "PER": ["PER01", "PER02", "PER03", "PER04", "PER05", "PER06", "PER07", "PER08", "PER09"],
        "DMG": ["DMG01", "DMG02", "DMG03", "DMG04", "DMG05", "DMG06", "DMG07", "DMG08", "DMG09"],
        "HD": ["HD01", "HD02", "HD03", "HD04", "HD05", "HD06", "HD07", "HD08", "HD09", "HD10", "HD11"],
        "INS": ["INS01", "INS02", "INS03", "INS04", "INS05", "INS06-1", "INS06-2", "INS07", "INS08", "INS09", "INS10", "INS11", "INS12", "INS13", "INS14", "INS15", "INS16", "INS17"],
    }

    def parse_segment(segment, keys):
        if not segment:
            return None
        values = segment.split()
        return json.dumps(dict(zip(keys, values)))

    insert_query = '''
        INSERT INTO EDI834Table (
            BGN, DMG, DTP, GS, HD, INS, ISA, N1, N3, N4, NM1, PER, REF, ST
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    connection = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=PROGRAMMER\SQLEXPRESS;DATABASE=EDI834Database;Trusted_Connection=yes;'
        )
    cursor = connection.cursor()

    for item in pivot_df_data:
        try:
            cursor.execute(insert_query, (
                parse_segment(item.get('BGN'), subfield_mappings['BGN']),
                parse_segment(item.get('DMG'), subfield_mappings['DMG']),
                parse_segment(item.get('DTP'), subfield_mappings['DTP']),
                parse_segment(item.get('GS'), subfield_mappings['GS']),
                parse_segment(item.get('HD'), subfield_mappings['HD']),
                parse_segment(item.get('INS'), subfield_mappings['INS']),
                parse_segment(item.get('ISA'), subfield_mappings['ISA']),
                parse_segment(item.get('N1'), subfield_mappings['N1']),
                parse_segment(item.get('N3'), subfield_mappings['N3']),
                parse_segment(item.get('N4'), subfield_mappings['N4']),
                parse_segment(item.get('NM1'), subfield_mappings['NM1']),
                parse_segment(item.get('PER'), subfield_mappings['PER']),
                parse_segment(item.get('REF'), subfield_mappings['REF']),
                parse_segment(item.get('ST'), subfield_mappings['ST']),
            ))
            connection.commit()
        except Exception as e:
            print(f"Error: {e}")
    connection.close()

def send_data_to_columns(pivot_df_data):
    subfield_mappings = {
        "ISA": ["ISA01", "ISA03", "ISA05", "ISA06", "ISA07", "ISA08", "ISA09", "ISA10", "ISA11", "ISA12", "ISA13", "ISA14", "ISA15", "ISA16"],
        "GS": ["GS01", "GS02", "GS03", "GS04", "GS05", "GS06", "GS07", "GS08"],
        "ST": ["ST01", "ST02", "ST03"],
        "BGN": ["BGN01", "BGN02", "BGN03", "BGN04", "BGN05", "BGN08"],
        "REF": ["REF01", "REF02"],
        "DTP": ["DTP01", "DTP02", "DTP03"],
        "N1": ["N101", "N102", "N103", "N104"],
        "N3": ["N301", "N302"],
        "N4": ["N401", "N402", "N403", "N404"],
        "NM1": ["NM101", "NM102", "NM103", "NM104", "NM105", "NM108", "NM109"],
        "PER": ["PER01", "PER03", "PER04", "PER05", "PER06", "PER07", "PER08"],
        "DMG": ["DMG01", "DMG02", "DMG03", "DMG04"],
        "HD": ["HD01", "HD03", "HD04", "HD05"],
        "INS": ["INS01", "INS02", "INS03", "INS05", "INS06-2", "INS07", "INS08", "INS09", "INS10", "INS11", "INS12", "INS17"],
    }

    columns_to_keep_blank = [
        "ISA02", "ISA04", "BGN06", "BGN07", "BGN09", "REF03", "REF04",
        "N105", "N106", "INS04", "INS13", "INS14", "INS15", "INS16",
        "INS06-1", "NM106", "NM107", "NM110", "NM111", "PER02", "PER09",
        "N405", "N406", "DMG05", "DMG06", "DMG07", "DMG08", "DMG09",
        "HD02", "HD06", "HD07", "HD08", "HD09", "HD10", "HD11"
    ]

    def parse_segment(segment, keys):
        """Parse segment data and map to respective keys with empty strings for missing values."""
        if not segment:
            return {key: "" for key in keys}
        values = segment.split()
        return {key: values[i] if i < len(values) else "" for i, key in enumerate(keys)}

    connection = pyodbc.connect(
        'DRIVER={SQL Server};SERVER=PROGRAMMER\\SQLEXPRESS;DATABASE=EDI834Database;Trusted_Connection=yes;'
    )
    cursor = connection.cursor()

    all_columns = sum(subfield_mappings.values(), []) + ["Date_edi"]
    column_names = ", ".join([f"[{col}]" if "-" in col else col for col in all_columns])
    placeholders = ", ".join(["?"] * len(all_columns))

    insert_query = f'''
        INSERT INTO edi834detailedtable ({column_names}) 
        VALUES ({placeholders})
    '''

    for item in pivot_df_data:
        try:
            parsed_data = {}
            for segment, keys in subfield_mappings.items():
                data = item.get(segment)
                if segment == "N4":
                    data_list = data.split()
                    if len(data_list[1]) > 2:
                        data_list[0] = f"{data_list[0]}_{data_list[1]}"
                        data_list.pop(1)
                    result = " ".join(data_list)
                    item[segment] = result
                if segment == "NM1":
                    data = item.get(segment)
                    data_list = data.split()
                    if len(data_list) > 4 and data_list[4] == '34':
                        data_list.insert(4, 'NA')
                    if len(data_list) > 6:
                        itemss = data_list[:-2]
                        itemss = itemss[2:]
                        new_string = ''.join(i + '_' for i in itemss)
                        new_list = [data_list[0], data_list[1], new_string, data_list[-2], data_list[-1]]
                        data_list = new_list
                    result = " ".join(data_list)
                    item[segment] = result
                if segment == "INS":
                    data = item.get(segment)
                    data_list = data.split()
                    if len(data_list) > 4 and len(data_list[4]) > 1:
                        data_list.insert(4, 'NA')
                    result = " ".join(data_list)
                    item[segment] = result
                if segment == "N1":
                    data = item.get(segment)
                    data_list = data.split()
                    if len(data_list) > 3:
                        if len(data_list[2]) > 3 and len(data_list[3]) > 3:
                            data_list[1] = f"{data_list[1]}_{data_list[2]}_{data_list[3]}"
                            data_list.pop(3)
                            data_list.pop(2)
                        else:
                            data_list[1] = f"{data_list[1]}_{data_list[2]}"
                            data_list.pop(2)
                    result = " ".join(data_list)
                    item[segment] = result

                parsed_data.update(parse_segment(item.get(segment), keys))
            
            parsed_data["Date_edi"] = item.get("Date_edi", "") 
            
            for blank_column in columns_to_keep_blank:
                parsed_data[blank_column] = ""

            values = [parsed_data.get(col, "") for col in all_columns]
            cursor.execute(insert_query, values)
            cursor.commit()
        except Exception as e:
            print(f"Error: {e}")
    connection.close()
