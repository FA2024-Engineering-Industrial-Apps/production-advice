from typing import Callable

from langchain_core.callbacks import BaseCallbackHandler, BaseRunManager
from langchain.agents import tool


class OnGetData(BaseCallbackHandler):
    def __init__(self, data: dict) -> None:
        super().__init__()
        self.data = data

    def get_data(self) -> dict:
        return self.data
    

def parse_tool_data(callbacks: BaseRunManager):
    on_data_handler = next(filter(lambda x: isinstance(x, OnGetData), callbacks.handlers), None)
    if not on_data_handler:
        return None

    assert isinstance(on_data_handler, OnGetData)
    return on_data_handler.get_data()
