# !/usr/bin/env python3

__version__="0.2.0"

import argparse, os, json, csv, glob, hashlib
from collections import defaultdict
from datetime import datetime
import pandas as pd

def binder():
    ask = input("Give a name to the output file (Y/n)? ")
    if  ask.lower() == 'y':
        given = input("Enter a name to the output file: ")
        output=f'{given}.csv'
    else:
        output='output.csv'
    csv_files = [file for file in os.listdir() if file.endswith('.csv') and file != output]
    dataframes = [pd.read_csv(file) for file in csv_files]
    combined_df = pd.concat(dataframes, axis=1)
    combined_df.to_csv(output, index=False)
    print(f"CSV files combined (by columns) and saved to '{output}'")

def calculate_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def get_file_info(file_path):
    file_hash = calculate_hash(file_path)
    file_size_kb = os.path.getsize(file_path) / 1024
    date_modified = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
    return file_hash, date_modified, file_size_kb

def get_files_and_hashes(base_directory):
    files_info = []
    total_size_kb = 0
    hash_counts = defaultdict(int)
    for root, _, files in os.walk(base_directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_hash, date_modified, file_size_kb = get_file_info(file_path)
            relative_path = os.path.relpath(file_path, base_directory)
            files_info.append((relative_path, file_hash, date_modified, file_size_kb))
            total_size_kb += file_size_kb
            hash_counts[file_hash] += 1
    total_size_mb = total_size_kb / 1024
    no_of_files = len(files_info)
    no_of_unique_files = len(hash_counts)
    no_of_duplicate_files = no_of_files - no_of_unique_files
    return files_info, total_size_mb, no_of_files, no_of_unique_files, no_of_duplicate_files

def save_file_info_to_csv(data, output_file):
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Source", "Hash", "Date_modified", "Size_KB"])
        writer.writerows(data)

def save_file_report_to_csv(report_file, total_size_mb, no_of_files, no_of_unique_files, no_of_duplicate_files):
    with open(report_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Total_size_MB", "No_of_file", "No_of_duplicate_file", "No_of_unique_file"])
        writer.writerow([total_size_mb, no_of_files, no_of_duplicate_files, no_of_unique_files])

def matcher():
    result = []
    ask = input("Enter another name instead of output (Y/n)? ")
    if  ask.lower() == 'y':
        given = input("Give a name to the output file: ")
        output=f'{given}.csv'
    else:
        output='output.csv'
    print("Processing...")
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.csv') and file != output:
                file_path = os.path.join(root, file)
                try:
                    df = pd.read_csv(file_path)
                except Exception as e:
                    print(f"Could not read {file_path}: {e}")
                    continue
                df.dropna(inplace=True)
                df['Source_file'] = file
                result.append(df)
    if result:
        combined_df = pd.concat(result)
        cols_to_check = combined_df.columns.difference(['Source_file'])
        duplicates = combined_df.duplicated(subset=cols_to_check, keep=False)
        repeated_df = combined_df[duplicates]
        repeated_df.to_csv(output, index=False)
    else:
        print("No CSV files found or no data to process.")
    print(f"Resutls saved to '{output}'")

def uniquer():
    result = []
    ask = input("Enter another name instead of output (Y/n)? ")
    if  ask.lower() == 'y':
        given = input("Give a name to the output file: ")
        output=f'{given}.csv'
    else:
        output='output.csv'
    print("Processing...")
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.csv') and file != output:
                file_path = os.path.join(root, file)
                try:
                    df = pd.read_csv(file_path)
                except Exception as e:
                    print(f"Could not read {file_path}: {e}")
                    continue
                df.dropna(inplace=True)
                df['Source_file'] = file
                result.append(df)
    if result:
        combined_df = pd.concat(result)
        cols_to_check = combined_df.columns.difference(['Source_file'])
        duplicates = combined_df.duplicated(subset=cols_to_check, keep=False)
        unique_df = combined_df[~duplicates]
        unique_df.to_csv(output, index=False)
    else:
        print("No CSV files found or no data to process.")
    print(f"Resutls saved to '{output}'")

def xmatch():
    result = []
    ask = input("Enter another name instead of output (Y/n)? ")
    if  ask.lower() == 'y':
        given = input("Give a name to the output file: ")
        output=f'{given}.xlsx'
    else:
        output='output.xlsx'
    print("Processing...")
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(('.xls', '.xlsx')) and file != output:
                file_path = os.path.join(root, file)
                try:
                    xls = pd.ExcelFile(file_path)
                except Exception as e:
                    print(f"Could not read {file_path}: {e}")
                    continue
                for sheet_name in xls.sheet_names:
                    try:
                        df = pd.read_excel(file_path, sheet_name=sheet_name)
                    except Exception as e:
                        print(f"Could not read sheet {sheet_name} in {file_path}: {e}")
                        continue
                    df.dropna(inplace=True)
                    df['Source_file'] = file
                    df['Sheet_name'] = sheet_name
                    result.append(df)
    if result:
        combined_df = pd.concat(result)
        cols_to_check = combined_df.columns.difference(['Source_file', 'Sheet_name'])
        duplicates = combined_df.duplicated(subset=cols_to_check, keep=False)
        repeated_df = combined_df[duplicates]
        repeated_df.to_excel(output, index=False)
    else:
        print("No Excel files found or no data to process.")
    print(f"Resutls saved to '{output}'")

def uniquex():
    result = []
    ask = input("Enter another name instead of output (Y/n)? ")
    if  ask.lower() == 'y':
        given = input("Give a name to the output file: ")
        output=f'{given}.xlsx'
    else:
        output='output.xlsx'
    print("Processing...")
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(('.xls', '.xlsx')) and file != output:
                file_path = os.path.join(root, file)
                try:
                    xls = pd.ExcelFile(file_path)
                except Exception as e:
                    print(f"Could not read {file_path}: {e}")
                    continue
                for sheet_name in xls.sheet_names:
                    try:
                        df = pd.read_excel(file_path, sheet_name=sheet_name)
                    except Exception as e:
                        print(f"Could not read sheet {sheet_name} in {file_path}: {e}")
                        continue
                    df.dropna(inplace=True)
                    df['Source_file'] = file
                    df['Sheet_name'] = sheet_name
                    result.append(df)
    if result:
        combined_df = pd.concat(result)
        cols_to_check = combined_df.columns.difference(['Source_file', 'Sheet_name'])
        duplicates = combined_df.duplicated(subset=cols_to_check, keep=False)
        unique_df = combined_df[~duplicates]
        unique_df.to_excel(output, index=False)
    else:
        print("No Excel files found or no data to process.")
    print(f"Resutls saved to '{output}'")

def filter():
    keyword = input("Please provide a search keyword to perform this mass filter: ")
    output_file = input("Please give a name to the output file: ")
    if output_file != "":
        output = f'{output_file}.csv'
    else:
        output = 'output.csv'
    output_df = pd.DataFrame(columns=['Source_file', 'Column_y', 'Row_x'])
    ask = input("Scan sub-folder(s) as well (Y/n)? ")
    if  ask.lower() == 'y':
        csv_files = [file for file in glob.glob('**/*.csv', recursive=True) if os.path.basename(file) and file != output]
    else:
        csv_files = [file for file in glob.glob('*.csv') if file != output]
    for file in csv_files:
        df = pd.read_csv(file)
        for row_idx, row in df.iterrows():
            for col_idx, value in row.items():
                if isinstance(value, str) and keyword in value:
                    print(f"Matched record found: {file}, Row: {row_idx + 1}, Column: {df.columns.get_loc(col_idx) + 1}, Value: {value}")
                    new_row = {
                        'Source_file': file,
                        'Column_y': df.columns.get_loc(col_idx) + 1,
                        'Row_x': row_idx + 1
                    }
                    combined_row = {**new_row, **row}
                    output_df = output_df._append(combined_row, ignore_index=True)
    output_df.to_csv(output, index=False)
    print(f"Results of massive filtering saved to '{output}'")

def kilter():
    keyword = input("Please provide a search keyword to perform this mass filter: ")
    output_file = input("Please give a name to the output file: ")
    if output_file != "":
        output = f'{output_file}.xlsx'
    else:
        output = 'output.xlsx'
    output_df = pd.DataFrame(columns=['Source_file', 'Sheet_z', 'Column_y', 'Row_x'])
    ask = input("Scan sub-folder(s) as well (Y/n)? ")
    if  ask.lower() == 'y':
        excel_files = [file for file in glob.glob('**/*.xls*', recursive=True) if os.path.basename(file) and file != output]
    else:
        excel_files = [file for file in glob.glob('**/*.xls*') if file != output]
    for file in excel_files:
        xls = pd.ExcelFile(file)
        for sheet_no, sheet_name in enumerate(xls.sheet_names, start=1):
            df = pd.read_excel(xls, sheet_name=sheet_name)
            for row_idx, row in df.iterrows():
                for col_idx, value in row.items():
                    if isinstance(value, str) and keyword in value:
                        print(f"Matched Record Found: {file}, Sheet: {sheet_no}, Row: {row_idx + 1}, Column: {df.columns.get_loc(col_idx) + 1}, Value: {value}")
                        new_row = {
                            'Source_file': file,
                            'Sheet_z': sheet_no,
                            'Column_y': df.columns.get_loc(col_idx) + 1,
                            'Row_x': row_idx + 1
                        }
                        combined_row = {**new_row, **row}
                        output_df = output_df._append(combined_row, ignore_index=True)
    output_df.to_excel(output, index=False)
    print(f"Results of mass filtering saved to '{output}'")

def convertor():
    json_files = [file for file in os.listdir() if file.endswith('.json')]
    if json_files:
        print("JSON file(s) available. Select which one to convert:")
        for index, file_name in enumerate(json_files, start=1):
            print(f"{index}. {file_name}")
        choice = input(f"Enter your choice (1 to {len(json_files)}): ")
        choice_index=int(choice)-1
        selected_file=json_files[choice_index]
        print(f"File: {selected_file} is selected!")
        ask = input("Enter another file name as output (Y/n)? ")
        if  ask.lower() == 'y':
                given = input("Give a name to the output file: ")
                output=f'{given}.csv'
        else:
                output=f"{selected_file[:len(selected_file)-5]}.csv"
        try:
            with open(selected_file, encoding='utf-8-sig') as json_file:
                jsondata = json.load(json_file)
            data_file = open(output, 'w', newline='', encoding='utf-8-sig')
            csv_writer = csv.writer(data_file)
            count = 0
            for data in jsondata:
                if count == 0:
                    header = data.keys()
                    csv_writer.writerow(header)
                    count += 1
                csv_writer.writerow(data.values())
            data_file.close()
            print(f"Converted file saved to '{output}'")
        except (ValueError, IndexError):
            print("Invalid choice. Please enter a valid number.")
    else:
        print("No JSON files are available in the current directory.")

def reverser():
    csv_files = [file for file in os.listdir() if file.endswith('.csv')]
    if csv_files:
        print("CSV file(s) available. Select which one to convert:")
        for index, file_name in enumerate(csv_files, start=1):
            print(f"{index}. {file_name}")
        choice = input(f"Enter your choice (1 to {len(csv_files)}): ")
        choice_index=int(choice)-1
        selected_file=csv_files[choice_index]
        print(f"File: {selected_file} is selected!")
        ask = input("Enter another file name as output (Y/n)? ")
        if  ask.lower() == 'y':
                given = input("Give a name to the output file: ")
                output=f'{given}.json'
        else:
                output=f"{selected_file[:len(selected_file)-4]}.json"
        try:
            data = []
            with open(selected_file, mode='r', encoding='utf-8') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    data.append(dict(row))
            with open(output, mode='w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
            print(f"Converted file saved to '{output}'")
        except (ValueError, IndexError):
            print("Invalid choice. Please enter a valid number.")
    else:
        print("No CSV files are available in the current directory.")

def detector():
    csv_files = [file for file in os.listdir() if file.endswith('.csv')]
    if csv_files:
        print("CSV file(s) available. Select the 1st csv file:")
        for index, file_name in enumerate(csv_files, start=1):
            print(f"{index}. {file_name}")
        choice = input(f"Enter your choice (1 to {len(csv_files)}): ")
        choice_index=int(choice)-1
        input1=csv_files[choice_index]
        print("CSV file(s) available. Select the 2nd csv file:")
        for index, file_name in enumerate(csv_files, start=1):
            print(f"{index}. {file_name}")
        choice = input(f"Enter your choice (1 to {len(csv_files)}): ")
        choice_index=int(choice)-1
        input2=csv_files[choice_index]
        output = input("Give a name to the output file: ")
        try:
            file1 = pd.read_csv(input1)
            file2 = pd.read_csv(input2)
            columns_to_merge = list(file1.columns)
            merged = pd.merge(file1, file2, on=columns_to_merge, how='left', indicator=True)
            merged['Coexist'] = merged['_merge'].apply(lambda x: 1 if x == 'both' else '')
            merged = merged.drop(columns=['_merge'])
            merged.to_csv(f'{output}.csv', index=False)
            print(f"Results of coexist-record detection saved to '{output}.csv'")
        except (ValueError, IndexError):
            print("Invalid choice. Please enter a valid number.")
    else:
        print("No CSV files are available in the current directory.")

def jointer(output_file):
    output = f'{output_file}.csv'
    csv_files = [f for f in os.listdir() if f.endswith('.csv') and f != output]
    dataframes = []
    if csv_files:
        for file in csv_files:
            file_name = os.path.splitext(file)[0]
            df = pd.read_csv(file)
            df['File'] = file_name
            dataframes.append(df)
        combined_df = pd.concat(dataframes, ignore_index=True)
        combined_df = combined_df[['File'] + [col for col in combined_df.columns if col != 'File']]
        combined_df.to_csv(output, index=False)
        print(f"Combined CSV file saved as '{output}'")
    else:
        print(f"No CSV files are available in the current directory; the output file {output} was dropped.")

def spliter():
    csv_files = [file for file in os.listdir() if file.endswith('.csv')]
    if csv_files:
        print("CSV file(s) available. Select which one to split:")
        for index, file_name in enumerate(csv_files, start=1):
            print(f"{index}. {file_name}")
        choice = input(f"Enter your choice (1 to {len(csv_files)}): ")
        try:
            choice_index=int(choice)-1
            selected_file=csv_files[choice_index]
            print(f"File: {selected_file} is selected!")
            df = pd.read_csv(selected_file)
            reference_field = df.columns[0]
            groups = df.groupby(reference_field)
            for file_id, group in groups:
                group = group.drop(columns=[reference_field]) 
                output_file = f'{file_id}.csv'
                group.to_csv(output_file, index=False)
            print("CSV files have been split and saved successfully.")
        except (ValueError, IndexError):
            print("Invalid choice. Please enter a valid number.")
    else:
        print("No CSV files are available in the current directory.")

def xplit():
    excel_files = [file for file in os.listdir() if file.endswith('.xls') or file.endswith('.xlsx')]
    if excel_files:
        print("Excel file(s) available. Select which one to split:")
        for index, file_name in enumerate(excel_files, start=1):
            print(f"{index}. {file_name}")
        choice = input(f"Enter your choice (1 to {len(excel_files)}): ")
        try:
            choice_index=int(choice)-1
            selected_file=excel_files[choice_index]
            print(f"File: {selected_file} is selected!")
            df = pd.read_excel(selected_file)
            reference_field = df.columns[0]
            groups = df.groupby(reference_field)
            for file_id, group in groups:
                group = group.drop(columns=[reference_field]) 
                output_file = f'{file_id}.xlsx'
                group.to_excel(output_file, index=False)
            print("Excel files have been split and saved successfully.")
        except (ValueError, IndexError):
            print("Invalid choice. Please enter a valid number.")
    else:
        print("No excel files are available in the current directory.")

def joint():
    excel_files = [f for f in os.listdir() if f.endswith('.xls') or f.endswith('.xlsx') and f != output]
    dataframes = []
    if excel_files:
        for file in excel_files:
            file_name = os.path.splitext(file)[0]
            df = pd.read_excel(file)
            df['File'] = file_name
            dataframes.append(df)
        output_file = input("Give a name to the output file: ")
        output = f'{output_file}.xlsx'
        combined_df = pd.concat(dataframes, ignore_index=True)
        combined_df = combined_df[['File'] + [col for col in combined_df.columns if col != 'File']]
        combined_df.to_excel(output, index=False)
        print(f"Combined excel file saved as '{output}'")
    else:
        print(f"No excel files are available in the current directory.")

def __init__():
    parser = argparse.ArgumentParser(description="rjj will execute different functions based on command-line arguments")
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand", help="choose a subcommand:")
    subparsers.add_parser('a', help='run file anlaysis')
    subparsers.add_parser('c', help='convert json to csv')
    subparsers.add_parser('r', help='convert csv to json')
    subparsers.add_parser('m', help='identify matched record(s)')
    subparsers.add_parser('u', help='identify unique record(s)')
    subparsers.add_parser('d', help='detect co-existing record(s)')
    subparsers.add_parser('b', help='bind all csv(s) by column(s)')
    subparsers.add_parser('j', help='joint all csv(s) together')
    subparsers.add_parser('s', help='split csv to piece(s)')
    subparsers.add_parser('f', help='filter data by keyword')
    subparsers.add_parser('k', help='filter data by keyword for excel')
    subparsers.add_parser('h', help='identify matched record(s) for excel')
    subparsers.add_parser('q', help='identify unique record(s) for excel')
    subparsers.add_parser('t', help='joint all excel(s) into one')
    subparsers.add_parser('x', help='split excel to piece(s)')
    args = parser.parse_args()
    if args.subcommand == 'a':
        base_directory = os.getcwd()
        ask = input("Enter another name instead of analysis_statistics (Y/n)? ")
        if  ask.lower() == 'y':
            given = input("Give a name to the statistic file: ")
            output_file=f'{given}.csv'
        else:
            output_file='analysis_statistics.csv'
        files_info, total_size_mb, no_of_files, no_of_unique_files, no_of_duplicate_files = get_files_and_hashes(base_directory)
        save_file_info_to_csv(files_info, output_file)
        print(f"File statistics have been saved to '{output_file}'.")
        ask = input("Enter another name instead of analysis_results (Y/n)? ")
        if  ask.lower() == 'y':
            given = input("Give a name to the result file: ")
            report_file=f'{given}.csv'
        else:
            report_file='analysis_results.csv'
        save_file_report_to_csv(report_file, total_size_mb, no_of_files, no_of_unique_files, no_of_duplicate_files)
        print(f"Results of the File Analysis have been saved to '{report_file}'.")
    if args.subcommand == 'j':
        ask = input("Give a name to the output file (Y/n)? ")
        if  ask.lower() == 'y':
            given = input("Enter a name to the output file: ")
            output=f'{given}.csv'
        else:
            output='output.csv'
        jointer(output)
    elif args.subcommand == 's':
        spliter()
    elif args.subcommand == 'b':
        binder()
    elif args.subcommand == 'f':
        filter()
    elif args.subcommand == 'd':
        detector()
    elif args.subcommand == 'c':
        convertor()
    elif args.subcommand == 'r':
        reverser()
    elif args.subcommand == 'k':
        kilter()
    elif args.subcommand == 'x':
        xplit()
    elif args.subcommand == 't':
        joint()
    elif args.subcommand == 'm':
        matcher()
    elif args.subcommand == 'u':
        uniquer()
    elif args.subcommand == 'h':
        xmatch()
    elif args.subcommand == 'q':
        uniquex()