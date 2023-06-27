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
            graph.add_node(node, green=False, placed=False, tail_start=False, tail_end=False, embedded=-1, color='b')

    # Else, add the edges from the filepath
    else:
        num_edges = 0
        num_nodes = int(num_nodes)
        list_nodes = list(range(0, num_nodes))

        # Generates the nodes
        graph = nx.Graph()
        for node in list_nodes:
            graph.add_node(node, green=False, placed=False, tail_start=False, tail_end=False, embedded=-1, color='b')

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
            graph.nodes[node]['green'] = True
            graph.nodes[node]['color'] = 'g'
            graph.nodes[node]['tail_end'] = True

            cur_node = node
            prev_nodes = [node]
            in_tail = True
            while in_tail:

                # See if the next node in the trail is degree two
                for next_node in nx.neighbors(graph, cur_node):
                    #print(f"Node #{cur_node}, Neighbor #{next_node}")

                    # This is node from previously up the chain.
                    # It's boring and we want to skip it so we go further
                    # down the end tail chain
                    if next_node in prev_nodes:
                        #print(f"Node {next_node} was skipped")
                        continue

                    elif graph.degree[next_node] == 2:
                        #print(f"Node {next_node} was colored")
                        graph.nodes[next_node]['green'] = True
                        graph.nodes[next_node]['color'] = 'g'
                        prev_nodes.append(next_node)
                        cur_node = next_node
                        break

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
    
    # Next, color the edges, which at this stage will always be red
    for edge in graph.edges:
        graph.edges[edge]['color'] = 'r'

    return graph



# This takes in a graph and colors it according to my color
# definitions
def color_edges(graph, list_of_entangles):
    
    for node1, node2 in graph.edges():

        if (node1, node2) in list_of_entangles:
            graph.edges[node1, node2]['color'] = 'r'
        elif (node2, node1) in list_of_entangles:
            graph.edges[node1, node2]['color'] = 'r'
        else:
            graph.edges[node1, node2]['color'] = 'g'


    return graph



# This makes the qubit lattice from an imported file
def import_lattice():
    # This will just be a premade lattice with a certain number of qubits

    HH_node_info = read_csv(HH_nodes_filepath, skiprows=1)
    HH_edges_info = read_csv(HH_edges_filepath, skiprows=1)

    lattice_graph = nx.Graph()

    for index, row in HH_node_info.iterrows():

        lattice_graph.add_node(index, qubit=-1, size=10, color='k', pos=(row['x_coor'], row['y_coor']))

    for index, row in HH_edges_info.iterrows():

        lattice_graph.add_edge(row['Node1'], row['Node2'])
    
    return lattice_graph


# This takes in a lattice and colors it
def color_lattice(graph, QUBO):

    HH_node_info = read_csv(HH_nodes_filepath, skiprows=1)

    # First, turn everything black
    for index, row in HH_node_info.iterrows():
        graph.nodes[index]['pos'] = (row['x_coor'], row['y_coor'])
        graph.nodes[index]['size'] = 100
        graph.nodes[index]['color'] = 'k'

    # Then, change the colors to match the colors of the QUBO graph
    for node in QUBO.nodes:
        embed = QUBO.nodes[node]['embedded']
        graph.nodes[embed]['color'] = QUBO.nodes[node]['color']
        graph.nodes[embed]['size'] = 300

    return graph


"""
Functions to Map the QUBO to the Lattice
"""


# This just places the nodes onto the graph in the given spot
def place_node(lattice_Graph, QUBO_Graph, lattice_node, qubo_node):
    # Places the node
    lattice_Graph.nodes[lattice_node]['qubit'] = qubo_node

    QUBO_Graph.nodes[qubo_node]['placed'] = True
    QUBO_Graph.nodes[qubo_node]['embedded'] = lattice_node


