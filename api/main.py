import os
import datetime as dt

import argparse
import pandas as pd
from xlrd import XLRDError

from database.db import initialize_database, \
    drop_database, \
    add_field, \
    FieldData, \
    save_field_data


def get_duration_in_seconds(p: dt.time) -> int:
    return p.hour * 3600 + p.minute * 60 + p.second


def parse_excel_workbook(path, field: str, date: dt.datetime, update: bool = False) -> dict:
    if os.path.exists(path):
        try:
            sheet = pd.read_excel(path, header=None, skiprows=1)
        except XLRDError:
            print(path, "is not Excel file")
            return {"status": "Fail", "message": path if type(path) is str else "File" + " is not Excel file"}
    else:
        print(path, "file not exist")
        return {"status": "Fail", "message": path if type(path) is str else "File" + " is not exist"}

    data = []
    for index, value in sheet.iterrows():
        if value[1] != 0 and value[1] != 'x':
            start = dt.datetime.combine(date, value[0])
            duration = get_duration_in_seconds(value[2])
            finish = start + dt.timedelta(seconds=duration)
            i = start
            while i < finish:
                data.append((i, value[1], value[2],))
                i = i + dt.timedelta(seconds=1)
    return save_data_to_database(field, data, path, update)


def save_data_to_database(field: str, data: list, path: str, update: bool = False) -> dict:
    field_id = add_field(field)
    instances = []
    for item in data:
        instances.append(FieldData(start_datetime=item[0], value=item[1], duration=item[2], field_id=field_id))
    return save_field_data(instances, path, update)


def parse_directory(path: str, update: bool = False):
    excel_files = []
    for (current_path, directory_names, file_names) in os.walk(path):
        excel_files.extend(os.path.join(current_path, f) for f in file_names if r".xlsx" in f)
    for file in excel_files:
        field, date = prepare_data(file)
        parse_excel_workbook(path, field, date, update)


def parse_date(date, path: str) -> dt.datetime:
    try:
        date = dt.datetime.strptime(date, "%d.%m.%Y")
    except ValueError:
        date = input(f"Please enter date in format \"DD.MM.YYYY\" for file '{path}':")
        date = parse_date(date, path)
    return date


def prepare_data(path: str) -> (str, str):
    split_path = path.split("/")
    file_name = split_path[-1].split(".xlsx")[0]
    split_file_name = file_name.split(", ")
    if len(split_file_name) == 2:
        if split_file_name[0] == '.':
            field = input(f"Please enter field name for file '{path}':")
        else:
            field = split_file_name[0]
        date = parse_date(split_file_name[1], path)
    elif len(split_file_name) > 2:
        field = input(f"Please enter field name for file '{path}':")
        date = parse_date("", path)
    else:
        field = split_path[-2]
        date = parse_date(file_name, path)
    return field, date


def get_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Parser application for KMG Engineering')
    parser.add_argument('-i', '--init', action='store_true',
                        help='Initialize database')
    parser.add_argument('--drop_database', action='store_true',
                        help='Drop database')
    parser.add_argument('-u', '--update', action='store_true',
                        help='Update data if already exist')
    parser.add_argument('-f', '--file', type=str,
                        help='Path to file')
    parser.add_argument('-d', '--directory', type=str,
                        help='Path to directory')
    return parser.parse_args()


if __name__ == "__main__":
    try:
        args = get_arguments()
        if args.init:
            initialize_database()
            print("Database successfully created")
            exit(0)
        if args.drop_database:
            drop_database()
            print("Database successfully dropped")
            exit(0)
        elif args.file:
            if os.path.exists(args.file):
                field, date = prepare_data(args.file)
                parse_excel_workbook(args.file, field, date, args.update)
            else:
                print(args.file, "file is not exists")
            exit(0)
        elif args.directory:
            if os.path.exists(args.directory):
                parse_directory(args.directory, args.update)
                print("Directory successfully parsed")
            else:
                print(args.directory, 'directory is not exists')
            exit(0)
        else:
            print("No file or directory for parsing")
    except KeyboardInterrupt:
        print("Canceled ...")
        exit(0)
