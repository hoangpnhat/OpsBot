import pandas as pd
import os
import shutil
import argparse

def concatenate_promotion_info(row):
    paragraphs = []
    
    # Add product name
    if pd.notna(row['Name']):
        paragraphs.append(f"* Name of promotion program: {row['Name']} ")
    # Add customer group
    if pd.notna(row['VIP']) or pd.notna(row['Birthday']):

        if row['VIP'] is not False :
            paragraphs.append("* ONLY for VIP customers")
        elif row['Birthday'] is not False:
            paragraphs.append("* ONLY for customers with Birthdays this month")
        else:
            paragraphs.append("* For ALL customers")
    # # Add sizes
    if pd.notna(row['Minimum products per invoice']) or pd.notna(row['Minimum invoice '])or pd.notna(row['Minimum deposit']):
        tmp = "* To participate in this promotion program,"
        if int(row['Minimum deposit'])>0:
            paragraphs.append(f"{tmp} the customer's minimum accumulated amount must be reached: {row['Minimum deposit']} VND")
        elif int(row['Minimum products per invoice']) >0:
            paragraphs.append(f"{tmp} the number of products on the order must be met: {row['Minimum products per invoice']} sản phẩm")
        elif int(row['Minimum invoice'])>0:
            paragraphs.append(f"{tmp} a minimum order value must be met {row['Minimum invoice']} VND")
    if pd.notna(row['Content']):
        paragraphs.append(f"* Content: {row['Content']}")
    if pd.notna(row['Regulation']):
        paragraphs.append(f"* Regulation of promotion: {row['Regulation']}")
    if pd.notna(row['Scope']):
        paragraphs.append(f"* Scope: {row['Scope']}")
    if pd.notna(row['Start date'] and row['End date']):
        paragraphs.append(f"* This promtion program start from {row['Start date']} to {row['End date']}")
    if pd.notna(row['Gift']):
        paragraphs.append(f"* {row['Name']} promotion is a discounted products/Gift program  (Please follow the link: {row['Gift']})")
    if pd.notna(row['Voucher']):
        paragraphs.append(f"* {row['Name']} promotion is a discount voucher program (Please follow the link: {row['Voucher']})")
    if pd.notna(row['Template']):
        paragraphs.append(f"* Template {row['Template']}")

    # Concatenate the paragraphs into a single string
    return '\n'.join(paragraphs)


def process_promotion_data(folder_save_path:str,path_file:str, sheet_name:str):
    # Check if the folder exists, if not, create it
    if os.path.exists(folder_save_path):
        shutil.rmtree(folder_save_path)
    os.makedirs(folder_save_path)
    program_paragraphs = {}

    df = pd.read_excel(path_file, sheet_name=sheet_name)

    #Strip column name
    df.columns = df.columns.str.strip()

    #Strip all values in dataframe
    df = df.apply(lambda x: x.strip() if isinstance(x, str) else x)

    # Capitalize all values in the 'Name' column
    df['Name'] = df['Name'].str.upper()

    #Fill NaN 
    df[['Minimum deposit', 'Minimum products per invoice','Minimum invoice']] = df[['Minimum deposit', 'Minimum products per invoice',
                                                                                           'Minimum invoice']].fillna(value=0)
    df[['VIP', 'Birthday']] = df[['VIP', 'Birthday']].fillna(value=False)
    
    # Disable silent downcasting
    pd.set_option('future.no_silent_downcasting', True)
    # Convert boolean columns to boolean
    df[['VIP', 'Birthday']] = df[['VIP', 'Birthday']].replace(1.0,True)


    #Set type of column
    df['Minimum deposit'] = df['Minimum deposit'].astype(int)
    df['Minimum products per invoice'] = df['Minimum products per invoice'].astype(int)
    df['Minimum invoice'] = df['Minimum invoice'].astype(int)

    # Convert columns to datetime
    df['Start date'] = pd.to_datetime(df['Start date'], dayfirst=True)
    df['End date'] = pd.to_datetime(df['End date'], dayfirst=True)

    # Format the dates
    # df['Start date'] = df['Start date'].dt.strftime('%d-%m-%Y')
    # df['End date'] = df['End date'].dt.strftime('%d-%m-%Y')

    #Concatenate product info
    df['paragraph'] = df.apply(concatenate_promotion_info, axis=1)

    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        # Extract "Tên chương trình" and "paragraph"
        program_name = row["Name"]
        paragraph = row["paragraph"]
        
        # Clean the program name to make it a valid filename
        valid_program_name = "".join(char for char in program_name if char.isalnum() or char in (" ", "_")).strip().replace(" ", "_")
        
        # Add the paragraph to the corresponding program name in the dictionary
        if valid_program_name in program_paragraphs:
            program_paragraphs[valid_program_name].append('\n' + paragraph)
        else:
            program_paragraphs[valid_program_name] = [paragraph]

    # Write the paragraphs to their respective files
    for program_name, paragraphs in program_paragraphs.items():
        filename = f"{program_name}.txt"
        save_path = folder_save_path + "/" + filename
        with open(save_path, 'w', encoding='utf-8') as file:
            for paragraph in paragraphs:
                file.write(paragraph + '\n')
    return
