"""
This script is designed to optimize the grouping of Printed Circuit Boards (PCBs) based on their material requirements
and slot widths using a hybrid brute forcing optimization algorithm. It generates optimal valid combinations
while adhering to a maximum slot width constraint (C_max).
"""
import pandas as pd
import time
import psutil
import os
import sys
import json

    
def is_valid_group(group, pcb_data_dict, material_catalogue_dict, C_max):
    '''
    This function checks if a group of PCBs is valid based on their total required slot width.

    :param group: List of PCB identifiers forming a group.
    :param pcb_data_dict: Dictionary with PCB identifiers as keys and lists of required materials as values.
    :param material_catalogue_dict: Dictionary with material identifiers as keys and their respective slot widths as values.
    :param C_max: Maximum allowed slot width for any group.
    :return: True if the group is valid, otherwise False.
    '''


    if len(group) == 1:    # a group consisting of only one PCB is always valid
        return True

    used_material = set()  # set to keep track of materials already counted
    total_capacity = 0

    for pcb in group:      # iterating over each PCB in the group

        for material in pcb_data_dict[pcb]:             # iterating over the materials required by the PCB

            if material not in used_material:            # only add new materials that haven't been counted yet

                used_material.add(material)
                total_capacity += material_catalogue_dict[material]
                if total_capacity > C_max:                # if total capacity exceeds the allowed maximum, the group is invalid

                    return False

    return True                                            # if the total capacity is within the allowed maximum, the group is valid



def generate_combinations(pcbs, pcb_data_dict, material_catalogue_dict, C_max, current_groups=[],min_groups=[float('inf')]):
    '''
    This function generates combinations of PCBs based on their total required slot width.
    It aims to find the minimum number of groups such that the combined slot width of PCBs in each group does not exceed C_max.

    :param pcbs: List of PCB identifiers to be grouped.
    :param pcb_data_dict: Dictionary with PCB identifiers as keys and their respective materials as values.
    :param material_catalogue_dict: Dictionary with material identifiers as keys and their respective slot widths as values.
    :param C_max: Maximum allowed slot width for any group.
    :param current_groups: List of current groups of PCBs being formed. Defaults to an empty list.
    :param min_groups: A list containing a single element which is the minimum number of groups found so far. Defaults to infinity.
    :return: Generator yielding valid combinations of groups.
    '''

    if not pcbs:                                                        # base case: If there are no PCBs left to group, yield the current grouping and return
        yield current_groups
        return

    if len(current_groups) > min_groups[0]:                              # pruning: If the current number of groups exceeds the minimum found so far, stop further exploration
        return

    for i, group in enumerate(current_groups):                          # try to add the first PCB to each of the existing groups and recurse
        new_group = group + [pcbs[0]]
        if is_valid_group(new_group, pcb_data_dict, material_catalogue_dict, C_max):
            new_groups = current_groups[:i] + [new_group] + current_groups[i + 1:]
            yield from generate_combinations(pcbs[1:], pcb_data_dict, material_catalogue_dict, C_max, new_groups,
                                             min_groups)

    if is_valid_group([pcbs[0]], pcb_data_dict, material_catalogue_dict, C_max) and len(current_groups) + 1 <= min_groups[0]:   # try to create a new group with the first PCB and recurse if valid

        for combination in generate_combinations(pcbs[1:], pcb_data_dict, material_catalogue_dict, C_max,
                                                 current_groups + [[pcbs[0]]], min_groups):

            min_groups[0] = min(min_groups[0], len(combination))                                            # update the minimum number of groups found
            yield combination


def create_json_data(best_combinations, pcb_data_dict):
    json_data = {"combinations": []}
    for combination_id, combi in enumerate(best_combinations, start=1):
        grouping = []
        # Loop through each group in best_combinations
        for group_id, group in enumerate(combi, start=1):
            group_pcbs = []
            group_materials = set()  # Use a set to avoid duplicate materials
            # Collect PCBs and their materials from the current group
            for pcb_group in group:
                if pcb_group in pcb_data_dict:
                    group_pcbs.append(pcb_group)
                    group_materials.update(pcb_data_dict[pcb_group])

            # Add the group information to the JSON structure
            grouping.append({
                "group_id": group_id,
                "PCBs": group_pcbs#,
                #"materials": list(group_materials)  # Convert set to list
            })
        json_data["combinations"].append({f"combination{combination_id}": grouping})

    # Return the JSON data as a Python dictionary
    return json_data

