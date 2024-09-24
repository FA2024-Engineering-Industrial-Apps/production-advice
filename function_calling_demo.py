from langchain_core.tools import tool
from langchain_ollama import ChatOllama

@tool
def GetWeather(location):
    """Get weather data for a specified location."""
    if location == "Munich":
        return 'cold and rainy'

@tool
def GetTraffic(location):
    """Use this tool to get traffic data for a specified location."""
    return f"Traffic data for {location}: heavy traffic"

tools = [GetWeather, GetTraffic]

llm = ChatOllama(model="llama3-groq-tool-use", temperature=0).bind_tools(tools) #8B
query = "Whats the weather in Munich?"

result = llm.invoke(query)
print(result)
print('\n')
tool_calls = result.tool_calls
print(tool_calls)
print('\n')

tool_mapping = {'GetWeather':GetWeather, 'GetTraffic': GetTraffic} # mapping between tool name and defined tool function


selected_tool = tool_mapping[tool_calls[0]['name']] # used to get the selected tool
tool_output = selected_tool.invoke(tool_calls[0]['args']) # invoke the selected tool with the argument
print(tool_output)
