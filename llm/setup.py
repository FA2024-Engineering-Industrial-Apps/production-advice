import sys, os.path as path
sys.path.append(path.abspath(path.join(__file__, path.pardir, path.pardir)))

from algorithms.bruteforce.serial import call_list
from algorithms.bruteforce.parallel import call_list_parallel
from algorithms.bruteforce.hybrid import call_list_hybrid
import pandas as pd

from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_tool_calling_agent, tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage

solutions_memory = {}

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
    model="llama3.1:70b",
    temperature=0,
    seed=0,
    base_url=api_endpoint
)

tools = [CallOptimizer, CallHybridOptimizer, CallParallelOptimizer, FilterPCBs, Text2Csv]
agent = create_tool_calling_agent(model, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

if __name__ == "__main__":
    print(agent_executor.invoke(
        {
            "input": "Hello there!",
            "chat_history": []
        }
    ))