# This function finds an open space to place an end tail
def find_open_node(lattice_Graph, QUBO_Graph, start_node, connecting_node):

    # Transform the connecting_node to the lattice graph
    connecting_node = QUBO_Graph.nodes[connecting_node]['embedded']

    placement_node = -1

    # This will just start at the connecting qubit and explore all neighbors until
    # it finds an open spot. It doesn't matter what spot it finds first, because is
    # checks all possible places to put the end tail at a certain distance before
    # moving on to a further distance
    # All of these nodes are in the lattice_Graph except the one it is trying to place

    # List of nodes I have not found empty neighbors for
    list_of_tried_nodes = [connecting_node]

    # List of nodes I want to check for neighbors
    connecting_nodes = [x for x in nx.neighbors(lattice_Graph, connecting_node)]
    list_of_tried_nodes += connecting_nodes

    # List of potentially empty places to put the end tail
    potential_empty_nodes = []

    while placement_node == -1:

        #print(f"The qubit {start_node}, which is connected to {connecting_node} has been tried to be placed at locations {list_of_tried_nodes}")

        # Find all the nodes that I need to check for an empty neighbor
        for node in connecting_nodes:
            new_items = [x for x in nx.neighbors(lattice_Graph, node) if (x not in list_of_tried_nodes and x not in potential_empty_nodes)]
            potential_empty_nodes += new_items

        #print(f"The location(s) {potential_empty_nodes} are candidate nodes to place {start_node} because they are neighbors of locations {connecting_nodes}")

        # Run through all the nodes
        for node in potential_empty_nodes:

            # If there's nothing there, place the qubit
            if lattice_Graph.nodes[node]['qubit'] == -1:
                placement_node = node
                #print(f"The node {start_node} will be placed at location: {node}")
                break

            else:
                #print(f"The node {start_node} could not be placed at location: {node}")
                list_of_tried_nodes.append(node)

        # The potential_empty_nodes becomes the connecting_nodes list
        connecting_nodes = []
        connecting_nodes = potential_empty_nodes
         
    # At the end, we return the node that we will put the end of the tail at
    return(placement_node)


def place_initial_qubits(lattice_Graph, QUBO_Graph):
    #print(lattice_Graph.nodes(data=True))
    #print(QUBO_Graph.nodes(data=True))

    # Places the first qubit
    #print(QUBO_Graph.nodes(data=True))
    cand_qubits = [x for x, node in QUBO_Graph.nodes(data=True) if not node['green']]

    # Picks the first node
    rand_node = random.choices(cand_qubits, k=1)[0]

    #print(f"The first node to be placed is {rand_node}")
    #print(f"Node {rand_node} was placed at 0")

    # Places the first node
    place_node(lattice_Graph, QUBO_Graph, 0, rand_node)
    #print(lattice_Graph.nodes(data=True))

    prev_node = rand_node

    # Places the rest of the qubits that are not green
    # Remeber, subtract another 1 in the range function because it starts at 0
    print(f"{len([x for x, node in QUBO_Graph.nodes(data=True) if not node['green']])} nodes are not green")
    for i in range(len([x for x, node in QUBO_Graph.nodes(data=True) if not node['green']]) - 1):

        # Chooses new candidate qubits
        cand_qubits = [x for x, node in QUBO_Graph.nodes(data=True) if (x in nx.neighbors(QUBO_Graph, prev_node) and not node['placed'] and not node['green'])]

        # If all the neighbors of the previous node have been placed, then randomly
        # choose from unplaced qubits
        if not cand_qubits:
            cand_qubits = [x for x, node in QUBO_Graph.nodes(data=True) if (not node['placed'] and not node['green'])]
        
        #print(f"The candidate qubits for the next placement is {cand_qubits}")

        rand_node = random.choices(cand_qubits, k=1)[0]

        #print(f"The next node to be placed is {rand_node} at lattice location {i+1}")

        # The lattice point is i + 1 because we are placing the qubits onto the
        # lattice sequentially
        place_node(lattice_Graph, QUBO_Graph, i+1, rand_node)
        #print(lattice_Graph.nodes(data=True))

        prev_node = rand_node
    
    #print("All of the non-green nodes have been placed")
    
    return lattice_Graph, QUBO_Graph


