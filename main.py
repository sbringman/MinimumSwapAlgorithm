#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  3 16:18:25 2023

@author: sambringman
"""

import PySimpleGUI as sg
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from pandas import read_csv
import random
import sys

"""
To Do:
    Place the full end tails
    Place end tails if the connecting node has no open neighbors
    Start swapping
"""

"""
Functions
"""


# Function to make the plot that will be drawn to the window
def makePlot(graph):

    color_array = list(graph.nodes[i]['color'] for i in range(num_nodes))

    plt.clf()
    plt.cla()

    # Make and show plot
    fig = plt.figure('QUBO')
    axQUBO = plt.axes(label='QUBO')
    axQUBO.set_axis_off()
    nx.draw_networkx(graph, pos=nx.circular_layout(graph), node_color=color_array)

    return fig


# Function to make the qubit lattice plot
def makeLatticePlot(graph):

    color_array = list(graph.nodes[i]['color'] for i in graph.nodes())
    size_array = list(graph.nodes[i]['size'] for i in graph.nodes())
    labels = {i: graph.nodes[i]['qubit'] for i in graph.nodes()}

    # Make and show plot
    # This plot has a number to differentiate from the QUBO graph
    fig = plt.figure('lattice')
    plt.clf()
    plt.cla()

    axLat = plt.axes(label='lattice')
    axLat.set_axis_off()

    # Draw HH lattice
    nx.draw_networkx(graph, pos=graph.nodes.data('pos'), node_color=color_array, node_size=size_array, labels=labels)

    return fig


# Function that draws the figure for the window
def drawFigure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


# Function that puts the figure on the window
def drawToWindow(window, graph, key):

    figure = makePlot(graph)

    fca = drawFigure(window[key].TKCanvas, figure)

    return fca


# Function that puts the HH plot on the window
def drawLatticeToWindow(window, graph, key):

    figure = makeLatticePlot(graph)

    fca = drawFigure(window[key].TKCanvas, figure)

    return fca


# Function that updates the figure in the window
def updateFigure(fca, window, graph, key):
    fca.get_tk_widget().forget()

    fca = drawToWindow(window, graph, key)

    return fca


"""
Variables
"""
HH_nodes_filepath = "./HH_Nodes.txt"
HH_edges_filepath = "./HH_Edges.txt"

font = ("Helvetica", 17)
sg.set_options(font=font)

title_font = 'Courier 20'

sg.theme('DarkTeal7')   # Add a little color to your windows
# All the stuff inside your window. This is the PSG magic code compactor...
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
    Transferring that info into a graphs
"""

# Create the Window
window = sg.Window('Min Swap Program', layout)

# Event Loop to process "events"
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Cancel'):
        window.close()
        sys.exit()

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

if values["file"] == "None":

    num_nodes = int(num_nodes)
    list_nodes = list(range(0, num_nodes))
    num_edges = 0

    QUBO_Graph = nx.Graph()
    for node in list_nodes:
        QUBO_Graph.add_node(node, color='b', pos=[0.2, 0.2], placed=False, tail_start=False, embedded=-1)

else:
    num_edges = 0
    num_nodes = int(num_nodes)
    list_nodes = list(range(0, num_nodes))

    # Generates the nodes
    QUBO_Graph = nx.Graph()
    for node in list_nodes:
        QUBO_Graph.add_node(node, color='b', pos=[0.2, 0.2], placed=False, tail_start=False, embedded=-1)

    QUBO_edges_info = read_csv(values["file"], skiprows=1)

    for index, row in QUBO_edges_info.iterrows():
        QUBO_Graph.add_edge(row['Node1'], row['Node2'])
        num_edges += 1

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

layout2 = [[sg.Col(info_column), sg.Canvas(size=(300, 200), key='figCanvas')],
           [sg.Exit(key="Exit"), sg.Button("Add Node", key="-ADD_NODE-"),
            sg.Button("Update Graph", key="-UPDATE-"), sg.Button("Finished")],
           [sg.Text("")],
           ]

# Create the second window
window2 = sg.Window('Min Swap Program', layout2, finalize=True)

# Update the second window
window2["-NUM_VAR-"].update(num_nodes)
window2["-NUM_EDGES-"].update(num_edges)

# Draws the initial figure to the window
fca = drawToWindow(window2, QUBO_Graph, 'figCanvas')

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
        fca = updateFigure(fca, window2, QUBO_Graph, 'figCanvas')

    if event == "Finished":
        break

# Can put this after the graph mapping if that takes a while
# Just pop up a message saying that it's mapping
window2.close()

"""
Data Processing for the Third Window:
    Color the graph
"""

