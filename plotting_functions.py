#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed June 7th, 2023

@author: sambringman
"""

import matplotlib.pyplot as plt
import networkx as nx


# Function to make the plot that will be drawn to the window
def makeQUBOGraph(graph):

    # Checks if the graph has a color attibute or not
    try:
        color_array = list(graph.nodes[i]['color'] for i in graph.nodes())
        edge_array = list('k' for i in graph.edges())

    except KeyError:
        color_array = ['b' for i in graph.nodes]
        edge_array = ['k' for i in graph.edges]

    # Make and show plot
    fig = plt.figure('QUBO Graph', figsize=(4, 3.5))

    axLat = plt.axes(facecolor='w')
    axLat.set_axis_off()

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
    fig = plt.figure('Lattice Graph', figsize=(4, 3.5))

    axLat = plt.axes(facecolor='w')
    axLat.set_axis_off()

    # Draw lattice
    nx.draw_networkx(graph, pos=graph.nodes.data('pos'), node_color=color_array, node_size=size_array, labels=labels)

    return fig

def makeSwapHist(swaps):

    fig = plt.figure("Swaps Required to Complete Entanglement", figsize=(4, 3.5))

    plt.xlabel("# of Swaps")
    plt.ylabel("Frequency")

    plt.hist(swaps, bins=range(min(swaps), max(swaps)+2), align='left', rwidth=0.8)
    plt.tight_layout()

    return fig


"""
Other graph makers
"""

def init_entangles_frac_v_swap_num(init_entangles, total_entangles, swap_num):

    fig = plt.figure('Initial Entanglement Fraction v. Swap Number', figsize=(4, 3.5))

    plt.xlabel("Fraction of Entanglements in Candidate Graph")
    plt.ylabel("# of Swaps")

    plt.tight_layout()

    plt.scatter([x/total_entangles for x in init_entangles], swap_num)

    return fig

def graph_distance_v_ave_swaps(graph_distance, ave_swap_num):

    fig = plt.figure('Initial Graph Distance v. Ave Swap Number', figsize=(4, 3.5))

    plt.xlabel("Initial Total Graph Distance")
    plt.ylabel("Ave # of Swaps")

    plt.tight_layout()

    plt.scatter(graph_distance, ave_swap_num)

    return fig

def makeAttemptHist(attempts):

    fig = plt.figure("# of Bad Graphs per Good Graph", figsize=(4, 3.5))

    plt.xlabel("# of Bad Graphs")
    plt.ylabel("Frequency")

    plt.hist(attempts, bins=range(min(attempts), max(attempts)+2), align='left', rwidth=0.8)
    plt.tight_layout()

    return fig


# Function to make the qubit lattice plot
def makePlacementSpiralImage(graph):

    # The lattice graph should always be colored by the time this is called
    color_array = list('#3c75aa' for i in graph.nodes())
    size_array = list(200 for i in graph.nodes())
    labels = {i: i for i in graph.nodes()}

    # Make and show plot
    # This plot has a number to differentiate from the QUBO graph
    fig = plt.figure('Lattice Graph', figsize=(4, 3.5))

    axLat = plt.axes(facecolor='w')
    axLat.set_axis_off()

    # Draw lattice
    nx.draw_networkx(graph, pos=graph.nodes.data('pos'), node_color=color_array, node_size=size_array, labels=labels)

    return fig