#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed June 7th

@author: sambringman
"""

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Function to make the plot that will be drawn to the window
def makePlot(graph):

    color_array = list(graph.nodes[i]['color'] for i in graph.nodes())

    plt.clf()

    # Make and show plot
    fig = plt.figure('QUBO')
    axQUBO = plt.axes(facecolor='w')
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

    axLat = plt.axes(facecolor='w')
    axLat.set_axis_off()

    # Draw HH lattice
    nx.draw_networkx(graph, pos=graph.nodes.data('pos'), node_color=color_array, node_size=size_array, labels=labels)

    return fig


# Function that draws the figure for the window
def drawFigure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=True)
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