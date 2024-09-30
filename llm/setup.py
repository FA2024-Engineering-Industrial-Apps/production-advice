import sys, os.path as path
sys.path.append(path.abspath(path.join(__file__, path.pardir, path.pardir)))

from llm.algorithm_calls import *
from llm.prioritization_calls import *
from llm.prompt import *
import os

from langchain_ollama import ChatOllama
from langchain_openai import OpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent, tool


openai_api_key = os.getenv("OPENAI_API")

@tool
def Text2Csv(text):
    """Converts text to a csv file"""
    return 'not yet implemented'


# key_path = "./key.txt"
# if path.isfile(key_path):
#     with open("key.txt", "r") as file:
#         api_endpoint = file.read()
# else:
#     raise RuntimeError("No key.txt provided!")

model = OpenAI(
    model="GPT-4o",
    temperature=0.2,
    seed=0,
    max_retries=2,
    api_key=openai_api_key,
    #base_url="workstation.ferienakademie.de"
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