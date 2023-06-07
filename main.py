#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  3 16:18:25 2023

@author: sambringman
"""

import PySimpleGUI as sg
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from pandas import read_csv
import random
import sys

# Import from my function program
import graph_functions as graph_func
import gui_functions as gui_func

"""
To Do:
    Move the mapping code to the other file
    Place end tails if the connecting node has no open neighbors
    Start swapping
    Test if changing the axes will zoom in the images
    Make the file input work with graphs with the first node labelled 1 instead of 0
"""


"""
Variables
"""

# Sets the font options
font = ("Helvetica", 17)
sg.set_options(font=font)
title_font = 'Courier 20'

# Creates a dummy window to try and standardize window sizes
# across different editors and computers
dummy_window = sg.Window("dummy", [[]], finalize=True)

base_px = sg.tkinter.font.Font().measure('A')
f_px = sg.tkinter.font.Font(font=font).measure('A')

graph_width = base_px * 150
graph_height = base_px * 100

dummy_window.close()

# Adds color to the windows
sg.theme('DarkTeal7')

# Layout of the first window
layout = [[sg.Text('Welcome to the Minimum Swap Algorithm Interface!', font=title_font, size=(45, 3))],
          [sg.Text('How many variables in your QUBO?', size=(28, 1)), sg.InputText('7', key='-INPUT-')],
          [sg.Text("", size=(40, 1), key='-ERROR-')],
          [sg.Text("You may also load a file below to preconstruct the edges")],
          [sg.FileBrowse(target='file'), sg.Input('None', key='file')],
          [sg.Button("Enter"), sg.Cancel()],
          [sg.Text("")],
          ]

"""
First Window:
    For taking in input about the QUBO
    Transferring that info into a graph
"""

# Create the Window
window = sg.Window('Min Swap Program', layout, finalize=True)
window.move_to_center() # This doesn't work right for some reason

# Event Loop to process "events"
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Cancel'):
        window.close()
        sys.exit()

    # If they enter anything, test to see if it is valid
    if event == "Enter":
        num_nodes = values['-INPUT-']

        try:
            test = range(int(num_nodes))

            if int(num_nodes) > 0:
                break
            else:
                window["-ERROR-"].update("Invalid input, please enter a valid number")

        except:
            window["-ERROR-"].update("Invalid input, please enter a number")

window.close()

"""
Data Processing the User Input
"""

QUBO_Graph, num_nodes, num_edges, list_nodes = graph_func(num_nodes, values["file"])

"""
Second Window:
    Putting in the edges
    Making the QUBO graph
"""

info_column = [[sg.Text("Number of Nodes: "), sg.Text(key='-NUM_VAR-', size=(10, 1))],
               [sg.Text("Number of Edges: "), sg.Text(key='-NUM_EDGES-', size=(10, 1))],
               [sg.Text("Add an edge between nodes:")],
               [sg.Text("", size=(3, 1)), sg.Combo(list_nodes, default_value=0, key="-NODE1-"),
                sg.Text("", size=(3, 1)), sg.Combo(list_nodes, default_value=0, key="-NODE2-")],
               [sg.Text("", size=(40, 1), key='-ERROR2-')],
               [sg.Text("")],
               ]

layout2 = [[sg.Col(info_column), sg.Canvas(size=(graph_width, graph_height), key='figCanvas')],
           [sg.Exit(key="Exit"), sg.Button("Add Node", key="-ADD_NODE-"),
            sg.Button("Update Graph", key="-UPDATE-"), sg.Button("Finished")],
           [sg.Text("")],
           ]

# Create the second window
window2 = sg.Window('Min Swap Program', layout2, finalize=True)
window2.move_to_center()

# Update the second window
window2["-NUM_VAR-"].update(num_nodes)
window2["-NUM_EDGES-"].update(num_edges)

# Draws the initial figure to the window
fca = gui_func.drawToWindow(window2, QUBO_Graph, 'figCanvas')

# Event Loop to process "events"
while True:
    event, values = window2.read()
    if event in (sg.WIN_CLOSED, "Exit"):
        window2.close()
        sys.exit()

    if event == "-ADD_NODE-":
        if values["-NODE1-"] == values["-NODE2-"]:
            window2["-ERROR2-"].update("Self loops are not allowed")
        else:
            window2["-ERROR2-"].update("")
            QUBO_Graph.add_edge(values["-NODE1-"], values["-NODE2-"])

            num_edges += 1
            window2["-NUM_EDGES-"].update(num_edges)

    if event == "-UPDATE-":
        fca = gui_func.updateFigure(fca, window2, QUBO_Graph, 'figCanvas')

    if event == "Finished":
        break

# Can put this after the graph mapping if that takes a while
# Just pop up a message saying that it's mapping
window2.close()

"""
Data Processing for the Third Window:
    Color the graph
"""

QUBO_Graph = graph_func.color_graph(QUBO_Graph)

# Graph info
# color: the color of the node, gives info on the degree of the node
# pos: position of the node for graphing purposes only
# placed: whether or not it has been put on the qubit lattice
# tail_start: whether it starts an end tail
# tail_end: whether it ends an end tail
# embedded: the number of the node on the lattice it is embedded at

"""
Creating the Qubit Graph
"""

lattice_Graph = graph_func.import_lattice()

# Graph info
# color: the color of the node
# pos: position of the node for graphing purposes only
# qubit: the number of the node of the QUBO graph that has been
#        placed at that node
# size: the size of the dot, for graphing purposes only
# color: the color of the node, for graphing purposes only

"""
Mapping the QUBO to the lattice:
    This is where the mapping algorithm is applied
