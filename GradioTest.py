import gradio as gr
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from BruteForcing_Serial_func import call
import pandas as pd

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

llm = ChatOllama(model="llama3-groq-tool-use", temperature=0).bind_tools(tools)  # 8B model

def process_query(query):
    result = llm.invoke(query)
    tool_calls = result.tool_calls
    tool_mapping = {'CallOptimizer': CallOptimizer, 'Text2Csv': Text2Csv}

    if tool_calls:
        selected_tool = tool_mapping[tool_calls[0]['name']]
        tool_output = selected_tool.invoke(tool_calls[0]['args'])

        PCB_grouping = [
            {'group_id': group['group_id'], 'PCBs': ', '.join(group['PCBs'])}
            for group in tool_output['groups']
        ]
        df = pd.DataFrame(PCB_grouping)
        return df
    else:
        return str(result)

iface = gr.Interface(
    fn=process_query,
    inputs=gr.Textbox(lines=2, placeholder="Enter your query here..."),
    outputs=gr.Dataframe(),
    title="LLM PCB Optimizer",
    description="Enter a query to optimize PCB grouping."
)

iface.launch()
