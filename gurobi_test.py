#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed July 12th

@author: sambringman
"""

import gurobipy as gp
from gurobipy import GRB
import numpy as np
import networkx as nx
import math
import qiskit
from pandas import read_csv
import time

start_time = time.time()

# Set up the circuit
path = "test_circuits/3_17_13.qasm"
qc = qiskit.QuantumCircuit.from_qasm_file(path)

n = 8

n_regular_graph = nx.random_regular_graph(3, n)
gates = n_regular_graph.edges()
#gates = [(0, 1), (1, 2), (0, 2)]

#gates = [(gate[1][0].index, gate[1][1].index) for gate in qc.data if len(gate[1]) == 2]

#gates = [(0, 1), (1, 2), (3, 5), (1, 5), (0, 5), 
         #(4, 6), (2, 7), ( 6, 7), (8, 4),
         #(4, 9), ( 8, 10), 
         #(7, 9), (5, 8), (10, 11), 
         #(11, 12), (12, 13), (7, 14),
         #]

"""
# 24 qubit test
gates = [(0,16),
(0,2),
(0,3),
(0,12),
(0,19),
(0,23),
(1,12),
(3,13),
(4,19),
(5,9),
(5,17),
(6,15),
(6,17),
(7,13),
(7,10),
(8,17),
(8,21),
(9,14),
(11,12),
(11,22),
(14,19),
(15,20),
(16,23),
(18,23),
]
"""
"""
# 25 qubit test
gates = [
    (0,15),
    (0,19),
    (0,22),
    (1,17),
    (2,4),
    (3,14),
    (3,17),
    (3,21),
    (3,23),
    (4,19),
    (5,7),
    (5,14),
    (6,9),
    (6,15),
    (6,16),
    (6,18),
    (7,8),
    (7,11),
    (7,20),
    (7,22),
    (8,12),
    (8,13),
    (8,20),
    (10,19),
    (11,14),
    (11,15),
    (12,14),
    (12,24),
    (13,17),
    (13,18),
    (13,22),
    (13,23),
    (14,16),
    (14,22),
    (16,20),
    (16,22),
    (16,23),
    (19,20),
    (20,23),
]
"""

"""
filepath = "./Original_Swap_Program/24_Node_Test.txt"
QUBO_gates = read_csv(filepath, skiprows=1)

gates = []
for index, row in QUBO_gates.iterrows():
    gates.append([row['Node1'], row['Node2']])