# This places all the green qubits
def place_green_qubits(lattice_Graph, QUBO_Graph):

    #print("Beginning placement of green nodes")

    # We have to run through each chain of green nodes on the graph
    for start_node in [x for x, node in QUBO_Graph.nodes(data=True) if node['tail_start'] is True]:
        #print(f"The next chain to be placed starts with the node {start_node}")

        # Gets the qubit that connects the tail to the main graph
        # The connecting qubit will always have a degree of greater than two, or it would be part of the chain
        connecting_node = [x for x in nx.neighbors(QUBO_Graph, start_node) if QUBO_Graph.degree[x] > 2][0]
        
        #print(f"This chain will connect to the main graph at {connecting_node}, which is embedded at location {QUBO_Graph.nodes[connecting_node]['embedded']}")

        while True:

            placed = False

            # Checks if there is an open spot next to the connecting node
            # The connecting node will always already be embedded, so it will have a spot on the lattice graph
            for placement_spot in nx.neighbors(lattice_Graph, QUBO_Graph.nodes[connecting_node]['embedded']):

                # If no qubit, place the node
                if lattice_Graph.nodes[placement_spot]['qubit'] == -1:

                    place_node(lattice_Graph, QUBO_Graph, placement_spot, start_node)
                    placed = True
                    
                    #print(f"The node {start_node} has been placed on the lattice at location {placement_spot}")
                    break
            
            # If a placement spot hasn't been found, search further away
            if not placed:

                placement_spot = find_open_node(lattice_Graph, QUBO_Graph, start_node, connecting_node)

                place_node(lattice_Graph, QUBO_Graph, placement_spot, start_node)
                    
                #print(f"The node {start_node} has been placed on the lattice at location {placement_spot}")
            
            # If the green node that was placed has a degree of 0, then the chain is finished
            if QUBO_Graph.degree(start_node) == 1:
                #print(f"This chain has ended")
                break
            else:
                # The placed qubit now connects the chain
                connecting_node = start_node
                #print( QUBO_Graph.nodes[4]['green'])
                #print([x for x in nx.neighbors(QUBO_Graph, connecting_node) if QUBO_Graph.nodes[x]['embedded'] == -1])

                # The qubit to be placed in the next one in line
                start_node = [x for x in nx.neighbors(QUBO_Graph, connecting_node) if QUBO_Graph.nodes[x]['embedded'] == -1][0]

                #print(f"Now, we will connect qubit {start_node} to qubit {connecting_node}")
    
    #print("All of the green nodes have been placed")

    return lattice_Graph, QUBO_Graph


"""
Swapping Functions
"""


# This function swaps two qubits
# It doesn't return anything, it just swaps them in the function
def swap_qubits(lattice_Graph, QUBO_Graph, lattice_point1, lattice_point2):

    qubit_1 = lattice_Graph.nodes[lattice_point1]['qubit']
    qubit_2 = lattice_Graph.nodes[lattice_point2]['qubit']

    lattice_Graph.nodes[lattice_point1]['qubit'], lattice_Graph.nodes[lattice_point2]['qubit'] = lattice_Graph.nodes[lattice_point2]['qubit'], lattice_Graph.nodes[lattice_point1]['qubit']

    if qubit_1 != -1 and qubit_2 != -1:

        #print(f"The qubits {qubit_1} and {qubit_2} were swapped")

        QUBO_Graph.nodes[qubit_1]['embedded'], QUBO_Graph.nodes[qubit_2]['embedded'] = lattice_point2, lattice_point1
    
    elif qubit_2 == -1:
        #print(f"Moving qubit {qubit_1} to a empty slot")

        QUBO_Graph.nodes[qubit_1]['embedded'] = lattice_point2
    
    else:
        #print(f"Moving qubit {qubit_2} to a empty slot")

        QUBO_Graph.nodes[qubit_2]['embedded'] = lattice_point1

    return None


