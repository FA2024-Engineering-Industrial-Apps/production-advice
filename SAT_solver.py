from ortools.sat.python import cp_model
import pandas as pd
import os
import psutil
import sys


number_of_data = int(sys.argv[1])
g_init = 14             #maximum number of groups
C_max = 15              #maximum slot width


## Creating the model
model = cp_model.CpModel()

X_mp = {}
# Slot width of materials: Format-Material index m: slot width s_m
s_m = {}
# If material m in group g: Format-Material index m: group g (Binary)
x_mg = {}
# If PCB p contains material m: Format-PCBx Material index m(Binary)
x_pg = {}
# If g-th group is used(Binary)
y_g = {}

## Reading PCBs data
pcb_data = []
pcb_files = [f"50_entry_dataset/PCB{i:03d}.csv" for i in range(1, number_of_data+1)]
for pcb_number, each_file in enumerate(pcb_files):
    pcb = pd.read_csv(each_file)
    pcb['PCB_Index'] = f'PCB{pcb_number+1:03d}'
    pcb_data.append(pcb)
material_catalogue = pd.read_csv(f"50_entry_dataset/Material_catalogue.csv")
## Preparing variables
#s_m
s_m = dict(zip(material_catalogue['Material Index'], material_catalogue['Slot Width']))
#x_mp
for pcb in pcb_data:
    for materials in s_m.keys():
        X_mp[pcb["PCB_Index"][0], materials] = materials in pcb["Material Index"].values
#x_pg
for pcb in pcb_data:
    pcb_name = pcb["PCB_Index"][0]
    for group in range(1, g_init+1):
        x_pg[pcb_name, group] = model.NewBoolVar( f'x_{pcb_name}_{group}')
#x_mg
for group in range(1, g_init+1):
    for materials in s_m.keys():
        x_mg[materials, group] = model.NewBoolVar(f'x_{materials}_{group}')
#y_g
for group in range(1, g_init+1):
    y_g[group] = model.NewBoolVar( f'y_{group}')

# Adding Constraints
# Constraint 1: Each PCB to exactly 1 setup group
for pcb in pcb_data:
    pcb_name = pcb["PCB_Index"][0]
    model.Add(sum(x_pg[pcb_name, group] for group in range(1, g_init + 1)) == 1)
pcb_index = []
for pcb in pcb_data:
    name = pcb["PCB_Index"][0]
    pcb_index.append(name)
# Constraint 2: Activation condition
for group in range(1, g_init+1):
    for pcb in pcb_index:
        model.Add(x_pg[pcb, group] <= y_g[group])
# Constraint 3: Capacity condition
for group in range(1, g_init+1):
    model.Add(sum(s_m[materials] * x_mg[materials, group] for materials in s_m.keys()) <= C_max)
# Constraint 4: Combination condition
for pcb in pcb_index:
    for group in range(1, g_init+1):
        for materials in s_m.keys():
            model.Add(x_pg[pcb, group] + int(X_mp[pcb, materials]) - x_mg[materials, group] <= 1)

## Solving the model
model.Minimize(sum(y_g[g]*10*g for g in range(1, g_init+1)))
solver = cp_model.CpSolver()
status = solver.Solve(model)

## Reporting the results
print(f"Solve status: {solver.StatusName(status)}")
print(f"Optimal objective value: {solver.ObjectiveValue()}")
print("Statistics")
print(f"  - conflicts : {solver.NumConflicts()}")
print(f"  - branches  : {solver.NumBranches()}")
print(f"  - wall time : {solver.WallTime()}s")
process = psutil.Process(os.getpid())
memory_usage = process.memory_info().rss
print(f"Memory usage: {memory_usage / (1024 * 1024)} MB")
for g in range(1, g_init+1):
    print("Group " + str(g) + " is used: " + str(solver.Value(y_g[g])))