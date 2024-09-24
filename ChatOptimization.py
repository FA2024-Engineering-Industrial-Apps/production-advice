from langchain_core.tools import tool
from langchain_ollama import ChatOllama


@tool
def Text2Csv(text):
    """Converts text to a csv file"""
    return 'not yet implemented'

@tool
def CallOptimizer(NumberOfPCBs):
    """Function to optimize the grouping of PCBs for the production line
    Args: NumberOfPCBs: The total amount of PCBs to be optimized
    
    """
    return f'**optmized PCB Grouping {NumberOfPCBs}**'

tools = [CallOptimizer, Text2Csv]



llm = ChatOllama(model="llama3-groq-tool-use", temperature=0).bind_tools(tools) #8B
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