# This function runs all the entanglements for the current graph
# May want to have it check all edges in the QUBO graph for edges in the lattice graph instead
def get_current_entangles(lattice_Graph, QUBO_Graph, list_of_entangles):

    new_entangles = 0 

    #print(f"Here is the list of qubits that need to be entangled: {list_of_entangles}")

    for node_1, node_2 in lattice_Graph.edges:

        # This function transforms the edge in the lattice graph to an edge in the 
        # qubit graph
        # There is a difference between (0, 1) and (1, 0)
        edge1 = (lattice_Graph.nodes[node_1]['qubit'], lattice_Graph.nodes[node_2]['qubit'])
        edge2 = (lattice_Graph.nodes[node_2]['qubit'], lattice_Graph.nodes[node_1]['qubit'])

        # This is the case where there is no qubit embedded at that spot
        if edge1[0] == -1 or edge1[1] == -1 or edge2[0] == -1 or edge2[1] == -1:
            pass

        elif edge1 in list_of_entangles:
            #print(f"{edge1} was entangled")
            
            list_of_entangles.remove(edge1)
            new_entangles += 1

        elif edge2 in list_of_entangles:
            #print(f"{edge2} was entangled")
            
            list_of_entangles.remove(edge2)
            new_entangles += 1
        
        else:
            #print(f"{edge1} and {edge2} were not in the list of entanglements")
            pass
    
    return lattice_Graph, QUBO_Graph, list_of_entangles, new_entangles


# This function calculates the sum of distances for each qubit from all the qubits it
# needs to entangle with
def calc_graph_total_distance(QUBO, all_path_lengths, list_of_entangles):

    total_dist = 0

    # Adds up the distance between every pair of qubits that needs to be entangled
    for entangle in list_of_entangles:
            
        total_dist += all_path_lengths[QUBO.nodes[entangle[0]]['embedded']][QUBO.nodes[entangle[1]]['embedded']]

    return total_dist


# Function to calculate the total distance from a qubit to all of the qubits it
# needs to entangle with
# All positions are positions on the lattice
def calc_distance_change(all_path_lengths, list_of_entangles, qubit, start_pos, end_pos, QUBO_Graph):

    # This calculation has the problem that it doesn't switch the qubits before testing the distances
    # In order to remedy this oversight, if moving the qubit would generate a distance of 0 from it's
    # pair, then you need to add the path length from the start position to the end position
    # The reason for this is that if there's a path of length of 0, then the qubit is being moved 
    # to the same spot as the qubit it needs to entangle with.
    # So, that qubit must be switching places with the original qubit.
    # This means that the new distance between them will be the path length between them
    path_length = all_path_lengths[start_pos][end_pos]

    dist_at_start = 0
    dist_at_end = 0

    # Find all the entangles left to do for that qubit
    for entangle in list_of_entangles:
        if entangle[0] == qubit:

            embed_node = QUBO_Graph.nodes[entangle[1]]['embedded']

            dist_at_start += all_path_lengths[start_pos][embed_node]

            if all_path_lengths[end_pos][embed_node] == 0:
                dist_at_end += path_length
            else:
                dist_at_end += all_path_lengths[end_pos][embed_node]

        elif entangle[1] == qubit:

            embed_node = QUBO_Graph.nodes[entangle[0]]['embedded']

            dist_at_start += all_path_lengths[start_pos][embed_node]

            if all_path_lengths[end_pos][embed_node] == 0:
                dist_at_end += path_length
            else:
                dist_at_end += all_path_lengths[end_pos][embed_node]

    return dist_at_end - dist_at_start


