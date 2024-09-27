import sys, os.path as path
sys.path.append(path.abspath(path.join(__file__, path.pardir, path.pardir)))

import datetime as dt

import pandas as pd
from langchain.agents import tool

from llm.prompt_utils import *
from llm.algorithm_calls import solutions_memory


current_date = dt.datetime.strptime("2024-10-04", "%Y-%m-%d")

path_to_vbap = "SAP_Data/VBAP.csv"


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


@tool
def PrioritizeBasedOnSAP():
    """
    Prioritize PCBs based on SAP data (VBAP table). Select PCBs with the closest delivery dates.
    This function genereated the PCB that should be prioritized and can be used as input for the FilterPCBs function
    """
    vbap_df = pd.read_csv(path_to_vbap)
    vbap_df["EDATU"] = pd.to_datetime(vbap_df["EDATU"])
    
    upcoming_orders = vbap_df[vbap_df["EDATU"] > current_date]
    closest_orders = upcoming_orders.sort_values(by="EDATU").head(5)  # Limit to 5 closest 
    
    prioritized_pcbs = closest_orders["MATNR"].tolist()
    
    if prioritized_pcbs:
        return f"PCBs with the delivery dates in descending order: {prioritized_pcbs}. If the Input from the Human doenst match with these tell the Human that there are no open order for the PCBs the Human mentioned."
    else:
        return "No upcoming orders found for prioritization."

@tool
def PrioritizationChoice():
    """
    Ask the user if they want to prioritize PCBs based on SAP data or their own input. This should always be done
    before calling the FilterPCBs function.
    """
    return "Do you want to prioritize based on SAP data or your own input? Please specify."
