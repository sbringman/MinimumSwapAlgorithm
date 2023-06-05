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
import sys

"""
Functions
"""
# Function to make the plot that will be drawn to the window


def makePlot(graph):

    color_array = list(graph.nodes[i]['color'] for i in range(num_nodes))

    plt.clf()
    plt.cla()

    # Make and show plot
    fig = plt.figure()
    ax = plt.axes()
    ax.set_axis_off()
    nx.draw_networkx(graph, pos=nx.circular_layout(graph), with_labels=True, node_color=color_array)

    return fig

# Function that draws the figure for the window


def drawFigure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

# Function that puts the figure on the window


def drawToWindow(window, graph):

    figure = makePlot(graph)

    fca = drawFigure(window['figCanvas'].TKCanvas, figure)

    return fca

# Function that updates the figure in the window


def updateFigure(fca, window, graph):
    fca.get_tk_widget().forget()

    fca = drawToWindow(window, graph)

    return fca


"""
Variables
"""
font = ("Helvetica", 17)
sg.set_options(font=font)

title_font = 'Courier 20'

sg.theme('DarkTeal7')   # Add a little color to your windows
# All the stuff inside your window. This is the PSG magic code compactor...
layout = [[sg.Text('Welcome to the Minimum Swap Algorithm Interface!', font=title_font, size=(45, 3))],
          [sg.Text('How many variables in your QUBO?', size=(28, 1)), sg.InputText(key='-INPUT-')],
          [sg.Text("", size=(40, 1), key='-ERROR-')],
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

        except ValueError:
            window["-ERROR-"].update("Invalid input, please enter a number")

window.close()

"""
Data Processing the User Input
"""
num_nodes = int(num_nodes)
list_nodes = list(range(0, num_nodes))


QUBO_Graph = nx.Graph()
for node in list_nodes:
    # The label part is currently broken
    QUBO_Graph.add_node(node, color='b')

# print(list(QUBO_Graph.nodes[i]['color'] for i in range(num_nodes)))

"""
Second Window:
    Putting in the edges
"""

info_column = [[sg.Text("Number of Nodes: "), sg.Text(key='-NUM_VAR-', size=(10, 1))],
               [sg.Text("Add an edge between nodes:")],
               [sg.Text("", size=(3, 1)), sg.Combo(list_nodes, default_value=0, key="-NODE1-"),
                sg.Text("", size=(3, 1)), sg.Combo(list_nodes, default_value=0, key="-NODE2-")],
               [sg.Text("", size=(40, 1), key='-ERROR2-')],
               [sg.Text("")],
               ]

layout2 = [[sg.Col(info_column), sg.Canvas(size=(300, 300), key='figCanvas')],
           [sg.Exit(key="Exit"), sg.Button("Add Node", key="-ADD_NODE-"), sg.Button("Update Graph", key="-UPDATE-")],
           [sg.Text("")],
           ]

# Create the second window
window2 = sg.Window('Min Swap Program', layout2, finalize=True)

# Update the second window
window2["-NUM_VAR-"].update(num_nodes)

# Draws the initial figure to the window
fca = drawToWindow(window2, QUBO_Graph)

# Event Loop to process "events"
while True:
    event, values = window2.read()
    if event in (sg.WIN_CLOSED, "Exit"):
        break

    if event == "-ADD_NODE-":
        if values["-NODE1-"] == values["-NODE2-"]:
            window["-ERROR-"].update("Self loops are not allowed in this graph")
        else:
            window["-ERROR-"].update("")
            QUBO_Graph.add_edge(values["-NODE1-"], values["-NODE2-"])

            # First, find max number of nodes for red coloring
            max_degree = max(QUBO_Graph.degree())

        for i in QUBO_Graph.nodes:

            # Blue means unconnected
            if QUBO_Graph.degree[i] == 0:
                QUBO_Graph.nodes[i]['color'] = 'b'

            # Green means either an end node or a node with degree two
            # connected to an end node
            elif QUBO_Graph.degree[i] == 1:
                QUBO_Graph.nodes[i]['color'] = 'g'

            # Checks if the new edge connects an end node to a node of
            # degree 2
            elif QUBO_Graph.degree[i] == 2:
                QUBO_Graph.nodes[i]['color'] = 'y'

                for node in QUBO_Graph.neighbors(i):
                    if QUBO_Graph.nodes[node]['color'] == 'g':
                        QUBO_Graph.nodes[i]['color'] = 'g'

                # Has more than one node and is not connected back to an end node
            elif QUBO_Graph.degree[i] == max_degree:
                QUBO_Graph.nodes[i]['color'] = 'r'

            else:
                QUBO_Graph.nodes[i]['color'] = 'y'

    if event == "-UPDATE-":
        fca = updateFigure(fca, window2, QUBO_Graph)


# Exits once the user closes the window
window2.close()
sys.exit()
