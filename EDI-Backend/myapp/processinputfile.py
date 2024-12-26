import csv
import os
import pyodbc
import smtplib
import pandas as pd
from email.mime.text import MIMEText
import openpyxl
from openpyxl import Workbook
from email.mime.multipart import MIMEMultipart 
from email.mime.application import MIMEApplication
from .send_data_to_sql import send_data_to_serever,send_data_in_json_form,send_data_to_columns
import sqlite3
from datetime import datetime
from email.mime.base import MIMEBase
from email import encoders
from io import BytesIO

# Email Configuration
smtp_config = {
    'host': 'mail.privateemail.com',
    'port': 465,
    'user': 'support@disruptionsim.com',
    'password': 'Onesmarter@2023'
}

csv_headers = [
    "SUB/DEP", "LAST NAME", "FIRST NAME", "SSN","TEMP SSN","SEX", "DOB", "DEP LAST NAME", "DEP FIRST NAME",
    "DEP SSN", "DEP SEX", "DEP DOB","CUSTODIAL PARENT","LOCAL", "PLAN", "CLASS", "EFF DATE", "TERM DATE", "ID",
    "ADDRESS 1", "ADDRESS 2", "CITY", "STATE", "ZIP", "PHONE", "EMAIL", "STATUS", "TYPE","MEMBER ID","DEP ADDRESS","DEP CITY","DEP STATE","DEP ZIP"
]

def send_success_email(email, file_name, output_path):
    
                        
    server = smtplib.SMTP_SSL(smtp_config['host'], smtp_config['port'])
    server.login(smtp_config['user'], smtp_config['password'])

    msg = MIMEMultipart()
    msg['From'] = smtp_config['user']
    msg['To'] = email
    msg['Subject'] = f"Processing Successful: {file_name}"

    body = f"""
    <p>The file <strong>{file_name}</strong> was processed successfully.</p>
    <p>Please find the processed file attached.</p>
    """
    msg.attach(MIMEText(body, 'html'))
    
    if file_name.endswith('.X12'):
                print('x12')
                file_name = file_name.replace('.X12', '.csv')
                print('csv')

    # Attach the processed output file
    with open(output_path, 'rb') as f:
        part = MIMEApplication(f.read(), Name="file_name")
        part['Content-Disposition'] = f'attachment; filename="{file_name}"'
        msg.attach(part)

    server.send_message(msg, from_addr=smtp_config['user'], to_addrs=email)
    server.quit()
    print(f"Success email sent for {file_name} to {email}")

def send_error_email(email, file_name, error_message):
    server = smtplib.SMTP_SSL(smtp_config['host'], smtp_config['port'])
    server.login(smtp_config['user'], smtp_config['password'])

    msg = MIMEMultipart()
    msg['From'] = smtp_config['user']
    msg['To'] = email
    msg['Subject'] = f"Processing Failed: {file_name}"

    body = f"""
    <p>The file <strong>{file_name}</strong> failed to process.</p>
    <p><strong>Reason:</strong> {error_message}</p>
    """
    msg.attach(MIMEText(body, 'html'))

    server.send_message(msg, from_addr=smtp_config['user'], to_addrs=email)
    server.quit()
    print(f"Error email sent for {file_name} to {email}")

def send_error_log_email(email, file_name, error_message, error_logs):
    # Step 1: Convert error_logs to DataFrame
    data = [{"Member ID": key, "Group Number": value} for key, value in error_logs.items()]
    df = pd.DataFrame(data)

    # Step 2: Save DataFrame to an in-memory Excel file
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Error Logs')
    excel_buffer.seek(0)

    # Step 3: Prepare the email content
    server = smtplib.SMTP_SSL(smtp_config['host'], smtp_config['port'])
    server.login(smtp_config['user'], smtp_config['password'])

    msg = MIMEMultipart()
    msg['From'] = smtp_config['user']
    msg['To'] = ", ".join(email)
    msg['Subject'] = f"Group Numbers Not Found: {file_name}"

    # Email body
    body = f"""
    <p><strong>Group numbers not found for the following member ID(s):</strong> {error_message}</p>
    """
    msg.attach(MIMEText(body, 'html'))

    # Step 4: Attach the Excel file
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(excel_buffer.read())
    encoders.encode_base64(part)
    part.add_header(
        'Content-Disposition',
        f'attachment; filename="ErrorLogs_{file_name}.xlsx"'
    )
    msg.attach(part)

    # Step 5: Send the email
    server.send_message(msg, from_addr=smtp_config['user'], to_addrs=email)
    server.quit()
    print(f"Group number log email sent for {file_name} to {email}")

