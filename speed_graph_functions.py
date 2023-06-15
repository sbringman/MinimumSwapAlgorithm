#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed June 14th

@author: sambringman
"""

import networkx as nx
import random
from pandas import read_csv
import copy

"""
Functions to Create the Graphs
"""

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
            graph.add_node(node, green=False, placed=False, tail_start=False, tail_end=False, embedded=-1)

    # Else, add the edges from the filepath
    else:
        num_edges = 0
        num_nodes = int(num_nodes)
        list_nodes = list(range(0, num_nodes))

        # Generates the nodes
        graph = nx.Graph()
        for node in list_nodes:
            graph.add_node(node, green=False, placed=False, tail_start=False, tail_end=False, embedded=-1)

        QUBO_edges_info = read_csv(filepath, skiprows=1)

        for index, row in QUBO_edges_info.iterrows():
            graph.add_edge(row['Node1'], row['Node2'])
            num_edges += 1
    
    return graph, num_nodes, num_edges, list_nodes


#This function finds the green nodes
def find_greens(graph):

    # Second, find the end nodes and the end tails
    for node in graph.nodes:

        # Upon finding an end node, trace it back until there's a node of degree
        # greater than 2
        if graph.degree[node] == 1:
            graph.nodes[node]['green'] = True
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
                        graph.nodes[next_node]['green'] = True
                        prev_nodes.append(next_node)
                        cur_node = next_node

                    # Else break out of the loop, you've reached the end of the
                    # tail
                    else:
                        #print("End of chain")
                        graph.nodes[cur_node]['tail_start'] = True
                        in_tail = False
    
    return graph


# This makes the qubit lattice from an imported file
def import_lattice():
    # This will just be a premade lattice with a certain number of qubits

    HH_node_info = read_csv(HH_nodes_filepath, skiprows=1)
    HH_edges_info = read_csv(HH_edges_filepath, skiprows=1)

    lattice_graph = nx.Graph()

    for index, row in HH_node_info.iterrows():

        lattice_graph.add_node(index, qubit=-1)

    for index, row in HH_edges_info.iterrows():

        lattice_graph.add_edge(row['Node1'], row['Node2'])
    
    return lattice_graph


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

    # Places the first qubit
    #print(QUBO_Graph.nodes(data=True))
    cand_qubits = [x for x, node in QUBO_Graph.nodes(data=True) if not node['green']]

    # Picks the first node
    rand_node = random.choices(cand_qubits, k=1)[0]

    #print(f"The first node to be placed is {rand_node}")
    #print(f"Node {rand_node} was placed at 0")

    # Places the first node
    place_node(lattice_Graph, QUBO_Graph, 0, rand_node)

    prev_node = rand_node

    # Places the rest of the qubits that are not green
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

        QUBO_Graph.nodes[qubit_1]['embedded'], QUBO_Graph.nodes[qubit_2]['embedded'] = lattice_point2, lattice_point1
    
    elif qubit_2 == -1:

        QUBO_Graph.nodes[qubit_1]['embedded'] = lattice_point2
    
    else:

        QUBO_Graph.nodes[qubit_2]['embedded'] = lattice_point1

    return None


# This function runs all the entanglements for the current graph
# May want to have it check all edges in the QUBO graph for edges in the lattice graph instead
def get_current_entangles(lattice_Graph, QUBO_Graph, list_of_entangles):

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

        elif edge2 in list_of_entangles:
            #print(f"{edge2} was entangled")
            
            list_of_entangles.remove(edge2)
        
        else:
            #print(f"{edge1} and {edge2} were not in the list of entanglements")
            pass
    
    return lattice_Graph, QUBO_Graph, list_of_entangles


# This function finds the next position for the lattice graph to swap to
def perform_next_swap(lattice_Graph, QUBO_Graph, list_of_entangles):

    # Find the next graph to swap to
    shortest_swap = [-1, -1, 100000000] # node 1, node 2, swap distance

    # Check the distances between the entanglements that still need to be done
    for entangle in list_of_entangles:
        path = nx.astar_path(lattice_Graph, QUBO_Graph.nodes[entangle[0]]['embedded'], QUBO_Graph.nodes[entangle[1]]['embedded'])
        #print(f"The distance between the qubits {entangle[0]} and {entangle[1]} is {len(path)}")
        #print(f"\tThis would be along the path {path}")

        # A path length of 3 is the shortest possible swap - 1 swap, so it should be done
        if len(path) < shortest_swap[2] or len(path) == 3:
            #print(f"\tThis path of distance {len(path)} is shorter than {shortest_swap[2]}, so it will be done instead")
            shortest_swap = [entangle[0], entangle[1], len(path)]
    
    #print(f"The next swap will be qubits {entangle[0]} and {entangle[1]} with a path length of {path}")

    # Perform the swaps
    swaps = 0
    swap_list = []

    while swaps < len(path) - 2:

        # This works because it is only swapping the qubits on top of the lattice points,
        # so it is only changing the variables attached to each lattice point
        # The lattice points remain unchanged in this
        swap_qubits(lattice_Graph, QUBO_Graph, path[swaps], path[swaps+1])

        swap_list.append((lattice_Graph.nodes[path[swaps]]['qubit'], lattice_Graph.nodes[path[swaps+1]]['qubit']))

        swaps += 1

    # Entangle everythings that needs to be entangled

    return lattice_Graph, swaps, swap_list, list_of_entangles




# Function that copies one graph onto another, for the purpose of resetting the graph
def copy_graph(template, graph_to_reset):

    # We only need to reset nodes, because all the information is in the nodes.
    # The only information in the edges is the color of the edge in the QUBO graph
    # to indicate entanglement
    graph_to_reset.update(nodes=list(template.nodes(data=True)))

    return(graph_to_reset)


# Function that copies one graph onto another, for the purpose of resetting the graph
def reconstruct_lattice(qubits, graph_to_construct):

    for node in graph_to_construct:
        graph_to_construct.nodes[node]["qubit"] = qubits[node]

    return(graph_to_construct)

# Function that copies one graph onto another, for the purpose of resetting the graph
def reconstruct_qubo(embeds, graph_to_construct):

    for node in graph_to_construct:
        graph_to_construct.nodes[node]["embedded"] = embeds[node]

    return(graph_to_construct)


# This is the code to iterate through trial graphs to find the best solution
def iterate_through(lattice_Graph, QUBO_Graph, iterations):
    # First thing to do is save all the original variables
    original_QUBO = copy.deepcopy(QUBO_Graph)
    original_lattice = copy.deepcopy(lattice_Graph)
    best_lattice_nodes = []
    best_qubo_embed = []

    # Then, get the variables for the process
    iter_num = 0
    list_of_swap_nums = []
    best_swap_list = []
    best_swap_num = 100000000000

    while iter_num < iterations:

        # Refresh everything
        QUBO_Graph = copy_graph(original_QUBO, QUBO_Graph)
        lattice_Graph = copy_graph(original_lattice, lattice_Graph)
        solved = False
        early_break = False
        swap_num = 0
        swap_list = []

        # Map to the lattice
        lattice_Graph, QUBO_Graph = place_initial_qubits(lattice_Graph, QUBO_Graph)
        lattice_Graph, QUBO_Graph = place_green_qubits(lattice_Graph, QUBO_Graph)

        # We have to save this for when it finds the best path
        # However, the only important parts of the graph that we need are the nodes
        start_lattice_nodes = copy.copy([value for node, value in lattice_Graph.nodes(data="qubit")])
        start_qubo_embed = copy.copy([value for node, value in QUBO_Graph.nodes(data="embedded")])

        #print(start_lattice_nodes)

        # Do initial entangling
        # entangles is a list of all the qubits that need to be entangled.
        # It is a list of tuples
        entangles_to_do = list(QUBO_Graph.edges)
        # num_entangles does nothing here

        lattice_Graph, QUBO_Graph, entangles_to_do = get_current_entangles(lattice_Graph, QUBO_Graph, entangles_to_do)

        while not solved:
            # Do the swaps
            lattice_Graph, new_swaps, new_swap_list, entangles_to_do = perform_next_swap(lattice_Graph, QUBO_Graph, entangles_to_do)
            swap_num += new_swaps
            swap_list += new_swap_list

            # Get the current entanglements
            lattice_Graph, QUBO_Graph, entangles_to_do = get_current_entangles(lattice_Graph, QUBO_Graph, entangles_to_do)


            # If we have already gone past the best swap num, immediately stop
            if swap_num >= best_swap_num:
                early_break = True
                break

            # If all the entanglments are done, quit
            if not entangles_to_do:
                
                solved = True
                #print(f"Finished solving attempt {i + 1} - {swap_num} swap_num")

        # Stuff done after the graphs are finished
        # We don't want to count early breaks as part of the average swap number
        if not early_break:
            list_of_swap_nums.append(swap_num)
            early_break = False

        if swap_num < best_swap_num:
            best_swap_num = swap_num
            best_swap_list = swap_list
            best_lattice_nodes = copy.copy(start_lattice_nodes)
            best_qubo_embed = copy.copy(start_qubo_embed)
            #print("\n\n\n")
            #print(best_lattice_nodes)

            print(f"A new best swap path was found, with a length of {len(swap_list)}")
        
        iter_num += 1


    
    return best_swap_list, list_of_swap_nums, best_lattice_nodes, best_qubo_embed