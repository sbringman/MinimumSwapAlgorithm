#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 3

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
import speed_graph_functions as sgf

"""
This is the code that will run the minimum swap algorithm a sufficient number of times
 to find the best path

 Speed Ups:
    We need to leverage the fact that I can store the distance between every pair of points
        on the lattice easily. That won't change between QUBOs. Can I use this to pick out the
        best paths through the lattice?
    Right now, the distance adjustments function doesn't change the time required for the total run.
        It actually increases it a little I think, at least for a strike count of 50. However,
        it does recude the number of bad graphs per good graph from 26 to 10, which is a success.
        The next step will be to have it get better at reducing the distance. One way to do this
        might be to have it be able to move qubits to a different spot, instead of just swapping them.
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
window = sg.Window('Min Swap Program', layout, finalize=True, size=(650, 350))
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

        if values['-3REG-']:
            num_nodes = int(values['-REGNUM-'])

            try:
                test = range(num_nodes)

                if num_nodes > 0 and num_nodes % 2 == 0:
                    break
                elif num_nodes > 0 and num_nodes % 2 == 1:
                    window["-ERROR-"].update("Invalid input, please enter an even number")
                else:
                    window["-ERROR-"].update("Invalid input, please enter a valid number")

            except:
                window["-ERROR-"].update("Invalid input, please enter a number")
        
        else:
            num_nodes = int(values['-INPUT-'])

            try:
                test = range(num_nodes)

                if num_nodes > 0:
                    break
                else:
                    window["-ERROR-"].update("Invalid input, please enter a valid number")

            except:
                window["-ERROR-"].update("Invalid input, please enter a number")

if values['-3REG-']:
    # Make 3-regular graph
    QUBO_Graph, num_nodes, num_edges, list_nodes = sgf.make_3reg_graph(num_nodes)
else:
    # Make the QUBO graph
    QUBO_Graph, num_nodes, num_edges, list_nodes = sgf.make_qubo_graph(num_nodes, values["file"])

window.close()

"""
Data Processing the User Input
"""

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
            [sg.Text("# of Iterations: "), sg.InputText('12000', size=(10, 1), key='-NUM_ITER-')],
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

best_moves_list, best_moves_key, list_of_swap_nums, best_lattice_nodes, best_qubo_embed, iterations, graph_distance, ave_swap_list = sgf.iterate_through(lattice_Graph, QUBO_Graph, iterations)
#cProfile.run('best_moves_list, list_of_swap_nums, best_lattice_nodes = graph_func.iterate_through(lattice_Graph, QUBO_Graph, iterations)')
#print(best_lattice_nodes)
#print(best_qubo_embed)
# Needs to also print out the original lattice placement
#print(f"The best path was {best_moves_list}")
print("Best Move List:")
print(best_moves_list)
print("\nBest Move Key:")
print(best_moves_key)

# Clean up calculations
best_swap = len([key for key in best_moves_key if key == "s"])
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
                [sg.Text("", key='-ROUTE-', size=(35, 7))],
                [sg.Text("Best Path Key:", size=(35, 1))],
                [sg.Text("", key='-ROUTE_KEY-', size=(35, 5))],
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
window3["-ROUTE-"].update(str(best_moves_list))
window3["-ROUTE_KEY-"].update(str(best_moves_key))
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
#extra_fig = gui_func.graph_distance_v_ave_swaps(init_entangles, swap_num)
extra_fig = gui_func.graph_distance_v_ave_swaps(graph_distance, ave_swap_list)
figure_agg_hist = gui_func.draw_figure(window3['figCanvas5'].TKCanvas, extra_fig)

window3.refresh()
window3.move_to_center()

# Event Loop to process "events"
while True:
    event, values = window3.read()
    if event in (sg.WIN_CLOSED, "Exit"):
        break

window3.close()
sys.exit()