"""

# Remeber, everything on the HH lattice has degree 3 when fully connected
# 1. Place the first qubit
# 2. Find a neighbor that is untaken and place the next qubit from among
#       those among the first one's neighbors
# 3. Repeat 2 until finished
# 4. Place end tails at the closest untaken node to their attachment point

# 1. Place non-edge tail qubits

# Places the first qubit
cand_qubits = [x for x, node in QUBO_Graph.nodes(data=True) if node['color'] == 'y']

rand_node = random.choices(cand_qubits, k=1)[0]

# Modifies the info stored in the nodes
lattice_Graph.nodes[0]['qubit'] = rand_node
lattice_Graph.nodes[0]['color'] = QUBO_Graph.nodes[rand_node]['color']
lattice_Graph.nodes[0]['size'] = 300

# Modifies the info stored in the nodes
QUBO_Graph.nodes[rand_node]['placed'] = True
QUBO_Graph.nodes[rand_node]['embedded'] = 0

prev_node = rand_node

# Places the rest of the qubits
for i in range(len([x for x, node in QUBO_Graph.nodes(data=True) if node['placed'] is False])):
    cand_qubits = [x for x, node in QUBO_Graph.nodes(data=True) if (x in nx.neighbors(QUBO_Graph, prev_node) and node['placed'] is False)]

    # If all the neighbors of the previous node have been placed, then randomly
    # choose from unplaced qubits
    if cand_qubits == []:
        cand_qubits = [x for x, node in QUBO_Graph.nodes(data=True) if node['placed'] is False]

    # print(cand_qubits)

    rand_node = random.choices(cand_qubits, k=1)[0]

    # i+1 because the first node is already taken
    lattice_Graph.nodes[i + 1]['qubit'] = rand_node
    lattice_Graph.nodes[i + 1]['color'] = QUBO_Graph.nodes[rand_node]['color']
    lattice_Graph.nodes[i + 1]['size'] = 300

    QUBO_Graph.nodes[rand_node]['placed'] = True
    QUBO_Graph.nodes[rand_node]['embedded'] = i + 1

    prev_node = rand_node

# 2. Place green qubits
for start_node in [x for x, node in QUBO_Graph.nodes(data=True) if node['tail_start'] is True]:
    #print(f"The next green node to be placed is: {start_node}")

    # Gets the qubit that connects the tail to the main graph
    connecting_qubit = [x for x in nx.neighbors(QUBO_Graph, start_node) if QUBO_Graph.degree[x] > 2][0]
    #print(f"The qubit it is connected to is: {connecting_qubit}")
    while True:

        # Checks if there is a place to put the next green qubit
        for placement_spot in nx.neighbors(lattice_Graph, QUBO_Graph.nodes[connecting_qubit]['embedded']):

            # If no qubit, place the node
            if lattice_Graph.nodes[placement_spot]['qubit'] == -1:

                lattice_Graph.nodes[placement_spot]['qubit'] = start_node
                lattice_Graph.nodes[placement_spot]['color'] = QUBO_Graph.nodes[start_node]['color']
                lattice_Graph.nodes[placement_spot]['size'] = 300

                QUBO_Graph.nodes[start_node]['placed'] = True
                QUBO_Graph.nodes[start_node]['embedded'] = placement_spot
                print(f"Qubit {start_node} was placed at {placement_spot}")
                break

        # If the green node that was placed has a degree of 0, then the chain is finished
        if QUBO_Graph.degree(start_node) == 1:
            #print(f"This chain has ended, and the connecting node was embedded at {QUBO_Graph.nodes[connecting_qubit]['embedded']}")
            break
        else:
            # The placed qubit now connects the chain
            connecting_qubit = start_node

            # The qubit to be placed in the next one in line
            start_node = [x for x in nx.neighbors(QUBO_Graph, connecting_qubit) if QUBO_Graph.nodes[x]['embedded'] == -1][0]

            #print(f"Now, we will connect qubit {start_node} to qubit {connecting_qubit}")

"""
Third Window:
    Actually run the min swap alorgithm
"""

run_time_column = [[sg.Text("Number of Nodes: "), sg.Text(key='-NUM_VAR2-', size=(10, 1))],
                   [sg.Text("Number of Edges: "), sg.Text(key='-NUM_EDGES2-', size=(10, 1))],
                   [sg.Text("", size=(27, 1))],
                   ]

extra_column = [[sg.Text("", size=(27, 1))],
                ]

layout3 = [[sg.Col(run_time_column), sg.Canvas(size=(graph_width, graph_height), key='figCanvas2')],
           [sg.Col(extra_column), sg.Canvas(size=(graph_width, graph_height), key='figCanvas3')],
           [sg.Exit(key="Exit")],
           [sg.Text("")],
           ]

# Create the second window
window3 = sg.Window('Min Swap Program', layout3, finalize=True)
window3.move_to_center()

# Update the third window
window3["-NUM_VAR2-"].update(num_nodes)
window3["-NUM_EDGES2-"].update(num_edges)

# Draws the initial QUBO graph to the window
fca_qubo = gui_func.drawToWindow(window3, QUBO_Graph, 'figCanvas2')

# Draws the HH graph to the window
fca_lattice = gui_func.drawLatticeToWindow(window3, lattice_Graph, 'figCanvas3')

# Initialize the qubit lattice here

# Event Loop to process "events"
while True:
    event, values = window3.read()
    if event in (sg.WIN_CLOSED, "Exit"):
        break

window3.close()
sys.exit()
