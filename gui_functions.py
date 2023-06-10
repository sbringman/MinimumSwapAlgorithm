#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed June 7th

@author: sambringman
"""

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg


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

    color_array = list(graph.nodes[i]['color'] for i in graph.nodes())

    plt.clf()

    # Make and show plot
    fig = plt.figure('QUBO', figsize=(4, 3.5))
    #print(fig.dpi/75)
    set_scale(fig.dpi/75)
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
    fig = plt.figure('lattice', figsize=(4, 3.5))
    set_scale(fig.dpi/75)

    plt.clf()

    axLat = plt.axes(facecolor='w')
    axLat.set_axis_off()

    # Draw HH lattice
    nx.draw_networkx(graph, pos=graph.nodes.data('pos'), node_color=color_array, node_size=size_array, labels=labels)

    return fig

