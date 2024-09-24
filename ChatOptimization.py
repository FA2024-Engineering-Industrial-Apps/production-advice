from BruteForcing_Serial_func import call
import pandas as pd

from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_tool_calling_agent, tool
from langchain_core.prompts import ChatPromptTemplate
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