def parse_edi_to_csv(input_file_path, output_directory,system_directory):
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs(system_directory, exist_ok=True)
    output_csv_path = os.path.join(output_directory, os.path.basename(input_file_path))
    system_csv_path = os.path.join(system_directory, os.path.basename(input_file_path))
    file_name = input_file_path.split("/")[-1]  # Extracts 'EDI_834_11-15-2024_3KXST5r.X12'
    date_part = file_name.split("_")[2]
    print("Extracted Date:", date_part)
    date_part = str(date_part[:10])
    with open(input_file_path, 'r') as file:
        edi_data = file.read()
    segments = edi_data.strip().split("~")
    csv_data = []
    current_subscriber = {}
    dependents = []
    error_logs = {}
    segment_list = []
    parsed_data_list = []
    total_parsed_data = []
    cus_data_list = []
    k = 0
    def extract_segment_data(segment, delimiter="*"):
        return segment.split(delimiter)

    for segment in segments:
        each_segments = segment.split("*") 
        segment_name = each_segments[0]  
        parsed_data = {}
        if segment_name in ["ISA", "GS", "ST", "BGN", "DTP", "N1", "INS", "REF", "NM1", 
                            "PER", "N3", "N4", "DMG", "HD", "SE", "GE", "IEA"]:
            parsed_data[segment_name] = "*".join(each_segments[1:])
            parsed_data_list.append(parsed_data)
            if segment_name == "HD":
                total_parsed_data.append({k:parsed_data_list})
                k += 1
                parsed_data_list = []
        else:
            print(f"Skipping unknown segment: {segment_name}")
        
        elements = extract_segment_data(segment)
        segment_id = elements[0]
        if segment_id not in segment_list:
            segment_list.append(segment_id)
        if segment_id == "REF":
            member_id_code = elements[1]
            if(member_id_code == "0F"):
                member_id = elements[2]
        if segment_id == "INS":
            relationship_code = elements[2]
            if relationship_code == '18':
                Sub = "Subscriber"
                Type = '18'
            else:
                dependent_type = elements[2]
                if dependent_type == '01':
                    Sub = "Spouse"
                    Type= dependent_type
                elif dependent_type == '19':
                    Sub = "Child"
                    Type = dependent_type
                else:
                    Sub = "Dependent"
                    Type= dependent_type
            if elements[1] == 'Y':
                status = 'Active'
            elif elements[1] == 'N':
                status = 'Inactive'
            else:
                status = ''

        elif segment_id == "NM1" and elements[1] == "IL":
            if current_subscriber:
                csv_data.append(current_subscriber)
                current_subscriber = {}
            sss = elements[-1] if len(elements) > 8 else ""
            sss = sss.replace("-", "").strip()
            if len(sss) == 9:
                sss = f"{sss[:3]}-{sss[3:5]}-{sss[5:]}"
            elif len(sss) == 8:
                sss = f"{sss[:2]}-{sss[2:4]}-{sss[4:]}"
            else:
                sss = "" 
            person = {
                "LAST NAME": elements[3] if len(elements) > 3 else "",
                "FIRST NAME": elements[4] if len(elements) > 4 else "",
                "SSN": sss,
                "SUB/DEP": Sub,
                "STATUS":status,
                "TYPE":Type,
                "MEMBER ID": member_id
            }
            current_subscriber.update(person)

        elif segment_id == "DMG" and len(elements) > 2:
            dob = elements[2]
            person = dependents[-1] if dependents else current_subscriber
            person["DOB"] = f"{dob[4:6]}/{dob[6:]}/{dob[:4]}" if len(dob) == 8 else ""
            person["SEX"] = elements[3] if len(elements) > 3 else ""
        
        elif "REF*17" in segment:
            data = segment.split("*")
            cus_data = data[-1]
            person["CUSTODIAL PARENT"] = cus_data

        elif segment_id == "N3" and len(elements) > 1:
            address = elements[1]
            person = dependents[-1] if dependents else current_subscriber
            person["ADDRESS 1"] = address

        elif segment_id == "N4" and len(elements) > 3:
            city, state, zip_code = elements[1:4]
            zerocode = zip_code.zfill(5)
            zip_code = str(zip_code).strip()
            if len(zip_code) < 5:
                zip_code = zip_code.zfill(5)
            elif len(zip_code) > 5:
                zip_code = zip_code[:5] 
            person = dependents[-1] if dependents else current_subscriber
            person.update({"CITY": city, "STATE": state, "ZIP": str(zip_code)})
        elif segment_id == "PER" and len(elements) > 3:
            phone = elements[-1]
            person = dependents[-1] if dependents else current_subscriber
            person["PHONE"] = phone

        elif segment_id == "HD" and len(elements) > 2:
            current_subscriber["PLAN"] = elements[1]
            current_subscriber["CLASS"] = elements[3] if len(elements) > 3 else ""

        elif segment_id == "DTP" and len(elements) > 2:
            if elements[1] == "348":
                eff_date = elements[-1]
                current_subscriber["EFF DATE"] = f"{eff_date[4:6]}/{eff_date[6:]}/{eff_date[:4]}" if len(eff_date) == 8 else ""
            elif elements[1] == "349":
                term_date = elements[-1]
                current_subscriber["TERM DATE"] = f"{term_date[:4]}/{term_date[4:6]}/{term_date[6:]}" if len(term_date) == 8 else ""

        elif segment_id == "REF" and len(elements) > 2 and elements[1] == "1L":
            current_subscriber["ID"] = elements[2]
            if elements[2] == "L11958M001":
                current_subscriber["PLAN"] = str("01")
                current_subscriber["CLASS"] = "01"
            
            elif elements[2] == "L11958M002":
                current_subscriber["PLAN"] = str("01")
                current_subscriber["CLASS"] = "02"
                
            elif elements[2] == "L11958MD01":
                current_subscriber["PLAN"] = "01"
                current_subscriber["CLASS"] = "SS"
                
            elif elements[2] == "L11958MR01":
                current_subscriber["PLAN"] = "01"
                current_subscriber["CLASS"] = "R8"
                
            elif elements[2] == "L11958MR02":
                current_subscriber["PLAN"] = "01"
                current_subscriber["CLASS"] = "D9"
                
            elif elements[2] == "L11958MR03":
                current_subscriber["PLAN"] = "01"
                current_subscriber["CLASS"] = "R1"    
                
            elif elements[2] == "L11958MR04":
                current_subscriber["PLAN"] = "01"
                current_subscriber["CLASS"] = "D2"       
                
            elif elements[2] == "L11958MR05":
                current_subscriber["PLAN"] = "01"
                current_subscriber["CLASS"] = "M8"             
                
            elif elements[2] == "L11958MR06":
                current_subscriber["PLAN"] = "01"
                current_subscriber["CLASS"] = "M9"    
                
            elif elements[2] == "L11958MR07":
                current_subscriber["PLAN"] = "01"
                current_subscriber["CLASS"] = "M1"
                
            elif elements[2] == "L11958MR08":
                current_subscriber["PLAN"] = "01"
                current_subscriber["CLASS"] = "M2"   
                
            elif elements[2] == "L11958MR09":
                current_subscriber["PLAN"] = "01"
                current_subscriber["CLASS"] = "D0"     
                
            else:
                current_subscriber["PLAN"] = "01"
                current_subscriber["CLASS"] = "01"

                error_logs[member_id] = elements[2]   
    errorFileName =  os.path.basename(input_file_path)
    # print(errorFileName)
    # if(len(error_logs) >0):
    #     error_message = "Missing group numbers for the given Member IDs"
    #     email = ['krishnarajjadhav2003@gmail.com']
    #     send_error_log_email(email, errorFileName, error_message, error_logs) 

    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    import pandas as pd
    flattened_data = []
    flattened_data = []
    for group in total_parsed_data:
        for group_id, records in group.items():
            for record in records:
                for key, value in record.items():
                    flattened_data.append({'group_id': group_id, 'key': key, 'value': value})

    df = pd.DataFrame(flattened_data)
    df = df.groupby(['group_id', 'key'], as_index=False).agg({'value': 'first'})

    pivot_df = df.pivot(index='group_id', columns='key', values='value').reset_index()
    pivot_df = pivot_df.where(pd.notnull(pivot_df), None)
    pivot_df.drop(columns=['group_id'],inplace=True)
    for column in pivot_df.columns:
        pivot_df[column] = pivot_df[column].str.replace('*', '  ', regex=False)
        pivot_df[column] = pivot_df[column].drop_duplicates().reset_index(drop=True)
    pivot_df = pivot_df.fillna(' ')
    pivot_df['Date_edi'] = date_part
    pivot_df_data = pivot_df.to_dict(orient="records")
    # send_data_to_serever(pivot_df_data)
    # send_data_in_json_form(pivot_df_data)
    send_data_to_columns(pivot_df_data)
    conn.close()
    csv_data.append(current_subscriber)
    csv_data.extend(dependents)
    input_filename = os.path.splitext(os.path.basename(input_file_path))[0]
    output_csv_path = os.path.join(output_directory, f"{input_filename}.csv")
    system_csv_path = os.path.join(system_directory, f"{input_filename}.csv")
    for row in csv_data:
        row['STATUS'] = row['ID']
        row['ID'] = row['TYPE']
        row['TYPE'] = ''
        row['TEMP SSN'] = row['SSN']
    for path in [output_csv_path, system_csv_path]:
        print('jam')
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Sheet1"
        worksheet.append(csv_headers)
        current_subscriber_ssn = None
        subscriber_address = None
        subscriber_city = None
        subscriber_zip = None
        subscriber_state = None
        previous_custodial_parent = None
        for row in csv_data:
            row["PLAN"] = row["PLAN"].zfill(2)
            row["CLASS"] = row["CLASS"].zfill(2)
            for key in row.keys():
                row[key] = str(row[key]) if row[key] is not None else ""

            if row['SUB/DEP'] != 'Subscriber':
                row['DEP FIRST NAME'] = str(row.get('FIRST NAME', "")).ljust(20)
                row['DEP LAST NAME'] = str(row.get('LAST NAME', "")).ljust(20)
                row['DEP DOB'] = str(row.get('DOB', "")).ljust(20)
                row['DEP SSN'] = str(row.get('TEMP SSN', "")).ljust(20)
                row['DEP SEX'] = str(row.get('SEX', "")).ljust(20)

            if row['SEX'] == 'M' and row['SUB/DEP'] == 'Child':
                row['SUB/DEP'] = 'SON'.ljust(20)
            elif row['SEX'] == 'F' and row['SUB/DEP'] == 'Child':
                row['SUB/DEP'] = 'DAUGHTER'.ljust(20)

            if row['SUB/DEP'] == 'Dependent':
                row['SUB/DEP'] = 'OTHER'.ljust(20)

            if row["SUB/DEP"] == "Subscriber":
                current_subscriber_ssn = row["SSN"]
            else:
                row["SSN"] = current_subscriber_ssn
            if row["SUB/DEP"] == "Subscriber":
                if "ADDRESS 1" in row and row["ADDRESS 1"]:
                    subscriber_address = row["ADDRESS 1"]
                subscriber_zip = row["ZIP"]
                subscriber_city = row["CITY"]
                subscriber_state = row["STATE"]
            else:
                if "ADDRESS 1" in row and row["ADDRESS 1"]:
                    if row["ADDRESS 1"] != subscriber_address:
                        row["DEP ADDRESS"] = row["ADDRESS 1"]
                        row["ADDRESS 1"] = subscriber_address
                    
                if row["ZIP"] != subscriber_zip:
                        row["DEP ZIP"] = row["ZIP"]
                        row["ZIP"] = subscriber_zip
                   
                if row["CITY"] != subscriber_city:
                        row["DEP CITY"] = row["CITY"]
                        row["CITY"] = subscriber_city
                    
                if row["STATE"] != subscriber_state:
                        row["DEP STATE"] = row["STATE"]
                        row["STATE"] = subscriber_state                            

            worksheet.append([row.get(header, "") for header in csv_headers])
        

    workbook.save(path)

    cus_df = parse_custodial_data(csv_data)
    # records_df = cus_df
    # records_df['date_edi'] = date_part
    # records = records_df.to_dict(orient="records")
    # print(records_df.columns)
    # conn = sqlite3.connect("db.sqlite3")
    # cursor = conn.cursor()

    # query = f"""
    # INSERT INTO myapp_edi_user_data (
    #     last_name, first_name, ssn, sub_dep, status, type, member_id, phone, address1,
    #     city, state, zip, dob, sex, plan, class_field, eff_date, id_field,temp_ssn,
    #     dep_first_name, dep_last_name, dep_dob, dep_ssn, dep_sex,custodial_parent,custodial_address1,custodial_address2,custodial_zip,custodial_state,custodial_phone,date_edi
    # ) VALUES (
    #     {', '.join(['?' for _ in range(len(records_df.columns))])}
    # )
    # """

    # for record in records:
    #     values = [record[col] for col in records_df.columns]
    #     cursor.execute(query, values)

    # conn.commit()
    # conn.close()
    cus_df.to_csv(output_csv_path)
    print(f"CSV generated successfully at: {output_csv_path} and {system_csv_path}")
    return output_csv_path

