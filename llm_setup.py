from BruteForcing_Serial_func import call_list
import pandas as pd

from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_tool_calling_agent, tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage

@tool
def Text2Csv(text):
    """Converts text to a csv file"""
    return 'not yet implemented'

@tool
def CallOptimizer(NumberOfPCBs):
    """
    Function to optimize the grouping of PCBs for the production line
    Args: NumberOfPCBs: this should either be a a list of PCBs or a single int for a range of PCBs.
    """
    json_data = call_list(NumberOfPCBs)
    return json_data


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant"),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)
model = ChatOllama(
    model="llama3-groq-tool-use",
    temperature=0,
    seed=0
)
tools = [CallOptimizer, Text2Csv]
agent = create_tool_calling_agent(model, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)