import json
from typing import Optional
from dataclasses import dataclass

@dataclass
class PCB():
    name: str
    materials: Optional[list[str]] = None

    def to_json(self):
        return {
            "name": self.name,
            "materials": self.materials
        }
    
    @classmethod
    def from_json(cls, json_data):
        return cls(
            name=json_data["name"],
            materials=json_data["materials"]
        )
    
    def __str__(self):
        return f"({self.name}, {self.materials})"


@dataclass
class Group():
    pcbs: list[PCB]

    def to_json(self, group_id: Optional[int] = None):
        if group_id is None:
            return [pcb.to_json() for pcb in self.pcbs]
        else:
            return {
                "group_id": group_id,
                "PCBs": [pcb.name for pcb in self.pcbs]
            }
    
    @classmethod
    def from_json(cls, json_data):
        if isinstance(json_data, list):
            return cls(
                pcbs=[PCB.from_json(pcb) for pcb in json_data]
            )
        else:
            return cls(
                pcbs=[PCB(name=pcb) for pcb in json_data["PCBs"]]
            )

    def __str__(self):
        return f"Group({self.pcbs})"


@dataclass
class Combination():
    groups: list[Group]

    def to_json(self, combination_id: Optional[int] = None):
        if combination_id is None:
            return {
                "groups": [group.to_json(i+1) for i, group in enumerate(self.groups)]
            }
        else:
            return {
                f"combination{combination_id}": [group.to_json(i+1) for i, group in enumerate(self.groups)]
            }
    
    @classmethod
    def from_json(cls, json_data):
        if "groups" in json_data:
            return cls(
                groups=[Group.from_json(group) for group in json_data["groups"]]
            )
        else:
            groups = next(iter(json_data.values()))
            return cls(
                groups=[Group.from_json(group) for group in groups]
            )

    def __str__(self):
        return f"Combination({self.groups})"


@dataclass
class Combinations():
    combinations: list[Combination]

    def to_json(self):
        if len(self.combinations) == 1:
            return self.combinations[0].to_json()
        else:
            return {
                "combinations": [
                    combination.to_json(i+1) for i, combination in enumerate(self.combinations)
                ]
            }

    @classmethod
    def from_json(cls, json_data):
        if "combinations" in json_data:
            return cls(
                combinations=[Combination.from_json(combination) for combination in json_data["combinations"]]
            )
        else:
            return cls(
                combinations=[Combination.from_json(json_data)]
            )
    
    def __str__(self):
        return f"Combinations({self.combinations})"


if __name__ == "__main__":
    output_5 = r"C:\buff\production-advice\output\5.json"
    output_0 = r"C:\buff\production-advice\output\0.json"

    with open(output_5) as file:
        json_data = json.loads(file.read())
        combinations = Combinations.from_json(json_data)
    
    for combination in combinations.combinations:
        print({pcb.name: group_id for (group_id, group) in enumerate(combination.groups) for pcb in group.pcbs})