def parse_custodial_data(csv_data):
    new_df = pd.DataFrame(csv_data)
    new_df['CUSTODIAL ADDRESS 1'] = ''
    new_df['CUSTODIAL ADDRESS 2'] = ''
    new_df['CUSTODIAL CITY'] = ''
    new_df['CUSTODIAL STATE'] = ''
    new_df['CUSTODIAL ZIP'] = ''
    new_df['CUSTODIAL PHONE'] = ''
    if 'ID' in new_df.columns:
        new_df['ID'] = pd.to_numeric(new_df['ID'], errors='coerce')
        condition = new_df['ID'] == 15
    else:
        new_df['id_field'] = pd.to_numeric(new_df['id_field'], errors='coerce')
        condition = new_df['id_field'] == 15
    new_df.fillna('', inplace=True)

    if 'ADDRESS 1' in new_df.columns:
        new_df.loc[condition, 'CUSTODIAL ADDRESS 1'] = new_df.loc[condition, 'ADDRESS 1']
    elif 'address1' in new_df.columns:
        new_df.loc[condition, 'custodial_address_1'] = new_df.loc[condition,'address1']
    if 'ADDRESS 2' in new_df.columns:
        new_df.loc[condition, 'CUSTODIAL ADDRESS 2'] = new_df.loc[condition, 'ADDRESS 2']
    elif 'address2' in new_df.columns:
        new_df.loc[condition, 'custodial_address_2'] = new_df.loc[condition,'address2']
    if 'CITY' in new_df.columns:
        new_df.loc[condition, 'CUSTODIAL CITY'] = new_df.loc[condition, 'CITY']
    elif 'city' in new_df.columns:
        new_df.loc[condition, 'custodial_city'] = new_df.loc[condition,'city']
    if 'STATE' in new_df.columns:
        new_df.loc[condition, 'CUSTODIAL STATE'] = new_df.loc[condition, 'STATE']
    elif 'state' in new_df.columns:
        new_df.loc[condition, 'custodial_state'] = new_df.loc[condition,'state']
    if 'ZIP' in new_df.columns:
        new_df.loc[condition, 'CUSTODIAL ZIP'] = new_df.loc[condition, 'ZIP']
    elif 'zip' in new_df.columns:
        new_df.loc[condition, 'custodial_zip'] = new_df.loc[condition,'zip']
    if 'PHONE' in new_df.columns:
        new_df.loc[condition, 'CUSTODIAL PHONE'] = new_df.loc[condition, 'PHONE']
    elif 'phone' in new_df.columns:
        new_df.loc[condition, 'custodial_phone'] = new_df.loc[condition,'phone']
    
    sdf = new_df
    sdf_data = sdf.to_dict(orient="records")
    previous_custodial_parent = None
    custodial_parent_column = [row.get("CUSTODIAL PARENT", None) for row in sdf_data]
    shifted_custodial_parent_column = [None] + custodial_parent_column[:-1]

    for row, shifted_value in zip(sdf_data, shifted_custodial_parent_column):
        row["CUSTODIAL PARENT"] = shifted_value

    for row in sdf_data:
        if row["SUB/DEP"] != "Subscriber":
                if not row.get("CUSTODIAL ADDRESS 1") or row.get("DEP ADDRESS"):
                        if row.get("DEP ADDRESS"):
                            print(row.get("DEP ADDRESS"))
                            row["CUSTODIAL ADDRESS 1"] = row["DEP ADDRESS"]
                        elif row.get("ADDRESS 1"):
                            row["CUSTODIAL ADDRESS 1"] = row["ADDRESS 1"]
                if not row.get("CUSTODIAL ZIP") or row.get("DEP ZIP"):
                        if row.get("DEP ZIP"):
                            row["CUSTODIAL ZIP"] = row["DEP ZIP"]
                        elif row.get("ZIP"):
                            row["CUSTODIAL ZIP"] = row["ZIP"]


                if not row.get("CUSTODIAL CITY") or row.get("DEP CITY"): 
                        if row.get("DEP CITY"):
                            row["CUSTODIAL CITY"] = row["DEP CITY"]
                        elif row.get("CITY"):
                            row["CUSTODIAL CITY"] = row["CITY"]


                if not row.get("CUSTODIAL STATE"):
                        if row.get("DEP STATE"):
                            row["CUSTODIAL STATE"] = row["DEP STATE"]
                        elif row.get("STATE"):
                            row["CUSTODIAL STATE"] = row["STATE"]

    sdf = pd.DataFrame(sdf_data)
    desired_order = [
        "SUB/DEP", "LAST NAME", "FIRST NAME", "SSN", "TEMP SSN", "SEX", "DOB",
        "DEP LAST NAME", "DEP FIRST NAME", "DEP SSN", "DEP SEX", "DEP DOB",
        "CUSTODIAL PARENT", "LOCAL", "PLAN", "CLASS", "EFF DATE", "TERM DATE",
        "ID", "ADDRESS 1", "ADDRESS 2", "CITY", "STATE", "ZIP", "PHONE", 
        "EMAIL", "STATUS", "TYPE", "MEMBER ID"
    ]

    existing_columns = sdf.columns.tolist()
    columns_in_order = [col for col in desired_order if col in existing_columns]
    other_columns = [col for col in existing_columns if col not in desired_order]


    final_column_order = columns_in_order + other_columns

    sdf = sdf[final_column_order]
    sdf.drop(columns=['TEMP SSN','DEP ADDRESS','DEP ZIP','DEP STATE','DEP CITY'],inplace=True)
    output_folder = "media/csv_files/"
    fil  = "new_custodial_report_EDI_834_12-24-2024.xlsx"
    path = os.path.join(output_folder,fil)
    return sdf


# print('done')
# output_folder = "media/csv_files/"
# J=output_folder
# archive_folder = "media/archive/"
# os.makedirs(output_folder, exist_ok=True)
# os.makedirs(archive_folder, exist_ok=True)

# input_file_path = r"C:/Users/91942/Downloads/EDI_834_12-24-2024.X12"
# output_file_path= parse_edi_to_csv(input_file_path, output_folder,J)
