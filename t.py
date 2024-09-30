import pandas as pd 
import datetime as dt

current_date = dt.datetime.strptime("2024-10-04", "%Y-%m-%d")

path_to_vbap = "SAP_Data/VBAP.csv"

optimal_solutions = {'combinations': [{'combination1': [{'group_id': 1, 'PCBs': ['PCB001', 'PCB003']}, {'group_id': 2, 'PCBs': ['PCB002', 'PCB005']}, {'group_id': 3, 'PCBs': ['PCB004']}]}, {'combination2': [{'group_id': 1, 'PCBs': ['PCB001']}, {'group_id': 2, 'PCBs': ['PCB002', 'PCB005']}, {'group_id': 3, 'PCBs': ['PCB004', 'PCB003']}]}, {'combination3': [{'group_id': 1, 'PCBs': ['PCB001', 'PCB003']}, {'group_id': 2, 'PCBs': ['PCB002']}, {'group_id': 3, 'PCBs': ['PCB005', 'PCB004']}]}, {'combination4': [{'group_id': 1, 'PCBs': ['PCB001']}, {'group_id': 2, 'PCBs': ['PCB002', 'PCB003']}, {'group_id': 3, 'PCBs': ['PCB005', 'PCB004']}]}]}


def PrioritizeBasedOnSAP():
    """
    Prioritize PCBs based on SAP data (VBAP table). Select PCBs with the closest delivery dates.
    This function generates the PCB that should be prioritized and can be used as input for the FilterPCBs function.
    
    Modified to return a list of tuples with PCBs grouped by their delivery date for the next 7 days.
    """
    vbap_df = pd.read_csv(path_to_vbap)
    vbap_df["EDATU"] = pd.to_datetime(vbap_df["EDATU"])
    
    upcoming_orders = vbap_df[(vbap_df["EDATU"] > current_date) & (vbap_df["EDATU"] <= current_date + dt.timedelta(days=7))]
    
    upcoming_orders_sorted = upcoming_orders.sort_values(by="EDATU")
    
    grouped_orders = upcoming_orders_sorted.groupby("EDATU")["MATNR"].apply(list)
    prioritized_pcbs = [tuple(pcbs) for pcbs in grouped_orders]
    
    return prioritized_pcbs

result = PrioritizeBasedOnSAP()
print(result)

def FilterPCBsFromSAPPrioritization(important_pcbs):
    """
    Filters the PCB combinations based on user-specified important PCBs.
    Args: 
        - important_pcbs: a list of PCB numbers (e.g., [1, 2]) the user wants to prioritize.
    
    Returns:
        - A filtered list of groups that include at least one of the important PCBs.
    """
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