def write_results(best_combinations, pcb_list, pcb_data_dict, material_catalogue_dict, C_max, dataset_path,execution_time):
    """
    This function writes the results of PCB combinations to a text file,
    and prints process information including execution time, memory usage, CPU times, and number of threads.

    :param best_combinations: List of best combinations of PCBs.
    :param pcbs: List of PCB identifiers to be grouped.
    :param pcb_data_dict: Dictionary with PCB identifiers as keys and their respective materials as values.
    :param material_catalogue_dict: Dictionary with material identifiers as keys and their respective slot widths as values.
    :param C_max: Maximum allowed slot width for any group.
    :param dataset_path: Path to the dataset where the results will be saved.
    :param execution_time: Execution time of the process.
    """
    shortest_combination = len(best_combinations[0])

    process = psutil.Process(os.getpid())                                # get process information
    memory_usage = process.memory_info().rss                             # in bytes
    cpu_times = process.cpu_times()                                      # CPU times
    num_threads = process.num_threads()                                  # number of threads
    print(f"Execution time: {execution_time} seconds")
    print(f"Memory usage: {memory_usage / (1024 * 1024)} MB")
    print(f"CPU Times: User Time = {cpu_times.user} seconds, System Time = {cpu_times.system} seconds")
    print(f"Number of Threads: {num_threads}")

    filename = f"{dataset_path}BF_results_pcbs_{len(pcb_list):02d}.txt"    # writing the results to a text file
    with open(filename, 'w') as file:
        file.write(f"Number of combined PCBs: {len(pcb_list)} \n")
        file.write(f"Max Feeder Capacity time: {C_max}\n")
        file.write(f"Execution time: {execution_time} seconds\n")
        file.write(f"Memory usage: {memory_usage / (1024 * 1024)} MB\n")    # convert bytes to MB
        file.write(f"CPU Times: User Time = {cpu_times.user} seconds, System Time = {cpu_times.system} seconds\n")
        file.write(f"Number of Threads: {num_threads}\n")
        file.write(f"Number of possible combinations that fulfill capacity constraint: {len(best_combinations)}\n")
        file.write(f"Number of combinations with the least amount of groups: {len(best_combinations)}\n")
        file.write(f"Number of groups necessary: {shortest_combination}\n \n")
        for count, combination in enumerate(best_combinations):
            file.write(f"Combination {count + 1} with {len(combination)} groups contain:\n")
            for group_count, group in enumerate(combination):
                file.write(f"\nGroup {group_count + 1} contains PCBs:\n")
                for pcb in group:
                    file.write(f"{pcb} ")
                file.write(f"\nGroup {group_count + 1} contains materials:\n")
                used_material = []
                for pcb in group:
                    for material in pcb_data_dict[pcb]:
                        if material not in used_material:
                            used_material.append(material)
                for material in used_material:
                    file.write(f"{material} ")
                file.write("\n")
            file.write("\n")
            
def call(number_of_data):
    C_max = 15  # maximum slot size
    dataset_path = "./50_entry_dataset/"  # path to dataset
    material_catalogue_path = f"{dataset_path}Material_catalogue.csv"  # path to csv file of Material_catelogue
    material_catalogue = pd.read_csv(material_catalogue_path)  # read csv file of Material_catelogue
    material_catalogue = material_catalogue.to_numpy()
    material_catalogue = material_catalogue[:, :2]
    material_catalogue_dict = {key: value for key, value in
                               material_catalogue}  # setup dictonary of materials ( key: Material Index , value: Slot Width ) using Material_catelogue
    pcb_data_dict = {}
    pcb_files = [f"{dataset_path}PCB{i:03d}.csv" for i in range(1, number_of_data + 1)]
    for pcb_number, each_file in enumerate(pcb_files):  # read every PCBs in pcb_files
        pcb = pd.read_csv(each_file)
        pcb_data_dict[f'PCB{pcb_number + 1:03d}'] = pcb[
            "Material Index"].values  # preparing dictionary of PCBs (key: Name of PCB, value: Material Index)
    pcb_list = list(pcb_data_dict.keys())  # list of all PCBs
    pcb_list = sorted(pcb_list, key=lambda x: sum(material_catalogue_dict[key] for key in pcb_data_dict[x]),reverse=True)  # sorting PCBS basing on their total slot width in descending order
