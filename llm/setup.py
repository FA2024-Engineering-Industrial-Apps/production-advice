import sys, os.path as path
sys.path.append(path.abspath(path.join(__file__, path.pardir, path.pardir)))

from llm.algorithm_calls import *
from llm.prioritization_calls import *
from llm.prompt import *
from llm.get_data_callback import OnGetData
from utils.csv_utils import create_csv_from_input

from typing import Callable

import pandas as pd
from langchain_core.callbacks import BaseCallbackHandler
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_tool_calling_agent, tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


model = ChatOllama(
    model="qwen2.5:32b",
    temperature=0,
    seed=0,
    base_url="workstation.ferienakademie.de"
)

tools = [
    CallOptimizer,
    CallSerialOptimizer,
    CallHybridOptimizer,
    CallParallelOptimizer,
    SelectOneOptimalPCB,
    PrioritizeBasedOnSAP
]
agent = create_tool_calling_agent(model, tools, prompt)

class OnToolCall(BaseCallbackHandler):
    def __init__(self, callback: Callable[[str, str], None]) -> None:
        super().__init__()
        self.callback = callback

    def on_tool_start(self, *args, **kwargs):
        function_name = args[0]["name"]
        function_arguments = args[1]
        self.callback(function_name, function_arguments)
        return super().on_tool_start(*args, **kwargs)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    return_intermediate_steps=True
)

if __name__ == "__main__":
    result = agent_executor.invoke(
        {
            "input": "opt 1-15",
            "chat_history": []
        },
        config={
            "callbacks": [OnToolCall(lambda name: print(name))]
        }
    )
    print(result)