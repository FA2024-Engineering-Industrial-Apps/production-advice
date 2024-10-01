import sys, os.path as path
sys.path.append(path.abspath(path.join(__file__, path.pardir, path.pardir)))

from langchain.agents import tool

from algorithms.bruteforce.serial import call_list
from algorithms.bruteforce.parallel import call_list_parallel
from algorithms.bruteforce.hybrid import call_list_hybrid
from llm.prompt_utils import *

MAX_PCBS_FOR_SERIAL = 10

solutions_memory = {}

@tool
def CallOptimizer(ListOfPCBsNumbers):
    """
    It is not an algorithm on its own, but a fallback function that should be called
    if the user wants to optimize the grouping of PCBs for the production line without specifying the optimization type.
    It is not an algorithm, do NOT mention it to the user.

    Args: 
        - ListOfPCBsNumbers: this should either be a a list of PCBs or a single int for one PCBs. If a range of PCBs should be optimized, expand it as a list of consecutive integers (e.g., 1-5 -> [1, 2, 3, 4, 5]).
    """
    try:
        ListOfPCBsNumbers = sanitize_input(ListOfPCBsNumbers)
        if len(ListOfPCBsNumbers) <= MAX_PCBS_FOR_SERIAL:
            print(F"Serial optimization is used for less than {MAX_PCBS_FOR_SERIAL} PCBs")
            json_data = call_list(ListOfPCBsNumbers)
        else:
            print(F"Hybrid optimization is used for more than {MAX_PCBS_FOR_SERIAL} PCBs")
            json_data = call_list_hybrid(ListOfPCBsNumbers)
    except:
        return "Incorrect function parameters are provided: PCBnumber: this should either be a a list of PCBs or a single int for one PCBs"

    solutions_memory['current_solutions'] = json_data
    save_output(json_data)
    try:
        return check_n_of_combinations(json_data)
    except:
        return json_data


@tool
def CallSerialOptimizer(ListOfPCBsNumbers):
    """
    Function to optimize the grouping of PCBs for the production line in a serial manner. 
    This function should only be called if the user asks for serial optimization.
    Better suited for less than 10 PCBs.

    Args: 
        - ListOfPCBsNumbers: this should either be a a list of PCBs or a single int for a range of PCBs.
    """
    try:
        ListOfPCBsNumbers = sanitize_input(ListOfPCBsNumbers)
        json_data = call_list(ListOfPCBsNumbers)
    except:
        return "Incorrect function parameters are provided: PCBnumber: this should either be a a list of PCBs or a single int for one PCBs"

    solutions_memory['current_solutions'] = json_data
    save_output(json_data)
    try:
        return check_n_of_combinations(json_data)
    except:
        return json_data
    

@tool
def CallHybridOptimizer(ListOfPCBsNumbers):
    """
    Function to optimize the grouping of PCBs for the production line in a hybrid manner. 
    This function should only be called if the user asks for hybrid optimization.
    Better suited for more than 10 PCBs.

    Args: 
        - ListOfPCBsNumbers: this should either be a a list of PCBs or a single int for a range of PCBs.
    """
    try:
        ListOfPCBsNumbers = sanitize_input(ListOfPCBsNumbers)
        json_data = call_list_hybrid(ListOfPCBsNumbers)
    except:
        return "Incorrect function parameters are provided: PCBnumber: this should either be a a list of PCBs or a single int for one PCBs"
    
    solutions_memory['current_solutions'] = json_data
    save_output(json_data)
    try:
        return check_n_of_combinations(json_data)
    except:
        return json_data
    

@tool
def CallParallelOptimizer(ListOfPCBsNumbers):
    """
    Function to optimize the grouping of PCBs for the production line in a parallel manner.
    This function should only be called if the user asks for parallel optimization.
    Is experimental and should be used with caution.

    Args: 
        - ListOfPCBsNumbers: this should either be a a list of PCBs or a single int for a range of PCBs. 
    """
    try:
        ListOfPCBsNumbers = sanitize_input(ListOfPCBsNumbers)
        json_data = call_list_parallel(ListOfPCBsNumbers)
    except:
        return "Incorrect function parameters are provided: PCBnumber: this should either be a a list of PCBs or a single int for one PCBs"
    
    solutions_memory['current_solutions'] = json_data
    save_output(json_data)
    try:
        return check_n_of_combinations(json_data)
    except:
        return json_data
