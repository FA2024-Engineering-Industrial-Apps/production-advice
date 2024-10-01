import sys, os.path as path
sys.path.append(path.abspath(path.join(__file__, path.pardir, path.pardir)))

from langchain.agents import tool

from algorithms.bruteforce.serial import call_list
from algorithms.bruteforce.parallel import call_list_parallel
from algorithms.bruteforce.hybrid import call_list_hybrid
from llm.prompt_utils import *

solutions_memory = {}

@tool
def CallOptimizer(ListOfPCBsNumbers):
    """
    Standard function to optimize the grouping of PCBs for the production line. 
    This function should be called if the user doesn't ask for a specific optimization.

    Args: 
        - ListOfPCBsNumbers: this should either be a a list of PCBs or a single int for one PCBs. If a range of PCBs should be optimized, expand it as a list of consecutive integers (e.g., 1-5 -> [1, 2, 3, 4, 5]).
    """
    try:
        ListOfPCBsNumbers = sanitize_input(ListOfPCBsNumbers)
        if len(ListOfPCBsNumbers) <= 15:
            json_data = call_list(ListOfPCBsNumbers)
        else:
            json_data = call_list_hybrid(ListOfPCBsNumbers)
    except:
        return "Incorrect function parameters are provided: PCBnumber: this should either be a a list of PCBs or a single int for one PCBs"

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
def CallSerialOptimizer(ListOfPCBsNumbers):
    """
    Function to optimize the grouping of PCBs for the production line in a serial manner. 
    This function should only be called if the user asks for serial optimization.

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
        if len(json_data['combinations']) > 4:
            return f"More than 4 optimal solutions found. Would you like to prioritize specific PCBs?"
        else:
            return json_data
    except:
        return json_data
    

@tool
def CallHybridOptimizer(ListOfPCBsNumbers):
    """
    Function to optimize the grouping of PCBs for the production line in a hybrid manner. 
    This function should only be called if the user asks for hybrid optimization.

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
        if len(json_data['combinations']) > 4:
            return f"More than 4 optimal solutions found. Would you like to prioritize specific PCBs?"
        else:
            return json_data
    except:
        return json_data


@tool
def CallParallelOptimizer(ListOfPCBsNumbers):
    """
    Function to optimize the grouping of PCBs for the production line in a parallel manner.
    This function should only be called if the user asks for parallel optimization.

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
        if len(json_data['combinations']) > 4:
            return f"More than 4 optimal solutions found. Would you like to prioritize specific PCBs?"
        else:
            return json_data
    except:
        return json_data