#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed June 7th

@author: sambringman
"""

import matplotlib as mat
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg

mat.use("TKAgg")



def draw_figure(canvas, figure):
    if not hasattr(draw_figure, 'canvas_packed'):
        draw_figure.canvas_packed = {}
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    widget = figure_canvas_agg.get_tk_widget()
    if widget not in draw_figure.canvas_packed:
        draw_figure.canvas_packed[widget] = figure
        widget.pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


def delete_figure_agg(figure_agg):
    figure_agg.get_tk_widget().forget()
    try:
        draw_figure.canvas_packed.pop(figure_agg.get_tk_widget())
    except Exception as e:
        print(f'Error removing {figure_agg} from list', e)
    plt.close('all')


def set_scale(scale):

    root = sg.tk.Tk()
    root.tk.call('tk', 'scaling', scale)
    root.destroy()


# Function to make the plot that will be drawn to the window
def makePlot(graph):

    # Checks if the graph has a color attibute or not
    try:
        color_array = list(graph.nodes[i]['color'] for i in graph.nodes())
        edge_array = list(graph.edges[i]['color'] for i in graph.edges())

    except KeyError:
        color_array = ['b' for i in graph.nodes]
        edge_array = ['k' for i in graph.edges]

    plt.clf()

    # Make and show plot
    fig = plt.figure('QUBO', figsize=(4, 3.5))
    #print(fig.dpi/75)
    set_scale(fig.dpi/75)
    axQUBO = plt.axes(facecolor='w')
    axQUBO.set_axis_off()
    nx.draw_networkx(graph, pos=nx.circular_layout(graph), node_color=color_array, edge_color=edge_array)

    return fig


# Function to make the qubit lattice plot
def makeLatticePlot(graph):

    # The lattice graph should always be colored by the time this is called
    color_array = list(graph.nodes[i]['color'] for i in graph.nodes())
    size_array = list(graph.nodes[i]['size'] for i in graph.nodes())
    labels = {i: graph.nodes[i]['qubit'] for i in graph.nodes()}

    # Make and show plot
    # This plot has a number to differentiate from the QUBO graph
    fig = plt.figure('lattice', figsize=(4, 3.5))
    set_scale(fig.dpi/75)

    plt.clf()

    axLat = plt.axes(facecolor='w')
    axLat.set_axis_off()

    # Draw HH lattice
    nx.draw_networkx(graph, pos=graph.nodes.data('pos'), node_color=color_array, node_size=size_array, labels=labels)

    return fig

def makeSwapHist(swaps):

    fig = plt.figure('hist', figsize=(4, 3.5))
    set_scale(fig.dpi/75)

    plt.clf()
    plt.title("Swaps Required to Solve the QUBO")
    plt.xlabel("# of Swaps")
    plt.ylabel("Frequency")

    plt.hist(swaps, bins=range(min(swaps), max(swaps)+2), align='left', rwidth=0.8)

    return fig


"""
Other graph makers
"""

def init_entangles_v_swap_num(init_entangles, swap_num):

    fig = plt.figure('evs', figsize=(4, 3.5))
    set_scale(fig.dpi/75)

    plt.title("Initial Entanglements v. Swap Number")
    plt.xlabel("Initial # of Entangles")
    plt.ylabel("# of Swaps")

    plt.scatter(init_entangles, swap_num)

    return fig