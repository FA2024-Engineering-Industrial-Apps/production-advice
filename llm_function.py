import json
from langchain_core.tools import tool
import pandas as pd
import BruteForcing_Serial as algorithm

@tool
def get_best_combination_json(pcb_numbers: list[int]) -> str:
    """
        Given the list of PCBs to produce, would group them together,
        such that PCBs in the same group can be produced simultaniously in parallel,
        and the number of groups is the least.

        Parameters
        ----------
        pcb_numbers: list[str]
            List of indecies of the PCBs to group

        Returns
        -------
        best_combination: str
            The JSON representation of the list of groups of PCBs,
            that could be produced together
    """

    dataset_path = "./50_entry_dataset/"  # path to dataset
    material_catalogue_path = f"{dataset_path}Material_catalogue.csv"  # path to csv file of Material_catelogue
    material_catalogue = pd.read_csv(material_catalogue_path)  # read csv file of Material_catelogue
    material_catalogue = material_catalogue.to_numpy()
    material_catalogue = material_catalogue[:, :2]
    material_catalogue_dict = {key: value for key, value in
                               material_catalogue}  # setup dictonary of materials ( key: Material Index , value: Slot Width ) using Material_catelogue
    
    