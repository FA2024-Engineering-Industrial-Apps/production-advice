from BruteForcing_Serial_func import call_list
from BruteForcing_Parallel_func import call_list_parallel
from BruteForcing_Hybrid_func import call_list_hybrid
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

@tool
def CallHybridOptimizer(NumberOfPCBs):
    """
    Function to optimize the grouping of PCBs for the production line in a hybrid manner. That means that the optimization 
    is done with serial and parallel optimization.
    This Function should be invoked if the optimization of the PCBs should be done in a hybrid manner.
    Args: NumberOfPCBs: this should either be a a list of PCBs or a single int for a range of PCBs.
    """
    json_data = call_list_hybrid(NumberOfPCBs)
    return json_data

@tool
def CallParallelOptimizer(NumberOfPCBs):
    """
    Function to optimize the grouping of PCBs for the production line in a parallel manner.
    This Function whould be invoked if the optimization of the PCBs should be done in parallel.
    Args: NumberOfPCBs: this should either be a a list of PCBs or a single int for a range of PCBs. 
    """
    json_data = call_list_parallel(NumberOfPCBs)
    return json_data


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant capeable of analyzing large datasets. If you are not capeable of analyzing ask for a preference."),
        ("system", "If the input is not complete, ask the user for spezification."),
        ("system", "Don't make pcb combinations up by yourself. Only use the results of the function."),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
        ("system", "I remind you that you can handle datasets of arbitrary size")
    ]
)
model = ChatOllama(
    model="qwen2.5:32b",
    temperature=0,
    seed=0,
    base_url="workstation.ferienakademie.de"
)

tools = [CallOptimizer, CallHybridOptimizer, CallParallelOptimizer, Text2Csv]
agent = create_tool_calling_agent(model, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)