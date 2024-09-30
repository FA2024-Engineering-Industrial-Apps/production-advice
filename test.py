import time
from algorithms.bruteforce.serial import call_list
from algorithms.bruteforce.parallel import call_list_parallel
from algorithms.bruteforce.hybrid import call_list_hybrid







def FilterPCBs(important_pcbs):
    """
    Filters the PCB combinations based on user-specified important PCBs.
    Args: 
        - important_pcbs: a list of PCB numbers (e.g., [1, 2]) the user wants to prioritize.
    
    Returns:
        - A filtered list of groups that include at least one of the important PCBs.
    """
    
    # Convert the integer PCBs (e.g., 1) to string format (e.g., 'PCB001')
    important_pcbs_str = [f"PCB{str(pcb).zfill(3)}" for pcb in important_pcbs]

    solutions = solutions_memory.get('current_solutions')
    
    if not solutions:
        return "No solutions available to filter."
    
    filtered_groups = []
    
    for combination in solutions['combinations']:
        for _, groups in combination.items():
            # Collect the groups that contain the prioritized PCBs
            matching_groups = [group for group in groups if any(pcb in group['PCBs'] for pcb in important_pcbs_str)]
            if matching_groups:
                filtered_groups.extend(matching_groups)  # Add matching groups to the result
        if len(filtered_groups) >= 4:
            break  # Limit to the first 4 matching groups

    if not filtered_groups:
        return f"No groups found containing the specified PCBs: {important_pcbs_str}."
    
    return filtered_groups


if __name__ == "__main__":
    pcb_list =  list(range(1, 5))

    solutions_memory = {}
    start_time_parallel = time.time()
    result_parallel = call_list(pcb_list)
    solutions_memory['current_solutions'] = result_parallel 
    end_time_parallel = time.time()
    execution_time_parallel = end_time_parallel - start_time_parallel

    print(f"n of combinations: {len('groups')}")
    print(" Function Result:")
    print(result_parallel)
    print(f" Execution Time: {execution_time_parallel} seconds")


    important_pcbs = [1]
    filtered = FilterPCBs(important_pcbs)
    print('\n')
    print(filtered)