def concatenate_voucher_info(row):
    paragraphs = []
    # Add product name
    if pd.notna(row['Code']):
        paragraphs.append(f"* Code's voucher: {row['Code']} ")
    # Add customer group
    if pd.notna(row['Promotion']):
        paragraphs.append(f"* Belong to promotion: {row['Promotion']}")
    if pd.notna(row['Content']):
        paragraphs.append(f"* Content of voucher: {row['Content']}")
    if pd.notna(row['Start date'] and row['End date']):
        paragraphs.append(f"* This voucher available start from {row['Start date']} to {row['End date']}")
    if pd.notna(row['Scope']):
        paragraphs.append(f"* Scope: {row['Scope']}")
    
    return '\n'.join(paragraphs)
def process_voucher_info(folder_save_path:str,path_file:str,sheet_name:str):
    # Check if the folder exists, if not, create it
    if os.path.exists(folder_save_path):
        shutil.rmtree(folder_save_path)
    os.makedirs(folder_save_path)
    voucher_paragraphs = {}

    df = pd.read_excel(path_file, sheet_name=sheet_name)

    #Strip column name
    df.columns = df.columns.str.strip()

    #Strip all values in dataframe
    df = df.apply(lambda x: x.strip() if isinstance(x, str) else x)

    # Convert columns to datetime
    df['Start date'] = pd.to_datetime(df['Start date'])
    df['End date'] = pd.to_datetime(df['End date'])

    # Format the dates
    df['Start date'] = df['Start date'].dt.strftime('%d-%m-%Y')
    df['End date'] = df['End date'].dt.strftime('%d-%m-%Y')

    #Concatenate product info
    df['paragraph'] = df.apply(concatenate_voucher_info, axis=1)

    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
    # Extract "Tên chương trình" and "paragraph"
        program_name = row["Promotion"]
        paragraph = row["paragraph"]
        
        # Clean the program name to make it a valid filename
        valid_program_name = "".join(char for char in program_name if char.isalnum() or char in (" ", "_")).strip().replace(" ", "_")
        
        # Add the paragraph to the corresponding program name in the dictionary
        if valid_program_name in voucher_paragraphs:
            voucher_paragraphs[valid_program_name].append('\n' + paragraph)
        else:
            voucher_paragraphs[valid_program_name] = [paragraph]

    # Write the paragraphs to their respective files
    for program_name, paragraphs in voucher_paragraphs.items():
        filename = f"voucher_{program_name}.txt"
        save_path = folder_save_path + "/" + filename
        with open(save_path, 'w', encoding='utf-8') as file:
            for paragraph in paragraphs:
                file.write(paragraph + '\n')
    return

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--promotion_save_path", type=str, default='data/promtions')
    parser.add_argument("--voucher_save_path", type=str, default='data/vouchers')
    parser.add_argument("--file_path", type=str, default="notebook/template_promotion.xlsx")
    args = parser.parse_args()
    process_promotion_data(args.promotion_save_path,args.file_path,"promotion")
    process_voucher_info(args.voucher_save_path,args.file_path,"voucher")
if __name__ == "__main__":
    main()
