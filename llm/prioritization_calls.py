import sys, os.path as path
sys.path.append(path.abspath(path.join(__file__, path.pardir, path.pardir)))

from functools import reduce
import datetime as dt

import pandas as pd
from langchain.agents import tool

from algorithms.objects import *
from llm.prompt_utils import *
from llm.algorithm_calls import solutions_memory
from llm.prompt_utils import *
from llm.get_data_callback import parse_tool_data

TIME_PER_SETUP_CHANGE = 2 * 60 * 60
TIME_PER_PCB = 10
TIME_PER_DAY = 8 * 60 * 60
SETUP_CHANGE = "SETUP_CHANGE"


current_date = dt.datetime.strptime("2024-10-03", "%Y-%m-%d")


@tool
def SelectOneOptimalPCB():
    """
    Selects one of the optimal solutions.
    Returns one optimal pcb combination
    """
    solutions = solutions_memory.get('current_solutions')
    if not solutions or not isinstance(solutions, dict):
        return {"error": "Run the optimization again first. If the arguments are already known, don't ask the user and just run optimization again"}
    
    return solutions['combinations'][0]


@tool
def PrioritizeBasedOnSAP(callbacks):
    """
    Prioritize PCBs based on SAP data and selects PCBs with the closest delivery dates.
    
    Returns a list of tuples with PCBs grouped by their delivery date and a production plan for the prioritized PCBs.
    """
    vbap_df = parse_tool_data(callbacks)["vbap_data"]

    upcoming_orders = vbap_df[(vbap_df["EDATU"] > current_date) & (vbap_df["EDATU"] <= current_date + dt.timedelta(days=7))]
    upcoming_orders_sorted = upcoming_orders.sort_values(by="EDATU")
    
    solutions = solutions_memory.get('current_solutions')
    if not isinstance(solutions, dict):
        return {"error": "Run the optimization again first. If the arguments are already known, don't ask the user and just run optimization again"}
    combinations = Combinations.from_json(solutions)

    sap_plan = [*upcoming_orders_sorted.groupby("EDATU", as_index=False)[["MATNR", "KWMENG"]].agg(list).itertuples(index=False, name=None)]
    
    for combination in combinations.combinations:
        cur_date = current_date
        cur_deadline = current_date + dt.timedelta(days=1)

        ordering = []
        cur_group_to_pcbs: dict[int, dict[str, int]] = dict()
        cur_working_time = 0

        def push_in_ordering():
            nonlocal ordering, cur_group_to_pcbs, cur_working_time, cur_date
            ordering.append({
                "date": cur_date.strftime("%Y-%m-%d"),
                "order": reduce(lambda x, y: x + [SETUP_CHANGE] + y, ([*entry.items()] for entry in cur_group_to_pcbs.values()), [])
            })
            cur_group_to_pcbs = dict()
            cur_working_time = 0
            cur_date += dt.timedelta(days=1)

        mapping = {pcb.name: group_id for (group_id, group) in enumerate(combination.groups) for pcb in group.pcbs}
        for date, pcbs, number in sap_plan:
            assert isinstance(date, pd.Timestamp)
            cur_deadline = date.to_pydatetime()

            for pcb, amount in sorted(zip(pcbs, number), key=lambda x: mapping[x[0]]):
                group = mapping[pcb]
                while amount > 0:
                    if cur_date > cur_deadline:
                        break

                    possible_amount = max(0, min(amount, (TIME_PER_DAY - cur_working_time - (group not in cur_group_to_pcbs) * TIME_PER_SETUP_CHANGE) // TIME_PER_PCB))
                    if possible_amount > 0:
                        cur_working_time += possible_amount * TIME_PER_PCB + (group not in cur_group_to_pcbs) * TIME_PER_SETUP_CHANGE
                        pcb_dict = cur_group_to_pcbs.setdefault(group, dict())
                        pcb_dict[pcb] = pcb_dict.get(pcb, 0) + possible_amount
                        amount -= possible_amount
                    else:
                        push_in_ordering()
                
                if cur_date > cur_deadline:
                    break
            
            if cur_date > cur_deadline:
                break
        
        if cur_date <= cur_deadline:
            if cur_group_to_pcbs != dict():
                push_in_ordering()
            
            cache_order({
                "production_plan": ordering
            })

            return {
                "explanation": f"There are only {len(combination.groups)} SETUP_CHANGEs, which happen in between the PCBs from different groups or different days.",
                "combination": combination.to_json(),
                "production_plan": ordering
            }
    
    return {"error": "No combination found with enough slack to fit the upcoming orders."}


if __name__ == "__main__":
    path_0 = "output/0.json"
    with open(path_0, "r") as file:
        solutions = json.load(file)
    
    solutions_memory = {
        "current_solutions": solutions
    }

    print(PrioritizeBasedOnSAP({}))