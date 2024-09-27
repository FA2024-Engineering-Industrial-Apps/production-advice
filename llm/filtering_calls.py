import sys, os.path as path
sys.path.append(path.abspath(path.join(__file__, path.pardir, path.pardir)))

from langchain.agents import tool

from llm.prompt_utils import *
from llm.algorithm_calls import solutions_memory

@tool
def FilterPCBs(important_pcbs):
    """
    Filters the PCB combinations based on user-specified important PCBs.
    Args: 
        - important_pcbs: a list of PCB numbers (e.g., [1, 2]) the user wants to prioritize.
    
    Returns:
        - A filtered list of groups that include at least one of the important PCBs.
    """
    important_pcbs = sanitize_input(important_pcbs)
    important_pcbs_str = [f"PCB{str(pcb).zfill(3)}" for pcb in important_pcbs]

    solutions = solutions_memory.get('current_solutions')
    
    if not solutions:
        return "No solutions available to filter."
    
    filtered_groups = []
    
    for combination in solutions['combinations']:
        for _, groups in combination.items():
            matching_groups = [group for group in groups if any(pcb in group['PCBs'] for pcb in important_pcbs_str)]
            if matching_groups:
                filtered_groups.extend(matching_groups) 
        if len(filtered_groups) >= 4:
            break  

    if not filtered_groups:
        return f"No groups found containing the specified PCBs: {important_pcbs_str}."
    
    return filtered_groups
