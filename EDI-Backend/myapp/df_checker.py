import pandas as pd
import os

wwdf = pd.read_excel(r"C:/Users/91942/Pictures/EDI-Avinash-main/EDI-Avinash-main/EDI-Backend/media/csv_files/EDI_834_11-11-2024.xlsx")
def convert_date_format(date_str):
  try:
    date_parts = date_str.split('/')
    year, month, day = date_parts
    return f"{month}/{day}/{year}" 
  except ValueError:
    return None 
  
# wwdf['DOB'] = wwdf['DOB'].apply(convert_date_format)
# for value in wwdf['EFF DATE']:
#     print(value,type(value))

# wwdf['DEP DOB'].fillna('',inplace=True)
# wwdf['DEP DOB'] = wwdf['DEP DOB'].apply(convert_date_format)
# wwdf['EFF DATE'] = wwdf['EFF DATE'].apply(convert_date_format)
wwdf.fillna("NA",inplace=True)
for i in wwdf['CUSTODIAL PARENT']:
  if i != "NA":
    print(i)

# output_folder = "media/csv_files/"
# fil  = "rtxon.xlsx"
# path = os.path.join(output_folder,fil)
# wwdf.to_excel(path)