print(gates)
"""

max_qubit1 = max(qubit1 for qubit1, qubit2 in gates)
max_qubit2 = max(qubit2 for qubit1, qubit2 in gates)
num_qubits = max(max_qubit1, max_qubit2) + 1

time_steps = round(len(gates) * 0.5)
time_steps = 4
# Create lattice
lattice_width ,lattice_height = 2, 2

while True:
    lattice = nx.hexagonal_lattice_graph(lattice_width, lattice_height)
    lattice = nx.convert_node_labels_to_integers(lattice, first_label=0)

    num_nodes = len(lattice.nodes)

    if num_nodes <= num_qubits * 1.1:
        lattice_width += 1
        lattice_height += 1
    else:
        break

edges = [e for e in lattice.edges]

print(gates)
print(f"Qubits: {num_qubits}")
print(f"Lattice Nodes: {num_nodes}")
print(f"Gates: {len(gates)}")
print(f"Initial time step guess: {time_steps}")

while True:
    
    # Create model
    m = gp.Model("test_model")

    # Adjust Gurobi log settings to suppress output
    m.setParam('OutputFlag', 0)

    # Binary Decision Variables
    Y_array = np.empty((num_qubits, num_nodes, time_steps), dtype=gp.Var)
    SWAP_array = np.empty((len(edges), time_steps), dtype=gp.Var)
    Z_array = np.empty((len(gates), len(edges), time_steps), dtype=gp.Var)

    # Qubit placement variables
    for qubit in range(num_qubits):
        for node in range(num_nodes):
            for step in range(time_steps):
                Y_array[qubit][node][step] = m.addVar(vtype=gp.GRB.BINARY, name=f"Y{qubit},{node},{step}")

    #print(f"Number of Y variables: {len(Y_array.flatten())}")

    # SWAP variables
    for e, edge in enumerate(edges):
        for step in range(time_steps):
            SWAP_array[e][step] = m.addVar(vtype=gp.GRB.BINARY, name=f"SWAP{e},{step}")

    #print(f"Number of SWAP variables: {len(SWAP_array.flatten())}")

    print(f"Finished Creating Variables")

    # Applied gate variables
    for g, gate in enumerate(gates):
        for e, edge in enumerate(edges):
            for step in range(time_steps):
                Z_array[g][e][step] = m.addVar(vtype=gp.GRB.BINARY, name=f"Z{gate},{edge},{step}")

    #print(f"Number of Z variables: {len(Z_array.flatten())}")

    # Objectives#
    m.setObjective(gp.quicksum(SWAP_array.flatten()), GRB.MINIMIZE)

    # Add constraint 1 - Each lattice node has 1 qubit
    for node in range(num_nodes):
        for step in range(time_steps):
            m.addConstr(gp.quicksum(Y_array[qubit][node][step] for qubit in range(num_qubits)) <= 1)

    #print(f"Number of constraint 1s: {num_nodes * time_steps}")

    # Add constraint 2 - Each lattice node has one qubit
    for qubit in range(num_qubits):
        for step in range(time_steps):
            m.addConstr(gp.quicksum(Y_array[qubit][node][step] for node in range(num_nodes)) == 1)

    #print(f"Number of constraint 2s: {num_qubits * time_steps}")

    # Add constraint 3 - Applied gate definition
    for g, gate in enumerate(gates):
        for e, edge in enumerate(edges):
            for step in range(time_steps):
                m.addConstr(Z_array[g][e][step] <= 0.5 * (
                    Y_array[gate[0]][edge[0]][step] +
                    Y_array[gate[1]][edge[0]][step] +
                    Y_array[gate[0]][edge[1]][step] +
                    Y_array[gate[1]][edge[1]][step])
                    )
                
    #print(f"Number of constraint 3s: {len(gates) * len(edge) * time_steps}")

    # Add constraint 4 - Each gate must be applied exactly once
    for g, gate in enumerate(gates):
        m.addConstr(gp.quicksum(Z_array[g].flatten()) == 1)

    #print(f"Number of constraint 4s: {len(gates)}")

    # Add constraint 5 - A qubit can either not move, be swapped with a neighbor, 
    # or have a gate with its neighbor
    for qubit in range(num_qubits):
        for node in range(num_nodes):
            for step in range(time_steps - 1):
                m.addConstr(
                    Y_array[qubit][node][step + 1] <=
                    # Didn't move
                    Y_array[qubit][node][step] +
                    # Did move
                    gp.quicksum( 
                        (Y_array[qubit][neighbor_node][step] *
                        # Swapped
                        (SWAP_array[edges.index((min(node, neighbor_node), max(node, neighbor_node)))][step + 1] +
                        # Went through gate and swapped
                        gp.quicksum(Z_array[g][edges.index((min(node, neighbor_node), max(node, neighbor_node)))][step + 1] for g, gate in enumerate(gates) if qubit in gate)))
                        for neighbor_node in range(num_nodes) if (min(node, neighbor_node), max(node, neighbor_node)) in edges
                        )
                )

    #print(f"Number of constraint 5s: {num_qubits * num_nodes * (time_steps - 1)}")


    # Add constraint 6 - each qubit can only be in one gate per time step
    for step in range(time_steps):
        for node in range(num_nodes):
            m.addConstr(
                gp.quicksum(
                    (gp.quicksum(Z_array[g][e][step] for g, gate in enumerate(gates)) + 
                    SWAP_array[e][step]) for e, edge in enumerate(edges) if node in edge
                ) <= 1
            )
  
    #print(f"Number of constraint 6s: {time_steps * num_qubits}")
    print(f"Finished Adding Constraints")

    # Optimize model
    m.update()
    m.optimize()

    # Check the optimization status
    status = m.status

    if status == gp.GRB.OPTIMAL:
        # Feasible solution found
        # Variable count
        print(f"Number of Y variables: {len(Y_array.flatten())}")
        print(f"Number of SWAP variables: {len(SWAP_array.flatten())}")
        print(f"Number of Z variables: {len(Z_array.flatten())}")
        print(f"Number of constraint 1s: {num_nodes * time_steps}")
        print(f"Number of constraint 2s: {num_qubits * time_steps}")
        print(f"Number of constraint 3s: {len(gates) * len(edge) * time_steps}")
        print(f"Number of constraint 4s: {len(gates)}")
        print(f"Number of constraint 5s: {num_qubits * num_nodes * (time_steps - 1)}")
        print(f"Number of constraint 6s: {time_steps * num_qubits}")
        break
    else:
        print(f"No solution found for {time_steps} time steps")
        # Increase the parameter value
        time_steps += 1

for v in m.getVars():
    if v.x == 1:
        print('%s %g' % (v.varName, v.x))

end_time = time.time()

print('Obj: %g' % m.objVal)

print(f"Minimum Swaps: {m.objVal}")
print(f"Time Steps: {time_steps}")
print(f"Total Time Taken: {round(((end_time - start_time)), 4)} seconds")
