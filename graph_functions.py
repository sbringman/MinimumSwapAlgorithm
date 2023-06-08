#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed June 7th

@author: sambringman
"""

import networkx as nx
from pandas import read_csv
import random

# Paths to the HH lattice data files
HH_nodes_filepath = "./HH_Nodes.txt"
HH_edges_filepath = "./HH_Edges.txt"

# This function takes the number of nodes and the file path as input
# It then makes a nx graph from the user input
# It returns the graph, along with information about the nodes and edges
def make_qubo_graph(num_nodes, filepath):

    # If no filepath, make blank graph
    if filepath == "None":

        num_nodes = int(num_nodes)
        list_nodes = list(range(0, num_nodes))
        num_edges = 0

        graph = nx.Graph()
        for node in list_nodes:
            graph.add_node(node, color='b', pos=[0.2, 0.2], placed=False, tail_start=False, tail_end=False, embedded=-1)

    # Else, add the edges from the filepath
    else:
        num_edges = 0
        num_nodes = int(num_nodes)
        list_nodes = list(range(0, num_nodes))

        # Generates the nodes
        graph = nx.Graph()
        for node in list_nodes:
            graph.add_node(node, color='b', pos=[0.2, 0.2], placed=False, tail_start=False, tail_end=False, embedded=-1)

        QUBO_edges_info = read_csv(filepath, skiprows=1)

        for index, row in QUBO_edges_info.iterrows():
            graph.add_edge(row['Node1'], row['Node2'])
            num_edges += 1
    
    return graph, num_nodes, num_edges, list_nodes



# This takes in a graph and colors it according to my color
# definitions
def color_graph(graph):
    # Green qubits count as placed, because they will be put on in specific
    # spots at the end

    # First, turn everything yellow
    for node in graph.nodes:
        graph.nodes[node]['color'] = 'y'

    # Second, find the end nodes and the end tails
    for node in graph.nodes:
        # Blue means unconnected
        if graph.degree[node] == 0:
            graph.nodes[node]['color'] = 'b'

        # Upon finding an end node, trace it back until there's a node of degree
        # greater than 2
        elif graph.degree[node] == 1:
            graph.nodes[node]['color'] = 'g'
            graph.nodes[node]['placed'] = True
            graph.nodes[node]['tail_end'] = True

            cur_node = node
            prev_nodes = [node]
            in_tail = True
            while in_tail:

                # See if the next node in the trail is degree two
                for next_node in nx.neighbors(graph, cur_node):
                    # print(f"Node #{cur_node}, Neighbor #{next_node}")

                    # This is node from previously up the chain.
                    # It's boring and we want to skip it so we go further
                    # down the end tail chain
                    if next_node in prev_nodes:
                        # print("Skipped")
                        continue

                    elif graph.degree[next_node] == 2:
                        # print("Colored")
                        graph.nodes[next_node]['color'] = 'g'
                        graph.nodes[next_node]['placed'] = True
                        prev_nodes.append(next_node)
                        cur_node = next_node

                    # Else break out of the loop, you've reached the end of the
                    # tail
                    else:
                        #print("End of chain")
                        graph.nodes[cur_node]['tail_start'] = True
                        in_tail = False

    # Third, color the max degree nodes red
    max_degree = max(graph.degree, key=lambda x: x[1])[1]

    # If the max is less than 3, it doesn't matter because the entanglement
    # is a chain
    max_degree = max(max_degree, 3)

    # Checks if it is the node with the max degree
    for node in graph.nodes:

        if graph.degree[node] == max_degree:
            graph.nodes[node]['color'] = 'r'

    return graph


# This makes the qubit lattice from an imported file
def import_lattice():
    # This will just be a premade lattice with a certain number of qubits

    HH_node_info = read_csv(HH_nodes_filepath, skiprows=1)
    HH_edges_info = read_csv(HH_edges_filepath, skiprows=1)

    lattice_graph = nx.Graph()

    for index, row in HH_node_info.iterrows():

        lattice_graph.add_node(index, pos=[row['x_coor'], row['y_coor']],
                            qubit=-1, size=100, color='k')

    for index, row in HH_edges_info.iterrows():

        lattice_graph.add_edge(row['Node1'] - 1, row['Node2'] - 1)
    
    return lattice_graph


# This places the qubits onto the lattice
def place_initial_qubits(lattice_Graph, QUBO_Graph):
    # Remeber, everything on the HH lattice has degree 3 when fully connected
    # 1. Place the first qubit
    # 2. Find a neighbor that is untaken and place the next qubit from among
    #       those among the first one's neighbors
    # 3. Repeat 2 until finished
    # 4. Place end tails at the closest untaken node to their attachment point

    # Place non-edge tail qubits
    # Places the first qubit
    cand_qubits = [x for x, node in QUBO_Graph.nodes(data=True) if node['color'] == 'y']

    rand_node = random.choices(cand_qubits, k=1)[0]

    # Modifies the info stored in the nodes
    lattice_Graph.nodes[0]['qubit'] = rand_node
    lattice_Graph.nodes[0]['color'] = QUBO_Graph.nodes[rand_node]['color']
    lattice_Graph.nodes[0]['size'] = 300

    # Modifies the info stored in the nodes
    QUBO_Graph.nodes[rand_node]['placed'] = True
    QUBO_Graph.nodes[rand_node]['embedded'] = 0

    prev_node = rand_node

    # Places the rest of the qubits
    for i in range(len([x for x, node in QUBO_Graph.nodes(data=True) if node['placed'] is False])):
        cand_qubits = [x for x, node in QUBO_Graph.nodes(data=True) if (x in nx.neighbors(QUBO_Graph, prev_node) and node['placed'] is False)]

        # If all the neighbors of the previous node have been placed, then randomly
        # choose from unplaced qubits
        if cand_qubits == []:
            cand_qubits = [x for x, node in QUBO_Graph.nodes(data=True) if node['placed'] is False]

        # print(cand_qubits)

        rand_node = random.choices(cand_qubits, k=1)[0]

        # i+1 because the first node is already taken
        lattice_Graph.nodes[i + 1]['qubit'] = rand_node
        lattice_Graph.nodes[i + 1]['color'] = QUBO_Graph.nodes[rand_node]['color']
        lattice_Graph.nodes[i + 1]['size'] = 300

        QUBO_Graph.nodes[rand_node]['placed'] = True
        QUBO_Graph.nodes[rand_node]['embedded'] = i + 1

        prev_node = rand_node

    # Place green qubits
    for start_node in [x for x, node in QUBO_Graph.nodes(data=True) if node['tail_start'] is True]:
        #print(f"The next green node to be placed is: {start_node}")

        # Gets the qubit that connects the tail to the main graph
        connecting_qubit = [x for x in nx.neighbors(QUBO_Graph, start_node) if QUBO_Graph.degree[x] > 2][0]
        #print(f"The qubit it is connected to is: {connecting_qubit}")
        while True:

            # Checks if there is a place to put the next green qubit
            for placement_spot in nx.neighbors(lattice_Graph, QUBO_Graph.nodes[connecting_qubit]['embedded']):

                # If no qubit, place the node
                if lattice_Graph.nodes[placement_spot]['qubit'] == -1:

                    lattice_Graph.nodes[placement_spot]['qubit'] = start_node
                    lattice_Graph.nodes[placement_spot]['color'] = QUBO_Graph.nodes[start_node]['color']
                    lattice_Graph.nodes[placement_spot]['size'] = 300

                    QUBO_Graph.nodes[start_node]['placed'] = True
                    QUBO_Graph.nodes[start_node]['embedded'] = placement_spot
                    print(f"Qubit {start_node} was placed at {placement_spot}")
                    break

            # If the green node that was placed has a degree of 0, then the chain is finished
            if QUBO_Graph.degree(start_node) == 1:
                #print(f"This chain has ended, and the connecting node was embedded at {QUBO_Graph.nodes[connecting_qubit]['embedded']}")
                break
            else:
                # The placed qubit now connects the chain
                connecting_qubit = start_node

                # The qubit to be placed in the next one in line
                start_node = [x for x in nx.neighbors(QUBO_Graph, connecting_qubit) if QUBO_Graph.nodes[x]['embedded'] == -1][0]

                #print(f"Now, we will connect qubit {start_node} to qubit {connecting_qubit}")

    return lattice_Graph, QUBO_Graph


