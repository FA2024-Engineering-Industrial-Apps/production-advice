import sys, os.path as path
sys.path.append(path.abspath(path.join(__file__, path.pardir, path.pardir)))

from langchain.agents import tool

from algorithms.bruteforce.serial import call_list
from algorithms.bruteforce.parallel import call_list_parallel
from algorithms.bruteforce.hybrid import call_list_hybrid
from llm.prompt_utils import *

solutions_memory = {}

@tool
def CallOptimizer(PCBnumber):
    """
    Function to optimize the grouping of PCBs for the production line.
    Args: 
        - PCBnumber: this should either be a a list of PCBs or a single int for one PCBs.
    """
    PCBnumber = sanitize_input(PCBnumber)
    json_data = call_list(PCBnumber)
    solutions_memory['current_solutions'] = json_data
    save_output(json_data)
    try:
        if len(json_data['combinations']) > 4:
            return f"More than 4 optimal solutions found. Would you like to prioritize specific PCBs?"
        else:
            return json_data
    except:
        return json_data


@tool
def CallHybridOptimizer(NumberOfPCBs):
    """
    Function to optimize the grouping of PCBs for the production line in a hybrid manner.
    Args: 
        - NumberOfPCBs: this should either be a a list of PCBs or a single int for a range of PCBs.
    """
    NumberOfPCBs = sanitize_input(NumberOfPCBs)
    json_data = call_list_hybrid(NumberOfPCBs)
    solutions_memory['current_solutions'] = json_data
    save_output(json_data)
    try:
        if len(json_data['combinations']) > 4:
            return f"More than 4 optimal solutions found. Would you like to prioritize specific PCBs?"
        else:
            return json_data
    except:
        return json_data


@tool
def CallParallelOptimizer(NumberOfPCBs):
    """
    Function to optimize the grouping of PCBs for the production line in a parallel manner.
    Args: 
        - NumberOfPCBs: this should either be a a list of PCBs or a single int for a range of PCBs. 
    """
    NumberOfPCBs = sanitize_input(NumberOfPCBs)
    json_data = call_list_parallel(NumberOfPCBs)
    solutions_memory['current_solutions'] = json_data
    save_output(json_data)
    try:
        if len(json_data['combinations']) > 4:
            return f"More than 4 optimal solutions found. Would you like to prioritize specific PCBs?"
        else:
            return json_data
    except:
        return json_data