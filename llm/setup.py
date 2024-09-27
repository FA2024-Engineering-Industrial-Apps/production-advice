import sys, os.path as path
sys.path.append(path.abspath(path.join(__file__, path.pardir, path.pardir)))

from llm.algorithm_calls import *
from llm.prioritization_calls import *
from llm.prompt import *
from utils.create_csv import create_csv_from_input

import pandas as pd
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_tool_calling_agent, tool
from langchain_core.messages import HumanMessage, AIMessage


@tool
def Text2Csv(groups_of_pcbs_in_csv_format):
    """
    Function to create a data for exporting the Human selected combination into groups of PCBs in the CSV format. Always have a format like this Group,"PCB001,PCB002".
    Args: 
        - combination_of_pcbs_in_csv_format: It contains the Group number and their respective list of PCB members.
    Return:
        -  file_path : The name of the file that was created
    """
    file_path=create_csv_from_input(groups_of_pcbs_in_csv_format)
    return file_path

# key_path = "./key.txt"
# if path.isfile(key_path):
#     with open("key.txt", "r") as file:
#         api_endpoint = file.read()
# else:
#     raise RuntimeError("No key.txt provided!")

model = ChatOllama(
    model="qwen2.5:32b",
    temperature=0,
    seed=0,
    base_url="workstation.ferienakademie.de"
)

tools = [
    CallOptimizer,
    CallHybridOptimizer,
    CallParallelOptimizer,
    FilterPCBs,
    Text2Csv,
    PrioritizeBasedOnSAP,
    PrioritizationChoice
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