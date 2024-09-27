import sys, os.path as path
sys.path.append(path.abspath(path.join(__file__, path.pardir, path.pardir)))

from algorithms.bruteforce.serial import call_list
from algorithms.bruteforce.parallel import call_list_parallel
from algorithms.bruteforce.hybrid import call_list_hybrid
import pandas as pd
import json
import datetime as dt
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_tool_calling_agent, tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage

solutions_memory = {}

current_date = dt.datetime.strptime("2024-10-04", "%Y-%m-%d")

path_to_vbap = "SAP_Data/VBAP.csv"

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


@tool
def Text2Csv(text):
    """Converts text to a csv file"""
    return 'not yet implemented'


@tool
def CallOptimizer(NumberOfPCBs):
    """
    Function to optimize the grouping of PCBs for the production line.
    Args: 
        - NumberOfPCBs: this should either be a a list of PCBs or a single int for a range of PCBs.
    """
    if isinstance(NumberOfPCBs, str):
        NumberOfPCBs = json.loads(NumberOfPCBs)
    json_data = call_list(NumberOfPCBs)
    solutions_memory['current_solutions'] = json_data 
    if len(json_data['combinations']) > 4:
        return f"More than 4 optimal solutions found. Would you like to prioritize specific PCBs?"
    else:
        return json_data


@tool
def CallHybridOptimizer(NumberOfPCBs):
    """
    Function to optimize the grouping of PCBs for the production line in a hybrid manner.
    Args: 
        - NumberOfPCBs: this should either be a a list of PCBs or a single int for a range of PCBs.
    """
    if isinstance(NumberOfPCBs, str):
        NumberOfPCBs = json.loads(NumberOfPCBs)
    json_data = call_list_hybrid(NumberOfPCBs)
    solutions_memory['current_solutions'] = json_data 
    if len(json_data['combinations']) > 4:
        return f"More than 4 optimal solutions found. Would you like to prioritize specific PCBs?"
    else:
        return json_data


@tool
def CallParallelOptimizer(NumberOfPCBs):
    """
    Function to optimize the grouping of PCBs for the production line in a parallel manner.
    Args: 
        - NumberOfPCBs: this should either be a a list of PCBs or a single int for a range of PCBs. 
    """
    if isinstance(NumberOfPCBs, str):
        NumberOfPCBs = json.loads(NumberOfPCBs)
    json_data = call_list_parallel(NumberOfPCBs)
    solutions_memory['current_solutions'] = json_data 
    if len(json_data['combinations']) > 4:
        return f"More than 4 optimal solutions found. Would you like to prioritize specific PCBs?"
    else:
        return json_data
    
@tool
def FilterPCBs(important_pcbs):
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



prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant capable of analyzing large datasets. If you are not capable of analyzing, ask for a preference."),
        ("system", "If the input is not complete, ask the user for specification."),
        ("system", "Don't make PCB combinations up by yourself. Only use the results of the function."),
        ("system", "You are not allowed to call more than one optimization function in response to a single prompt."),
        ("system", "Never output just a single or a subset of the groups of an optimal combination. The Human should always see "),
        ("system", "You should d"),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ]
)

key_path = "./key.txt"
if path.isfile(key_path):
    with open("key.txt", "r") as file:
        api_endpoint = file.read()
else:
    raise RuntimeError("No key.txt provided!")

model = ChatOllama(
    model= "qwen2.5:32b",   #"llama3.1:70b"
    temperature=0,
    seed=0,
    base_url= "workstation.ferienakademie.de"   #api_endpoint
)

tools = [
        CallOptimizer
        , CallHybridOptimizer 
        , CallParallelOptimizer
        , FilterPCBs
        , Text2Csv
        , PrioritizeBasedOnSAP
        , PrioritizationChoice
         ]
agent = create_tool_calling_agent(model, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

if __name__ == "__main__":
    print(agent_executor.invoke(
        {
            "input": "Hello there!",
            "chat_history": []
        }
    ))