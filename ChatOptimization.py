from BruteForcing_Serial_func import call
import pandas as pd

from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

from typing import Iterable, Any

@tool
def Text2Csv(text):
    """Converts text to a csv file"""
    return 'not yet implemented'

@tool
def CallOptimizer(NumberOfPCBs):
    """Function to optimize the grouping of PCBs for the production line
    Args: NumberOfPCBs: The total amount of PCBs to be optimized
    
    """
    json_data = call(NumberOfPCBs)
    return json_data

tools = [CallOptimizer, Text2Csv]


history_dict = dict()
def get_session_history(session_id):
    if session_id in history_dict:
        return history_dict[session_id]
    history_dict[session_id] = ChatMessageHistory()
    return history_dict[session_id]


llm = ChatOllama(
    model="llama3-groq-tool-use",
    temperature=0,
    seed=0
).bind_tools(tools) #8B

if __name__ == "__main__":
    query = "Please optimize the PCB grouping for PCB 1-3"
    
    result = llm.invoke(query)
    print(result)
    print('\n')
    tool_calls = result.tool_calls
    print(tool_calls)
    print('\n')

    tool_mapping = {'CallOptimizer':CallOptimizer, 'Text2Csv': Text2Csv} # mapping between tool name and defined tool function


    selected_tool = tool_mapping[tool_calls[0]['name']] # used to get the selected tool
    tool_output = selected_tool.invoke(tool_calls[0]['args']) # invoke the selected tool with the argument
    print(tool_output)

    PCB_grouping = [{'group_id': group['group_id'], 'PCBs': ', '.join(group['PCBs'])} for group in tool_output['groups']]


    df = pd.DataFrame(PCB_grouping)

    print(df)