import sys, os.path as path
sys.path.append(path.abspath(path.join(__file__, path.pardir, path.pardir)))

from algorithm_calls import *
from filtering_calls import *
from prompt import *

import pandas as pd

from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_tool_calling_agent, tool
from langchain_core.messages import HumanMessage, AIMessage


@tool
def Text2Csv(text):
    """Converts text to a csv file"""
    return 'not yet implemented'


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