#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  17

@author: sambringman
"""

#import networkx as nx
import PySimpleGUI as sg
import numpy as np
import sys
import time
#import cProfile

import gui_functions as gui_func
import graph_functions as graph_func
import test_speed_funcs as sgf

"""
This is the code that will run the minimum swap algorithm a sufficient number of times
 to find the best path

 Speed Ups:
    Rework the swapping part so that it randomly picks a swap to do from all the shortest paths 
        instead of the first one it finds
    That way, instead of testing thousands of random graphs, find a good looking graph and test it 
        50 times. Then find another good looking graph and test it fifty times, et cetera
    If there is a strong correlation between initial entanglements between non-green nodes and 
        minimum swap paths for the graph, it might be faster to check if the graph looks favorable
        before putting on the green nodes
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

QUBO_Graph, num_nodes, num_edges, list_nodes = sgf.make_qubo_graph(num_nodes, values["file"])

QUBO_Graph = sgf.find_greens(QUBO_Graph)

# Graph info
# green: whether or not it is a green node
# placed: whether or not it has been put on the qubit lattice
# tail_start: whether it starts an end tail
# tail_end: whether it ends an end tail
# embedded: the number of the node on the lattice it is embedded at

lattice_Graph = sgf.import_lattice()

# Graph info
# qubit: the number of the node of the QUBO graph that has been
#        placed at that node

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
            [sg.Text("# of Iterations: "), sg.InputText('1', size=(10, 1), key='-NUM_ITER-')],
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
        #QUBO_Graph = graph_func.color_graph(QUBO_Graph)

        gui_func.delete_figure_agg(figure_agg2)
        figure2 = gui_func.makePlot(QUBO_Graph)
        figure_agg2 = gui_func.draw_figure(window2['figCanvas'].TKCanvas, figure2)

        #fca = gui_func.updateFigure(fca, window2, QUBO_Graph, 'figCanvas')

    if event == "Finished":

        # Check for the validity of the iterations value
        if values['-NUM_ITER-']:

            iterations = values['-NUM_ITER-']

            try:
                int(iterations) + 1

                if int(iterations) > 0:
                    # Now, everything is checked

                    iterations = int(iterations)
                    break
                else:
                    window2["-ERROR2-"].update("# of iterations must be a positive integer")
            
            except:
                window2["-ERROR2-"].update("# of iterations must be an integer")

window2.close()

# Here, put the loading window

start_time = time.perf_counter()

best_swap_list, list_of_swap_nums, best_lattice_nodes, best_qubo_embed, init_entangles, iterations = sgf.iterate_through(lattice_Graph, QUBO_Graph, iterations)
#cProfile.run('best_swap_list, list_of_swap_nums, best_lattice_nodes = graph_func.iterate_through(lattice_Graph, QUBO_Graph, iterations)')
#print(best_lattice_nodes)
#print(best_qubo_embed)
# Needs to also print out the original lattice placement
print(f"The best path was {best_swap_list}")

# Clean up calculations
best_swap = len(best_swap_list)
ave_swaps = round(np.average(np.array(list_of_swap_nums)), 3)

end_time = time.perf_counter()
run_time = round(end_time - start_time, ndigits=2)

#print("\n\n\n")

lattice_Graph = sgf.reconstruct_lattice(best_lattice_nodes, lattice_Graph)
QUBO_Graph = sgf.reconstruct_qubo(best_qubo_embed, QUBO_Graph)

#print(best_lattice.nodes(data=True))

# Add in the graph colors
QUBO_Graph = graph_func.color_graph(QUBO_Graph)
lattice_Graph = graph_func.color_lattice(lattice_Graph, QUBO_Graph)

"""
Now, display all the final information
"""

run_time_column = [[sg.Text("# of Qubits: "), sg.Text(key='-NUM_VAR2-', size=(10, 1))],
                [sg.Text("# of Entanglements Needed: "), sg.Text(key='-NUM_EDGES2-', size=(10, 1))],
                [sg.Text("Average # of Swaps: "), sg.Text('0', key='-AVE_SWAPS-', size=(10, 1))],
                [sg.Text("Lowest # of Swaps: "), sg.Text('0', key='-BEST_SWAP-', size=(10, 1))],
                [sg.Text("Iterations: "), sg.Text('0', key='-ITER-', size=(10, 1))],
                [sg.Text("Run Time: "), sg.Text('0', key='-RUN_TIME-', size=(10, 1))],
                [sg.Text("Run Time per Trial: "), sg.Text('0', key='-RUN_TIME_TRIAL-', size=(10, 1))],
                [sg.Text("", size=(35, 1))],
                ]

route_column = [[sg.Text("Best Path:", size=(35, 1))],
                [sg.Text("", key='-ROUTE-', size=(35, 5))],
            ]

layout3 = [[sg.Col(run_time_column), sg.Canvas(size=(graph_width, graph_height), key='figCanvas2'), sg.Canvas(size=(graph_width, graph_height), key='figCanvas3')],
        [sg.Col(route_column), sg.Canvas(size=(graph_width, graph_height), key='figCanvas4'), sg.Canvas(size=(graph_width, graph_height), key='figCanvas5')],
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
window3["-ITER-"].update(iterations)
window3["-RUN_TIME-"].update(f"{run_time} s")
window3["-RUN_TIME_TRIAL-"].update(f"{round((run_time / iterations) * 1000, ndigits=3)} ms")

# Draws the initial QUBO graph to the window
figure_q = gui_func.makePlot(QUBO_Graph)
figure_agg_q = gui_func.draw_figure(window3['figCanvas2'].TKCanvas, figure_q)

# Draw the lattice graph to the window
figure_l = gui_func.makeLatticePlot(lattice_Graph)
figure_agg_l = gui_func.draw_figure(window3['figCanvas3'].TKCanvas, figure_l)

# Draw the histogram plot to the window
figure_hist = gui_func.makeSwapHist(list_of_swap_nums)
figure_agg_hist = gui_func.draw_figure(window3['figCanvas4'].TKCanvas, figure_hist)

# Draw the histogram plot to the window
init_entangle_fig = gui_func.init_entangles_v_swap_num(init_entangles, list_of_swap_nums)
figure_agg_hist = gui_func.draw_figure(window3['figCanvas5'].TKCanvas, init_entangle_fig)

window3.refresh()
window3.move_to_center()

# Event Loop to process "events"
while True:
    event, values = window3.read()
    if event in (sg.WIN_CLOSED, "Exit"):
        break
            
window3.close()
sys.exit()
