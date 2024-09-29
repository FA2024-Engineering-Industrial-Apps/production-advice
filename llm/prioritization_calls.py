import sys, os.path as path
sys.path.append(path.abspath(path.join(__file__, path.pardir, path.pardir)))

import datetime as dt

import pandas as pd
from langchain.agents import tool

from algorithms.objects import *
from llm.prompt_utils import *
from llm.algorithm_calls import solutions_memory

TIME_PER_SETUP_CHANGE = 2 * 60 * 60
TIME_PER_PCB = 10


current_date = dt.datetime.strptime("2024-10-03", "%Y-%m-%d")

path_to_vbap = "SAP_Data/VBAP.csv"


@tool
def FilterPCBsFromUserInput(important_pcbs):
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
    This function generates the PCB that should be prioritized and can be used as input for the FilterPCBs function.
    
    Modified to return a list of tuples with PCBs grouped by their delivery date.
    """
    vbap_df = pd.read_csv(path_to_vbap)
    vbap_df["EDATU"] = pd.to_datetime(vbap_df["EDATU"])

    upcoming_orders = vbap_df[(vbap_df["EDATU"] > current_date) & (vbap_df["EDATU"] <= current_date + dt.timedelta(days=7))]
    upcoming_orders_sorted = upcoming_orders.sort_values(by="EDATU")
    
    solutions = solutions_memory.get('current_solutions')
    if not isinstance(solutions, dict):
        return {"error": "First optimization should be called before prioritizing PCBs."}
    combinations = Combinations.from_json(solutions)

    sap_plan = [*upcoming_orders_sorted.groupby("EDATU", as_index=False)[["MATNR", "KWMENG"]].agg(list).itertuples(index=False, name=None)]
    
    for combination in combinations.combinations:
        slack = int(0)
        prev_date = current_date
        mapping = {pcb.name: group_id for (group_id, group) in enumerate(combination.groups) for pcb in group.pcbs}
        # TODO: optimize if there is an overlap between different days, and we can start with the same group we left yesterday
        for date, pcbs, number in sap_plan:
            assert isinstance(date, pd.Timestamp)
            slack += (date.to_pydatetime() - prev_date).total_seconds()
            prev_date = date.to_pydatetime()

            used_groups = {mapping[pcb_name] for pcb_name in pcbs}
            total_amount = sum(number)

            slack -= len(used_groups) * TIME_PER_SETUP_CHANGE
            slack -= total_amount * TIME_PER_PCB

            if slack < 0:
                break
        
        if slack >= 0:
            mapping = {pcb.name: group_id for (group_id, group) in enumerate(combination.groups) for pcb in group.pcbs}
            slack = int(0)

            days_stack = []
            prev_date = current_date
            cur_date = None

            current_order = []
            current_group = None

            orderding = []

            for date, pcbs, number in sap_plan:
                assert isinstance(date, pd.Timestamp)
                days_stack.append(date.to_pydatetime())
                
                for pcb, amount in sorted(zip(pcbs, number), key=lambda x: mapping[x[0]]):
                    delta = ((current_group != mapping[pcb]) * TIME_PER_SETUP_CHANGE) + (amount * TIME_PER_PCB)
                    if delta > slack:
                        orderding.append({
                            "date": cur_date,
                            "order": current_order
                        })
                        
                        current_group = None
                        delta = ((current_group != mapping[pcb]) * TIME_PER_SETUP_CHANGE) + (amount * TIME_PER_PCB)
                        while slack < delta:
                            cur_date = days_stack.pop(0)
                            slack += int((cur_date - prev_date).total_seconds())
                            prev_date = cur_date
                        current_order = []
                    
                    slack -= delta
                    if current_group != mapping[pcb]:
                        current_group = mapping[pcb]
                        current_order.append("SETUP_CHANGE")
                    current_order.append(pcb)
            
            if current_order:
                orderding.append({
                    "date": cur_date.strftime("%Y-%m-%d"),
                    "order": current_order
                })

            return {
                "combination": combination.to_json(),
                "production_plan": orderding[1:]
            }
    
    return {"error": "No combination found with enough slack to fit the upcoming orders."}


@tool
def PrioritizationChoice():
    """
    Ask the user if they want to prioritize PCBs based on SAP data or their own input. This should always be done
    before calling the FilterPCBs function.
    """
    return "Do you want to prioritize based on SAP data or your own input? Please specify."


if __name__ == "__main__":
    path_0 = "output/0.json"
    with open(path_0, "r") as file:
        solutions = json.load(file)
    
    solutions_memory = {
        "current_solutions": solutions
    }

    print(PrioritizeBasedOnSAP({}))