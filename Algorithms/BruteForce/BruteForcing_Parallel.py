"""
This script is designed to optimize the grouping of Printed Circuit Boards (PCBs) based on their material requirements
and slot widths using a parallel brute forcing optimization algorithm. It generates optimal valid combinations
while adhering to a maximum slot width constraint (C_max).
"""

import copy
import pandas as pd
import time
import psutil
import os
import sys
import multiprocessing
import copy
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
    shared_mingp = multiprocessing.Value('i', number_of_data)    # shared integer value to store the minimum number of groups found, initialized to number_of_data - 1

    lock = manager.Lock()                                        # lock object to ensure thread-safe access to shared_mingp
    processes = []                                               # list to store the process objects

    for min_group in range(1, max_num_group + 1):                     # create and start processes for each min_group value from 1 to k

        p = multiprocessing.Process(target=worker, args=(min_group, pcb_list, pcb_data_dict, material_catalogue_dict, C_max, shared_mingp, lock))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    return shared_mingp.value

def find_permute(pcb_list, pcb_data_dict, material_catalogue_dict, C_max):
    """
    This function calculates permutations of the first PCB with other PCBs in the list and returns possible valid groups of size 2.

    :param pcb_list: List of PCBs.
    :param pcb_data_dict: Dictionary with PCB identifiers as keys and their respective materials as values.
    :param material_catalogue_dict: Dictionary with material identifiers as keys and their respective slot widths as values.
    :param C_max: Maximum allowed slot width for any group.
    :return: List of valid groups, each containing 2 PCBs.
    """
    pair_list = []
    for i in range(len(pcb_list) - 1):
        possible_group = []
        possible_group.append(pcb_list[0])
        possible_group.append(pcb_list[i + 1])
        if is_valid_group(possible_group, pcb_data_dict, material_catalogue_dict, C_max):
            pair_list.append(possible_group)
    return pair_list

def process_pair(pair, pcb_list, pcb_data_dict, material_catalogue_dict, C_max, min_gp, output_list, i):
    """
    This function processes pairs generated by the find_permute function.
    It starts to find possible combinations starting with a given pair, checks if it is already generated,
    and if not, appends the valid combination into the output_list.

    :param pair: Pair of PCBs to start the combination.
    :param pcb_list: List of PCBs.
    :param pcb_data_dict: Dictionary with PCB identifiers as keys and their respective data (e.g., materials) as values.
    :param material_catalogue_dict: Dictionary containing material data.
    :param C_max: Maximum allowed slot width for any group.
    :param min_gp: Minimum number of groups for a valid combination.
    :param output_list: List to store the valid combinations.
    :param i: Index used to filter the PCB list.
    """
    filtered_list = copy.copy(pcb_list)                   # create a copy of the PCB list and remove the elements in the pair
    for sub_element in pair:
        filtered_list.remove(sub_element)

    for j in range(i):                                     # remove the first i elements from the filtered_list to avoid duplicates
        filtered_list.remove(pcb_list[j])

    current_groups = [pair]                                # initialize current groups with the pair
    for combination in generate_combinations(filtered_list, pcb_data_dict, material_catalogue_dict, C_max,current_groups=current_groups, min_groups=[min_gp]):     # generate combinations starting with the current_groups

        for j in range(i):                                  # append the first i elements as separate groups (already counted in previous iteraion)
            combination.append([pcb_list[j]])

        if len(combination) == min_gp:                      # if the combination has the desired number of groups, add it to the output list (checks for duplications)
            combination_frozenset = frozenset(frozenset(group) for group in combination)
            output_list.append(combination_frozenset)


def main(pcb_list, pcb_data_dict, material_catalogue_dict, C_max, min_gp):
    """
    Finds the best combinations of PCBs (Printed Circuit Boards) based on given constraints.
    Parameters:
    :param pcb_list: List of PCBs.
    :param pcb_data_dict: Dictionary with PCB identifiers as keys and their respective data (e.g., materials) as values.
    :param material_catalogue_dict: Dictionary containing material data.
    :param C_max: Maximum allowed slot width for any group.
    :param min_gp: Minimum number of groups for a valid combination.
    :return List of best combinations of PCBs with minimum number of groups needed to create a valid combination of PCBs.
    """
    manager = multiprocessing.Manager()             # set up multiprocessing manager and shared list for output
    output_list = manager.list()
    best_combinations_set = set()

    cpu_count = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=cpu_count)

    for i in range(len(pcb_list)):
        pairs = find_permute(pcb_list[i:], pcb_data_dict, material_catalogue_dict, C_max)                   # find all permissible pairs of PCBs starting from the current index
        all_pairs = [(pair, pcb_list, pcb_data_dict, material_catalogue_dict, C_max, min_gp, output_list, i) for pair in
                     pairs]                                                             # create a list of arguments for each pair to be processed in parallel

        pool.starmap_async(process_pair, all_pairs).get()

    pool.close()
    pool.join()

    for combination in output_list:                                                     # collect results from the output list and add to the set to ensure uniqueness
        best_combinations_set.add(combination)

    best_combinations_total = list(best_combinations_set)                                   # convert the set to a list to return the unique best combinations
    return best_combinations_total
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

# -----------------------------------------------------
if __name__ == "__main__":

    number_of_data = int(sys.argv[1])  # get number_of_data at runtime
    assert 1 <= number_of_data <= 50, "Error: number_of_data must be between 1 and 50."
    print(f"number_of_data is valid: {number_of_data}")
# -----------------------------------------------------
# Start timing
    start_time = time.time()
# -----------------------------------------------------
# Reading data and initialization
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
#finds minimum number of groups in a valid combination
    min_group = find_first_combination(number_of_data-1, pcb_list, pcb_data_dict, material_catalogue_dict, C_max)
#finds every possible combination with min_group size in parallel
    best_combinations = main(pcb_list, pcb_data_dict, material_catalogue_dict, C_max, min_group)

# -----------------------------------------------------
# Measuring runtime
    end_time = time.time()
    execution_time = end_time - start_time
# -----------------------------------------------------
# Writing the output_file
    write_results(best_combinations,pcb_list,pcb_data_dict,material_catalogue_dict, C_max,dataset_path,execution_time)
