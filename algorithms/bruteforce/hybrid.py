"""
This script is designed to optimize the grouping of Printed Circuit Boards (PCBs) based on their material requirements
and slot widths using a hybrid brute forcing optimization algorithm. It utilizes multiprocessing to efficiently find
minimum number of groups inside a valid combination and generates valid combinations while adhering to a
maximum slot width constraint (C_max).
"""
import pandas as pd
import time
import psutil
import os
import sys
import multiprocessing
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

def worker(min_group, pcb_list, pcb_data_dict, material_catalogue_dict, C_max, shared_mingp, lock):
    """
    Worker function to find the first valid combination of PCBs with a specific minimum number of groups.

    :param min_group: Minimum number of groups to test.
    :param pcb_list: List of PCBs.
    :param pcb_data_dict: Dictionary with PCB identifiers as keys and their respective materials as values.
    :param material_catalogue_dict: Dictionary with material identifiers as keys and their respective slot widths as values.
    :param C_max: Maximum allowed slot width for any group.
    :param shared_mingp: Multiprocessing.Value to store the minimum number of groups found.
    :param lock: Lock object to ensure thread-safe access to shared_mingp.
    """
    try:
        if next(generate_combinations(pcb_list, pcb_data_dict, material_catalogue_dict, C_max, min_groups=[min_group])):    # attempt to generate combinations with the given min_group

            with lock:                                                              # If a valid combination is found, update the shared_mingp if the current min_group is smaller
                if min_group < shared_mingp.value:
                    shared_mingp.value = min_group
    except StopIteration:                                                           # handle the case where no valid combinations are found

        pass

def find_first_combination(max_num_group, pcb_list, pcb_data_dict, material_catalogue_dict, C_max):
    """
    Finds the only first valid combination of PCBs using multiple processes to test different minimum group sizes concurrently.

    :param max_num_group: Maximum number of groups to test.
    :param pcb_list: List of PCBs.
    :param pcb_data_dict: Dictionary with PCB identifiers as keys and their respective materials as values.
    :param material_catalogue_dict: Dictionary with material identifiers as keys and their respective slot widths as values.
    :param C_max: Maximum allowed slot width for any group.
    :return: Minimum number of groups needed to create a valid combination of PCBs.
    """
    manager = multiprocessing.Manager()
    shared_mingp = multiprocessing.Value('i', len(pcb_list))    # shared integer value to store the minimum number of groups found, initialized to number_of_data - 1

    lock = manager.Lock()                                        # lock object to ensure thread-safe access to shared_mingp
    processes = []                                               # list to store the process objects

    for min_group in range(1, max_num_group + 1):                     # create and start processes for each min_group value from 1 to k

        p = multiprocessing.Process(target=worker, args=(min_group, pcb_list, pcb_data_dict, material_catalogue_dict, C_max, shared_mingp, lock))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    return shared_mingp.value

import time
import pandas as pd
import multiprocessing

def call_list_hybrid(input_pcb_list):
    """
    This function takes a list of PCB numbers and returns the optimal grouping for the list of PCBs.
    It uses the hybrid brute force approach, which leverages multiprocessing to find the minimum number of groups
    and then brute-forces valid combinations while adhering to the maximum slot width constraint (C_max).
    """
    assert len(input_pcb_list) > 0, "Error: empty input list."
    assert min(input_pcb_list) >= 1 and max(input_pcb_list) <= 50, "Error: PCB numbers must be between 1 and 50."
    
    C_max = 15  # maximum slot size
    dataset_path = "./50_entry_dataset/"  # path to dataset
    material_catalogue_path = f"{dataset_path}Material_catalogue.csv"  # path to csv file of Material_catalogue
    material_catalogue = pd.read_csv(material_catalogue_path)  # read csv file of Material_catalogue
    material_catalogue = material_catalogue.to_numpy()
    material_catalogue = material_catalogue[:, :2]
    material_catalogue_dict = {key: value for key, value in material_catalogue}  # setup dictionary of materials
    
    pcb_data_dict = {}
    for pcb_number in input_pcb_list:
        each_file = f"{dataset_path}PCB{pcb_number:03d}.csv"
        pcb = pd.read_csv(each_file)
        pcb_data_dict[f'PCB{pcb_number:03d}'] = pcb["Material Index"].values  # preparing dictionary of PCBs
    
    pcb_list = list(pcb_data_dict.keys())  # list of all PCBs
    pcb_list = sorted(pcb_list, key=lambda x: sum(material_catalogue_dict[key] for key in pcb_data_dict[x]), reverse=True)  # sorting PCBs by total slot width

   
    min_group = find_first_combination(len(pcb_list), pcb_list, pcb_data_dict, material_catalogue_dict, C_max)

   
    best_combinations = []
    for combination in generate_combinations(pcb_list, pcb_data_dict, material_catalogue_dict, C_max, min_groups=[float(min_group)]):
        best_combinations.append(combination)

    
    json_data = {"groups": []}
    for group_id, group in enumerate(best_combinations[0], start=1):
        group_pcbs = []
        group_materials = set()  
        for pcb_group in group:
            if pcb_group in pcb_data_dict:
                group_pcbs.append(pcb_group)
                group_materials.update(pcb_data_dict[pcb_group])

        
        json_data["groups"].append({
            "group_id": group_id,
            "PCBs": group_pcbs,
            "materials": list(group_materials)  
        })
    
    return json_data