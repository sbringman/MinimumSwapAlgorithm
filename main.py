#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  3 16:18:25 2023

@author: sambringman
"""

import PySimpleGUI as sg
import sys

# Import from my function program
import graph_functions as graph_func
import gui_functions as gui_func

"""
To Do:
    Start swapping
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

lattice_Graph, QUBO_Graph = graph_func.place_initial_qubits(lattice_Graph, QUBO_Graph)
lattice_Graph, QUBO_Graph = graph_func.place_green_qubits(lattice_Graph, QUBO_Graph)

# entangles is a list of all the qubits that need to be entangled.
# It is a list of tuples
entangles = list(QUBO_Graph.edges)
num_swaps = 0

# Perform initial entanglements
lattice_Graph, QUBO_Graph, num_entangles = graph_func.get_current_entangles(lattice_Graph, QUBO_Graph, entangles)

"""
Third Window:
    Actually run the min swap alorgithm
"""

run_time_column = [[sg.Text("# of Qubits: "), sg.Text(key='-NUM_VAR2-', size=(10, 1))],
                   [sg.Text("# of Entanglements Needed: "), sg.Text(key='-NUM_EDGES2-', size=(10, 1))],
                   [sg.Text("# of Entanglements Performed: "), sg.Text('0', key='-NUM_ENT-', size=(10, 1))],
                   [sg.Text("# of Swaps: "), sg.Text('0', key='-NUM_SWAPS-', size=(10, 1))],
                   [sg.Text("", size=(27, 1))],
                   ]

extra_column = [[sg.Text("", size=(27, 1))],
                ]

layout3 = [[sg.Col(run_time_column), sg.Canvas(size=(graph_width, graph_height), key='figCanvas2'), sg.Canvas(size=(graph_width, graph_height), key='figCanvas3')],
           [sg.Button("Next Swap", key="-SWAP-")], [sg.Exit(key="Exit")],
           [sg.Text("")],
           ]

# Create the second window
window3 = sg.Window('Min Swap Program', layout3, finalize=True, size=(1200, 400), margins=(0, 0))
window3.move_to_center()

# Update the third window
window3["-NUM_VAR2-"].update(num_nodes)
window3["-NUM_EDGES2-"].update(num_edges)

# Draws the initial QUBO graph to the window
figure_q = gui_func.makePlot(QUBO_Graph)
figure_agg_q = gui_func.draw_figure(window3['figCanvas2'].TKCanvas, figure_q)

# Draws the HH graph to the window
figure_l = gui_func.makeLatticePlot(lattice_Graph)
figure_agg_l = gui_func.draw_figure(window3['figCanvas3'].TKCanvas, figure_l)

window3.refresh()
window3.move_to_center()

window3["-NUM_ENT-"].update(num_entangles)

# Event Loop to process "events"
while True:
    event, values = window3.read()
    if event in (sg.WIN_CLOSED, "Exit"):
        break

    elif event == "-SWAP-":

        # Do the swaps
        lattice_Graph, new_swaps = graph_func.perform_next_swap(lattice_Graph)

        # Update the window
        num_swaps += new_swaps
        window3["-NUM_SWAPS-"].update(num_swaps)

        # And the graphs
        gui_func.delete_figure_agg(figure_agg_q)
        figure_q = gui_func.makePlot(QUBO_Graph)
        figure_agg_q = gui_func.draw_figure(window3['figCanvas2'].TKCanvas, figure_q)

        gui_func.delete_figure_agg(figure_agg_l)
        figure_l = gui_func.makeLatticePlot(lattice_Graph)
        figure_agg_l = gui_func.draw_figure(window3['figCanvas3'].TKCanvas, figure_l)

window3.close()
sys.exit()
