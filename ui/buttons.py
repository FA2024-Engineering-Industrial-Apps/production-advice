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

XLSX_MAX_ROWS = 10485
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

        self.number_of_rows = len(df.index)
        self.xlsx_overflow = self.number_of_rows > XLSX_MAX_ROWS

        xlsx_path = os.path.abspath(os.path.join(
            __file__,
            os.path.pardir,
            os.path.pardir,
            f"output/{self.id}_tabular.xlsx"
        ))
        df = df.head(min(self.number_of_rows, XLSX_MAX_ROWS))
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
    
    def __show_excel_download_button(self, excel_file_name: str, id: int, label: str, key: str):
        st.download_button(
            label=label,
            data=open(excel_file_name, "rb"),
            file_name=os.path.basename(excel_file_name),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"excel_button_{id}_{key}",
            use_container_width=True
        )
    
    def __show_csv_download_button(self, csv_file_name: str, id: int, label: str, key: str):
        st.download_button(
            label=label,
            data=open(csv_file_name, "rb"),
            file_name=os.path.basename(csv_file_name),
            mime="text/csv",
            key=f"csv_button_{id}_{key}",
            use_container_width=True
        )
    
    @st.dialog("Too many combinations", width="large")
    def __display_excel_overflow_warning(self, tabular_csv_name: str, tabular_xlsx_name: str, id: int):
        assert self.export_button is not None
        st.write(
            f"Warning, Excel spreadsheets do not support than {XLSX_MAX_ROWS} rows. Current groupping result contains {self.export_button.number_of_rows} rows." +
            f"Only the first {XLSX_MAX_ROWS} rows will be exported. If you need the full result, please download the CSV file."
        )
        c1, c2 = st.columns([1, 1])
        with c1:
            self.__show_excel_download_button(tabular_xlsx_name, id, "Download Excel export anyway", "overflow")
        with c2:
            self.__show_csv_download_button(tabular_csv_name, id, "Download full CSV export", "overflow")

    def __display_export_button(self, column: DeltaGenerator):
        export = self.export_button
        assert export is not None
        id = export.id
        with column.popover("Export", use_container_width=True):
            # CSV
            tabular_csv_name = export.get_tabular_csv()
            self.__show_csv_download_button(tabular_csv_name, id, "Download CSV export", "normal")

            # Excel
            excel_file_name = export.get_tabular_xlsx()
            if export.xlsx_overflow:
                if st.button("Download Excel export"):
                    self.__display_excel_overflow_warning(tabular_csv_name, excel_file_name, id)
            else:
                self.__show_excel_download_button(excel_file_name, id, "Download Excel export", "normal")

    def __display_deploy_button(self, column: DeltaGenerator):
        order = self.deploy_button
        assert order is not None
        if column.button("Send to edge", use_container_width=True):
            result_message = csv_utils.publish_user_data(order.order)
            st.toast(result_message)
    
    def display(self):
        if (self.export_button is not None) != (self.deploy_button is not None):
            _, c1 = st.columns([3, 1])
            if self.deploy_button is not None:
                self.__display_deploy_button(c1)
            else:
                self.__display_export_button(c1)
        elif (self.export_button is not None) and (self.deploy_button is not None):
            _, c1, c2 = st.columns([3, 1, 1])
            self.__display_export_button(c1)
            self.__display_deploy_button(c2)