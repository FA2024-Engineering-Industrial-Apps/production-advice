import sys, os.path as path
sys.path.append(path.abspath(path.join(__file__, path.pardir, path.pardir)))

import os
import re
import time
import csv

import pandas as pd


# Function to generate CSV from given input and save with timestamped filename
def create_csv_from_input(input_data):
    # Split the input data by lines and process each line
    data = []
    for line in input_data.strip().split('\n'):
        # Split each line by the first comma only, to keep PCBs grouped together after the first item
        group, pcbs = line.split(',', 1)
        data.append([group, pcbs])

    # Generate timestamp for the file name
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    file_path = f'./output/user_selected_pcbs_{timestamp}.csv'

    # Write to CSV file
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL)
        writer.writerows(data)

    return file_path


def _combination_to_csv(json_data: dict, combination_id: int, writer) -> None:
    for group in json_data["groups"]:
        group_id = group["group_id"]
        for pcb in group["PCBs"]:
            # TODO: also write materials
            writer.writerow([combination_id, group_id, pcb])


def json_solution_to_tabular_csv(file_id: int, json_data: dict) -> str:
    path = os.path.abspath(os.path.join(
        __file__,
        os.path.pardir,
        os.path.pardir,
        f"output/{file_id}_tabular.csv"
    ))

    with open(path, "w") as file:
        writer = csv.writer(file, lineterminator="\n")
        if "groups" in json_data:
            _combination_to_csv(json_data, 1, writer)
            return path
        
        for combination in json_data["combinations"]:
            combination_name, groups = next(iter(combination.items()))
            m = re.match(r"combination(\d+)", combination_name)
            assert m
            _combination_to_csv(
                {"groups": groups},
                int(m.group(1)),
                writer
            )
    
    return path


PATH_TO_DEFAULT_VBAP_DATA = os.path.abspath(os.path.join(
    __file__,
    os.path.pardir,
    os.path.pardir,
    "SAP_Data/VBAP.csv"
))
def get_default_vbap_data() -> pd.DataFrame:
    vbap_df = pd.read_csv(PATH_TO_DEFAULT_VBAP_DATA)
    vbap_df["EDATU"] = pd.to_datetime(vbap_df["EDATU"])
    return vbap_df