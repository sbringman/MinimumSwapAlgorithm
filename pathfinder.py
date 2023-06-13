#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  3 16:18:25 2023

@author: sambringman
"""

import networkx as nx
import PySimpleGUI as sg
import numpy as np
import sys
import copy

import gui_functions as gui_func
import graph_functions as graph_func

"""
This is the code that will run the minimum swap algorithm 100 times to find a short path
"""

iterations = 10000

# Sets the font options
font = ("Helvetica", 17)
sg.set_options(font=font)
title_font = 'Courier 20'

# Creates a dummy window to try and standardize window sizes
# across different editors and computers
dummy_window = sg.Window("dummy", [[]], finalize=True)

base_px = sg.tkinter.font.Font().measure('A')
f_px = sg.tkinter.font.Font(font=font).measure('A')

graph_width = base_px * 10
graph_height = base_px * 67

dummy_window.close()

# Adds color to the windows
sg.theme('DarkTeal7')

# Layout of the first window
layout = [[sg.Text('Welcome to the Minimum Swap Algorithm Interface!', font=title_font, size=(45, 3))],
          [sg.Text('How many variables in your QUBO?', size=(28, 1)), sg.InputText('8', key='-INPUT-')],
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
window = sg.Window('Min Swap Program', layout, finalize=True, size=(650, 300))
window.refresh()
window.move_to_center()

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

QUBO_Graph, num_nodes, num_edges, list_nodes = graph_func.make_qubo_graph(num_nodes, values["file"])

QUBO_Graph = graph_func.color_graph(QUBO_Graph)

# Graph info
# color: the color of the node, gives info on the degree of the node
# pos: position of the node for graphing purposes only
# placed: whether or not it has been put on the qubit lattice
# tail_start: whether it starts an end tail
# tail_end: whether it ends an end tail
# embedded: the number of the node on the lattice it is embedded at

lattice_Graph = graph_func.import_lattice()

# Graph info
# color: the color of the node
# pos: position of the node for graphing purposes only
# qubit: the number of the node of the QUBO graph that has been
#        placed at that node
# size: the size of the dot, for graphing purposes only
# color: the color of the node, for graphing purposes only

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
           [sg.Exit(key="Exit"), sg.Button("Add Edge", key="-ADD_NODE-"),
            sg.Button("Update Graph", key="-UPDATE-"), sg.Button("Finished")],
           [sg.Text("")],
           ]

# Create the second window
window2 = sg.Window('Min Swap Program', layout2, finalize=True, size=(950, 400), margins=(0, 0))
window2.refresh()
window2.move_to_center()

# Update the second window
window2["-NUM_VAR-"].update(num_nodes)
window2["-NUM_EDGES-"].update(num_edges)

# Draws the initial figure to the window
figure2 = gui_func.makePlot(QUBO_Graph)
figure_agg2 = gui_func.draw_figure(window2['figCanvas'].TKCanvas, figure2)

window2.refresh()
window2.move_to_center()

# Event Loop to process "events"
while True:
    event, values = window2.read()
    if event in (sg.WIN_CLOSED, "Exit"):
        window2.close()
        sys.exit()

    if event == "-ADD_NODE-":
        if values["-NODE1-"] == values["-NODE2-"]:
            window2["-ERROR2-"].update("Self loops are not allowed")

        elif (values["-NODE1-"], values["-NODE2-"]) in QUBO_Graph.edges():
            window2["-ERROR2-"].update("That edge already exists in the graph")

        else:
            window2["-ERROR2-"].update("")
            QUBO_Graph.add_edge(values["-NODE1-"], values["-NODE2-"])

            num_edges += 1
            window2["-NUM_EDGES-"].update(num_edges)

    if event == "-UPDATE-":
        QUBO_Graph = graph_func.color_graph(QUBO_Graph)

        gui_func.delete_figure_agg(figure_agg2)
        figure2 = gui_func.makePlot(QUBO_Graph)
        figure_agg2 = gui_func.draw_figure(window2['figCanvas'].TKCanvas, figure2)

        #fca = gui_func.updateFigure(fca, window2, QUBO_Graph, 'figCanvas')

    if event == "Finished":
        break

window2.close()

# Here, put the loading window

# First thing to do is save all the original variables
original_QUBO = copy.deepcopy(QUBO_Graph)
original_lattice = copy.deepcopy(lattice_Graph)

# Then, get the variables for the process
list_of_swap_nums = []
best_swap_list = [i for i in range(1000)]

for i in range(iterations):

    # Refresh everything
    QUBO_Graph = copy.deepcopy(original_QUBO)
    lattice_Graph = copy.deepcopy(original_lattice)
    solved = False
    swaps = 0

    # Map to the lattice
    lattice_Graph, QUBO_Graph = graph_func.place_initial_qubits(lattice_Graph, QUBO_Graph)
    lattice_Graph, QUBO_Graph = graph_func.place_green_qubits(lattice_Graph, QUBO_Graph)

    # We have to save this for when it finds the best path
    start_lattice = copy.deepcopy(lattice_Graph)

    # Do initial entangling
    # entangles is a list of all the qubits that need to be entangled.
    # It is a list of tuples
    entangles_to_do = list(QUBO_Graph.edges)
    num_swaps = 0
    # num_entangles does nothing here
    swap_list = []

    lattice_Graph, QUBO_Graph, entangles_to_do, num_entangles = graph_func.get_current_entangles(lattice_Graph, QUBO_Graph, entangles_to_do)

    while not solved:
        # Do the swaps
        lattice_Graph, new_swaps, new_swap_list, entangles_to_do = graph_func.perform_next_swap(lattice_Graph, QUBO_Graph, entangles_to_do)
        swaps += new_swaps
        swap_list += new_swap_list

        # Get the current entanglements
        lattice_Graph, QUBO_Graph, entangles_to_do, new_entangles = graph_func.get_current_entangles(lattice_Graph, QUBO_Graph, entangles_to_do)

        if len(entangles_to_do) == 0:
            solved = True
            #print(f"Finished solving attempt {i + 1} - {swaps} swaps")

            list_of_swap_nums.append(swaps)

            if len(swap_list) < len(best_swap_list):
                best_swap_list = swap_list
                best_lattice = copy.deepcopy(start_lattice)

                print(f"A new best swap path was found, with a length of {len(swap_list)}")

# Needs to also print out the original lattice placement
print(f"The best path was {best_swap_list}")

# Clean up calculations
best_swap = min(list_of_swap_nums)
ave_swaps = np.average(np.array(list_of_swap_nums))

"""
Now, display all the final information
"""

run_time_column = [[sg.Text("# of Qubits: "), sg.Text(key='-NUM_VAR2-', size=(10, 1))],
                   [sg.Text("# of Entanglements Needed: "), sg.Text(key='-NUM_EDGES2-', size=(10, 1))],
                   [sg.Text("Average # of Swaps: "), sg.Text('0', key='-AVE_SWAPS-', size=(10, 1))],
                   [sg.Text("Lowest # of Swaps: "), sg.Text('0', key='-BEST_SWAP-', size=(10, 1))],
                   [sg.Text("", size=(35, 1))],
                   ]

route_column = [[sg.Text("Best Path:", size=(35, 1))],
                [sg.Text("", key='-ROUTE-', size=(35, 5))],
               ]

layout3 = [[sg.Col(run_time_column), sg.Canvas(size=(graph_width, graph_height), key='figCanvas2'), sg.Canvas(size=(graph_width, graph_height), key='figCanvas3')],
           [sg.Col(route_column), sg.Canvas(size=(graph_width, graph_height), key='figCanvas4')],
           [sg.Exit(key="Exit")],
           [sg.Text("")],
           ]

# Create the second window
window3 = sg.Window('Min Swap Program', layout3, finalize=True, size=(1200, 780), margins=(0, 0))
window3.move_to_center()

# Update the third window
window3["-NUM_VAR2-"].update(num_nodes)
window3["-NUM_EDGES2-"].update(num_edges)
window3["-AVE_SWAPS-"].update(ave_swaps)
window3["-BEST_SWAP-"].update(best_swap)
window3["-ROUTE-"].update(str(best_swap_list))

# Draws the initial QUBO graph to the window
figure_q = gui_func.makePlot(QUBO_Graph)
figure_agg_q = gui_func.draw_figure(window3['figCanvas2'].TKCanvas, figure_q)

# Draw the histogram plot to the window
figure_l = gui_func.makeLatticePlot(best_lattice)
figure_agg_l = gui_func.draw_figure(window3['figCanvas3'].TKCanvas, figure_l)

# Draw the histogram plot to the window
figure_hist = gui_func.makeSwapHist(list_of_swap_nums)
figure_agg_hist = gui_func.draw_figure(window3['figCanvas4'].TKCanvas, figure_hist)

window3.refresh()
window3.move_to_center()

# Event Loop to process "events"
while True:
    event, values = window3.read()
    if event in (sg.WIN_CLOSED, "Exit"):
        break
            
window3.close()
sys.exit()
