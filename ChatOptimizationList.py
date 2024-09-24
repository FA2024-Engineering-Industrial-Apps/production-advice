from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from BruteForcing_Serial_func import call, call_list
from langchain_core.messages import HumanMessage, SystemMessage
import pandas as pd



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

tools = [CallOptimizer, Text2Csv]



llm = ChatOllama(model="llama3-groq-tool-use", temperature=0, seed=0).bind_tools(tools) #8B

query = "Please optimize the PCB grouping for the PCBs 4 8 and also 10"
message = [HumanMessage(query), SystemMessage('You are a helpful assitantant.')]
query2 = "I have to optimize the PCBs 1-5"
query3 = 'please optimize the PCB grouping for PCBs 1 3 5 7'

result = llm.invoke(query3)
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