# Green qubits count as placed, because they will be put on in specific
# spots at the end

# First, turn everything yellow
for node in QUBO_Graph.nodes:
    QUBO_Graph.nodes[node]['color'] = 'y'

# Second, find the end nodes and the end tails
for node in QUBO_Graph.nodes:
    # Blue means unconnected
    if QUBO_Graph.degree[node] == 0:
        QUBO_Graph.nodes[node]['color'] = 'b'

    # Upon finding an end node, trace it back until there's a node of degree
    # greater than 2
    elif QUBO_Graph.degree[node] == 1:
        QUBO_Graph.nodes[node]['color'] = 'g'
        QUBO_Graph.nodes[node]['placed'] = True

        cur_node = node
        prev_nodes = [node]
        in_tail = True
        while in_tail:

            # See if the next node in the trail is degree two
            for next_node in nx.neighbors(QUBO_Graph, cur_node):
                # print(f"Node #{cur_node}, Neighbor #{next_node}")

                # This is node from previously up the chain.
                # It's boring and we want to skip it so we go further
                # down the end tail chain
                if next_node in prev_nodes:
                    # print("Skipped")
                    continue

                elif QUBO_Graph.degree[next_node] == 2:
                    # print("Colored")
                    QUBO_Graph.nodes[next_node]['color'] = 'g'
                    QUBO_Graph.nodes[next_node]['placed'] = True
                    prev_nodes.append(next_node)
                    cur_node = next_node

                # Else break out of the loop, you've reached the end of the
                # tail
                else:
                    #print("End of chain")
                    QUBO_Graph.nodes[cur_node]['tail_start'] = True
                    in_tail = False

# Third, color the max degree nodes red
max_degree = max(QUBO_Graph.degree, key=lambda x: x[1])[1]

# If the max is less than 3, it doesn't matter because the entanglement
# is a chain
max_degree = max(max_degree, 3)

# Checks if it is the node with the max degree
for node in QUBO_Graph.nodes:

    if QUBO_Graph.degree[node] == max_degree:
        QUBO_Graph.nodes[node]['color'] = 'r'


"""
Creating the Qubit Graph:
    
"""

# This will just be a premade lattice with a certain number of qubits

# Instead of a Boolean, if the qubit variable of the node = -1, then the space
# is untaken

HH_node_info = read_csv(HH_nodes_filepath, skiprows=1)
HH_edges_info = read_csv(HH_edges_filepath, skiprows=1)

lattice_Graph = nx.Graph()

for index, row in HH_node_info.iterrows():

    lattice_Graph.add_node(index, pos=[row['x_coor'], row['y_coor']],
                           qubit=-1, size=100, color='k')

for index, row in HH_edges_info.iterrows():

    lattice_Graph.add_edge(row['Node1'] - 1, row['Node2'] - 1)

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

    # Gets the qubit that connects the tail to the main graph
    connecting_qubit = [x for x in nx.neighbors(QUBO_Graph, start_node) if QUBO_Graph.degree[x] > 2][0]

    for placement_spot in nx.neighbors(lattice_Graph, QUBO_Graph.nodes[connecting_qubit]['embedded']):

        # If no qubit, place the node
        if lattice_Graph.nodes[placement_spot]['qubit'] == -1:

            lattice_Graph.nodes[placement_spot]['qubit'] = start_node
            lattice_Graph.nodes[placement_spot]['color'] = QUBO_Graph.nodes[start_node]['color']
            lattice_Graph.nodes[placement_spot]['size'] = 300

            QUBO_Graph.nodes[start_node]['placed'] = True
            QUBO_Graph.nodes[start_node]['embedded'] = i

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

layout3 = [[sg.Col(run_time_column), sg.Canvas(size=(300, 200), key='figCanvas2')],
           [sg.Col(extra_column), sg.Canvas(size=(300, 200), key='figCanvas3')],
           [sg.Exit(key="Exit")],
           [sg.Text("")],
           ]

# Create the second window
window3 = sg.Window('Min Swap Program', layout3, finalize=True)

# Update the second window
window3["-NUM_VAR2-"].update(num_nodes)
window3["-NUM_EDGES2-"].update(num_edges)

# Draws the initial QUBO graph to the window
fca_qubo = drawToWindow(window3, QUBO_Graph, 'figCanvas2')

# Draws the HH graph to the window
fca_lattice = drawLatticeToWindow(window3, lattice_Graph, 'figCanvas3')

# Initialize the qubit lattice here

# Event Loop to process "events"
while True:
    event, values = window3.read()
    if event in (sg.WIN_CLOSED, "Exit"):
        break

window3.close()
sys.exit()
