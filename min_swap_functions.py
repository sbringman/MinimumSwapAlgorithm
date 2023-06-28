#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue June 27th

@author: sambringman
"""

import networkx as nx
import random as rand


def add_node_details(graph, width, height):

    # Adds the positional arguments to the nodes, so they can be graphed
    for x in range(width):
        for y in range(height):

            # Position will always be between 0 and 1
            graph.nodes[(x, y)]["pos"] = (x * (1 / (width - 1)), y * (1 / (height - 1)))
            graph.nodes[(x, y)]["qubit"] = -1
            graph.nodes[(x, y)]["size"] = 50
            graph.nodes[(x, y)]["color"] = 'k'

    return graph


# Place qubits
def place_qubit(graph, node, qubit):

    graph.nodes[node]["qubit"] = qubit
    graph.nodes[node]["size"] = 300
    graph.nodes[node]["color"] = 'b'

    return graph


# A function to place qubits onto the lattice
def map_qubits(graph, qubits, entangle_list):

    for qubit in qubits:
        node = rand.choices(list(graph.nodes), k=1)[0]
        place_qubit(graph, node, qubit)

    return graph


# Place qubits
def swap_qubits(graph, node1, node2):

    graph.nodes[node1]["qubit"], graph.nodes[node2]["qubit"] = graph.nodes[node2]["qubit"], graph.nodes[node1]["qubit"]
    graph.nodes[node1]["color"], graph.nodes[node2]["color"] = graph.nodes[node2]["color"], graph.nodes[node1]["color"]
    graph.nodes[node1]["size"], graph.nodes[node2]["size"] = graph.nodes[node2]["size"], graph.nodes[node1]["size"]

    return graph