# This function finds the next position for the lattice graph to swap to
def perform_next_swap(lattice_Graph, QUBO_Graph, list_of_entangles, all_path_lengths):
    print(lattice_Graph.nodes(data=True))

    # Find the next graph to swap to
    shortest_swap_dist = 100000000
    cand_swap_list = [] # This will be a list of tuples, where tuples are the path

    # Check the distances between the entanglements that still need to be done
    for entangle in list_of_entangles:
        path = nx.astar_path(lattice_Graph, QUBO_Graph.nodes[entangle[0]]['embedded'], QUBO_Graph.nodes[entangle[1]]['embedded'])
        #print(f"The distance between the qubits {entangle[0]} and {entangle[1]} is {len(path)}")
        #print(f"\tThis would be along the path {path}")

        if len(path) < shortest_swap_dist:
            #print(f"\tThis path of distance {len(path)} is the new shortest path")
            cand_swap_list = [path]
            shortest_swap_dist = len(path)
        elif len(path) == shortest_swap_dist:
            #print(f"\tThis path of distance {len(path)} is short enough to be added to the candidate list")
            cand_swap_list.append(path)

    #print(f"The next path will be chosen from a list with {len(cand_swap_list)} items: {cand_swap_list}")
    path = random.choices(cand_swap_list, k=1)[0]

    left_qubit = lattice_Graph.nodes[path[0]]['qubit']
    right_qubit = lattice_Graph.nodes[path[-1]]['qubit']

    #print(f"\nThe next swap will be qubits {left_qubit} and {right_qubit} with a path of {path}\n")

    # Perform the swaps
    swaps = 0
    swap_list = []

    # This is the total distance from the qubit to all of its entangles
    # It compares that total distance while in its original spot with the total
    # distance from the spot it will be moving to, returning the difference
    dist_change_l = calc_distance_change(all_path_lengths, list_of_entangles, left_qubit, path[0], path[1], QUBO_Graph)
    dist_change_r = calc_distance_change(all_path_lengths, list_of_entangles, right_qubit, path[-1], path[-2], QUBO_Graph)

    #print(f"Initial distance change left is {dist_change_l}")
    #print(f"Initial distance change right is {dist_change_r}")

    marker_l = 0
    marker_r = -1

    while swaps < len(path) - 2:
        #print(f"Swaps left for this path: {len(path) - 2 - swaps}")

        # Swap the left qubit over
        if dist_change_l < dist_change_r:
            # This works because it is only swapping the qubits on top of the lattice points,
            # so it is only changing the variables attached to each lattice point
            # The lattice points remain unchanged in this
            swap_qubits(lattice_Graph, QUBO_Graph, path[marker_l], path[marker_l+1])
            swap_list.append((lattice_Graph.nodes[path[marker_l]]['qubit'], lattice_Graph.nodes[path[marker_l+1]]['qubit']))
            swaps += 1

            #print(f"The left qubit {lattice_Graph.nodes[path[marker_l]]['qubit']} will be swapped with {lattice_Graph.nodes[path[marker_l+1]]['qubit']}")

            # We only need to advance if we are not done swapping
            if swaps < len(path) - 2:
                marker_l += 1
                dist_change_l = calc_distance_change(all_path_lengths, list_of_entangles, left_qubit, path[marker_l-1], path[marker_l], QUBO_Graph)

                #print(f"The new left distance change is {dist_change_l}")

        # Swap the right qubit over, or it doesn't matter because the two are tied
        else:

            swap_qubits(lattice_Graph, QUBO_Graph, path[marker_r], path[marker_r-1])
            swap_list.append((lattice_Graph.nodes[path[marker_r]]['qubit'], lattice_Graph.nodes[path[marker_r-1]]['qubit']))
            swaps += 1

            #print(f"The right qubit {lattice_Graph.nodes[path[marker_r]]['qubit']} will be swapped with {lattice_Graph.nodes[path[marker_r-1]]['qubit']}")

            if swaps < len(path) - 2:
                marker_r -= 1
                dist_change_r = calc_distance_change(all_path_lengths, list_of_entangles, right_qubit, path[marker_r-1], path[marker_r], QUBO_Graph)

                #print(f"The new right distance change is {dist_change_r}")
    

    return lattice_Graph, swaps, swap_list, list_of_entangles
    