# -----------------------------------------------------
# Generating Combinations
    best_combinations = []        # initialize a list to store the best combinations
    min_comb_len = float('inf')   # initialize a variable to store the length of the smallest combination found
    for combination in generate_combinations(pcb_list, pcb_data_dict, material_catalogue_dict, C_max):            # iterate over each valid combination generated by the generate_combinations function
        if len(combination) < min_comb_len:    # if the current combination has fewer groups than the previously found minimum, update the minimum and clear the best_combinations list
            min_comb_len = len(combination)
            best_combinations.clear()          # less efficient combinations ( combinations with larger number of groups are deleted )
    if len(combination) == min_comb_len:    # if the current combination has the same number of groups as the minimum, add it to the best_combinations list
        best_combinations.append(combination)

    return create_json_data(best_combinations, pcb_data_dict)


def call_list(input_pcb_list):
    """
    This function takes a list of PCBs and returns the optimal grouping for the list of PCBs.

    :param list or number of PCBs
    :return json dictionary containing the groups and materials required for the production process
    """
    print(input_pcb_list)
    if type(input_pcb_list)==type(1):
        input_pcb_list = [input_pcb_list]
    if len(input_pcb_list) <= 0: 
        return {"Error": "empty input list"}
    if min(input_pcb_list) < 1 or max(input_pcb_list) > 50: 
        return {"Error": "the input PCBs must be between 1 and 50"}
    C_max = 15  # maximum slot size
    dataset_path = "./50_entry_dataset/"  # path to dataset
    material_catalogue_path = f"{dataset_path}Material_catalogue.csv"  # path to csv file of Material_catelogue
    material_catalogue = pd.read_csv(material_catalogue_path)  # read csv file of Material_catelogue
    material_catalogue = material_catalogue.to_numpy()
    material_catalogue = material_catalogue[:, :2]
    material_catalogue_dict = {key: value for key, value in
                               material_catalogue}  # setup dictonary of materials ( key: Material Index , value: Slot Width ) using Material_catelogue
    pcb_data_dict = {}
    for pcb_number in input_pcb_list:
        each_file = f"{dataset_path}PCB{pcb_number:03d}.csv"
        pcb = pd.read_csv(each_file)
        pcb_data_dict[f'PCB{pcb_number:03d}'] = pcb[
            "Material Index"].values  # preparing dictionary of PCBs (key: Name of PCB, value: Material Index)
    
    pcb_list = list(pcb_data_dict.keys())  # list of all PCBs
    pcb_list = sorted(pcb_list, key=lambda x: sum(material_catalogue_dict[key] for key in pcb_data_dict[x]),reverse=True)  # sorting PCBS basing on their total slot width in descending order
# -----------------------------------------------------
# Generating Combinations
    best_combinations = []        # initialize a list to store the best combinations
    while len(best_combinations) == 0:
        min_comb_len = float('inf')   # initialize a variable to store the length of the smallest combination found
        for combination in generate_combinations(pcb_list, pcb_data_dict, material_catalogue_dict, C_max):            # iterate over each valid combination generated by the generate_combinations function
            if len(combination) < min_comb_len:    # if the current combination has fewer groups than the previously found minimum, update the minimum and clear the best_combinations list
                min_comb_len = len(combination)
                best_combinations.clear()          # less efficient combinations ( combinations with larger number of groups are deleted )
            if len(combination) == min_comb_len:    # if the current combination has the same number of groups as the minimum, add it to the best_combinations list
                best_combinations.append(combination)

    return create_json_data(best_combinations, pcb_data_dict)