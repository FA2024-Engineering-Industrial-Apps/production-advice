import sys, os.path as path
sys.path.append(path.abspath(path.join(__file__, path.pardir, path.pardir)))

import utils.create_csv as csv_utils
import utils.docker_utils as docker_utils
import llm.setup as llmchat

import streamlit as st
from streamlit.delta_generator import DeltaGenerator
import pandas as pd
import json
import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class DataExport:
    path: str

    def __post_init__(self):
        self.id = int(os.path.basename(self.path)[:-len(".json")])

    def __get_json_data(self) -> dict:
        with open(self.path) as file:
            json_data = json.load(file)
        return json_data

    @st.cache_data
    def get_tabular_csv(self) -> str:
        """Loads JSON data and returns it as a Pandas DataFrame."""
        return csv_utils.json_solution_to_tabular_csv(
            self.id,
            self.__get_json_data()
        )

    @st.cache_data
    def get_tabular_xlsx(self):
        """Exports the DataFrame to an Excel file."""
        csv_path = self.get_tabular_csv()
        df = pd.read_csv(csv_path)
        df.columns = ["Combination ID", "Group ID", "PCB"]

        xlsx_path = path = os.path.abspath(os.path.join(
            __file__,
            os.path.pardir,
            os.path.pardir,
            f"output/{self.id}_tabular.xlsx"
        ))
        df.to_excel(xlsx_path, index=False)
        return xlsx_path

EXPORTING_FUNCTIONS = [func.func.__name__ for func in [
    llmchat.CallOptimizer,
    llmchat.CallHybridOptimizer,
    llmchat.CallParallelOptimizer,
]]

@dataclass
class OrderDeployment:
    order: dict

DEPLOYING_FUNCTIONS = [func.func.__name__ for func in [
    llmchat.PrioritizeBasedOnSAP,
]]


@dataclass
class MessageButton:
    export_button: Optional[DataExport] = None
    deploy_button: Optional[OrderDeployment] = None

    @classmethod
    def isinstance(cls, obj) -> bool:
        return type(obj).__name__ == cls.__name__

    def __display_export_button(self, column: DeltaGenerator):
        export = self.export_button
        assert export is not None
        id = export.id
        with column.popover("Export", use_container_width=True):
            # CSV
            tabular_csv_name = export.get_tabular_csv()
            st.download_button(
                label="Download CSV export",
                data=open(tabular_csv_name, "rb"),
                file_name=os.path.basename(tabular_csv_name),
                mime="text/csv",
                key=f"csv_button_{id}",
                use_container_width=True
            )

            # Excel
            excel_file_name = export.get_tabular_xlsx()
            st.download_button(
                label="Download Excel export",
                data=open(excel_file_name, "rb"),
                file_name=os.path.basename(excel_file_name),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"excel_button_{id}",
                use_container_width=True
            )

    def __display_deploy_button(self, column: DeltaGenerator):
        order = self.deploy_button
        assert order is not None
        if docker_utils.is_run_in_docker() and column.button("Send to edge", use_container_width=True):
            csv_utils.publish_user_data(order.order)
    
    def display(self):
        can_use_deploy = docker_utils.is_run_in_docker() and self.deploy_button is not None
        if (self.export_button is not None) != (can_use_deploy):
            _, c1 = st.columns([3, 1])
            if can_use_deploy:
                self.__display_deploy_button(c1)
            else:
                self.__display_export_button(c1)
        elif (self.export_button is not None) and (can_use_deploy):
            _, c1, c2 = st.columns([3, 1, 1])
            self.__display_export_button(c1)
            self.__display_deploy_button(c2)