#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  17

@author: sambringman
"""

import argparse
import numpy as np
import time

import plotting_functions as gui_func
import optimization_funcs as ofs

"""
This is the code that will run the minimum swap algorithm a sufficient number of times
 to find the best path

 Speed Ups:
    Right now, the distance adjustments function doesn't change the time required for the total run.
        It actually increases it a little I think, at least for a strike count of 50. However,
        it does reduce the number of bad graphs per good graph from 26 to 10, which is a success.
        The next step will be to have it get better at reducing the distance. One way to do this
        might be to have it be able to move qubits to a different spot, instead of just swapping them.
"""
"""
Arguments: 
    First argument is the .txt or .qasm file
    All other arguments are flags for some or another functionality
"""



parser = argparse.ArgumentParser(
                    prog='PROGRAM NAME',
                    description='PROGRAM DESCRIPTION')

# Input graph arguments
parser.add_argument('-f', '--filename', default="graph.txt",
                    help="Name of the file listing which variables need to be entangled with each other. \n"
                    "(default: graph.txt)")
parser.add_argument('-thr', '--threeReg', default=-1, type=int,
                    help="The number of nodes in a random 3-regular graph that will be generated to "
                    "represent the variable graph. This option "
                    "will be used if a variable graph file is not provided and a valid number of nodes is given."
                    "(default: -1)")

# Lattice arguments
parser.add_argument('-a', '--architecture', choices=["Hex", "HHex"], default="HHex",
                    help="The physical structure of the qubit connections in the quantum computer. \n"
                    "Either \'Hex\' for hexagonal or \'HHex\' for a heavy hexagonal structure. \n"
                    "(default: HHex)")

# Optimization arguments
parser.add_argument('-i', '--iterations', default=1_000, type=int,
                    help="The number of attempts to find the minimum swap path.\n"
                    "(default: 1_000)")
parser.add_argument('-ies', '--init_entangles_frac', default=1.0, type=float,
                    help="When a candidate starting position is generated, a minimum "
                    "fraction of qubit pairs must be able to be entangled without using any "
                    "SWAP gates or free swaps. If not, a new starting position is generated.\n"
                    "This fraction is given by the value of this argument.\n"
                    "(default: 1.0)")
parser.add_argument('-gds', '--init_graph_dist', default=10_000, type=float,
                    help="When a candidate starting position is generated, the \'distance function\' "
                    "of the position is calculated. The distance function of the graph must be less than "
                    "the value of this argument to be accepted. If the candidate position has a distance "
                    "function greater than this value, a new candidate starting position is generated.\n"
                    "(default: 10_000)")
parser.add_argument('-nt', '--no_truncate', action='store_true', default=False,
                    help="If false, will stop solving the graph once the number of swaps in that solution."
                    "meets or exceeds the current minimum number of swaps. \n"
                    "(default: False)")

# Data analysis arguments
parser.add_argument('-v', '--verbose', action='store_true', default=False, 
                    help="If true, will display all graphs generated during the optimization process. \n"
                    "(default: False)")

args = parser.parse_args()
print(args.filename, args.threeReg, args.architecture, args.verbose)


"""
Creating Variable and Lattice Graphs
"""
# Create the variable graph
print("Creating variable graph...")

if args.filename == "graph.txt" and args.threeReg > 3:
    QUBO_Graph, num_nodes, num_edges, list_nodes = ofs.make_3reg_graph(args.threeReg)
elif args.filename != "graph.txt" and args.threeReg != -1:
    print("It seems that you have entered both a graph file and requested a random "
          "3-regular graph. You may only choose one of these options.")
    print("Exiting program...")
    quit()
else:
    try:
        QUBO_Graph, num_nodes, num_edges, list_nodes = ofs.make_qubo_graph(args.filename)
    except FileNotFoundError:
        print(f"The file {args.filename} was not found.\n")
        print("Exiting program...")


# Create the lattice graph
print("Creating lattice graph...")

# Graph info
# qubit: the number of the node of the QUBO graph that has been
#        placed at that node
lattice_Graph = ofs.import_lattice(args.architecture)


"""
Preparing Variable Graph
"""

print("Preprocessing the variable graph...")

# Graph info
# green: whether or not it is a green node
# placed: whether or not it has been put on the qubit lattice
# tail_start: whether it starts an end tail
# tail_end: whether it ends an end tail
# embedded: the number of the node on the lattice it is embedded at

QUBO_Graph = ofs.find_greens(QUBO_Graph)


"""
Performing the Optimization
"""

print("Beginning optimization\n\n")

start_time = time.perf_counter()

iterations = args.iterations

best_moves_list, best_moves_key, list_of_swap_nums, best_lattice_nodes, best_qubo_embed, iterations, graph_distance, init_entangles, ave_swap_list, attempts = ofs.iterate_through(lattice_Graph, 
                                                                                                                                                                                   QUBO_Graph, 
                                                                                                                                                                                   iterations, 
                                                                                                                                                                                   args.no_truncate, 
                                                                                                                                                                                   args.init_entangles_frac, 
                                                                                                                                                                                   args.init_graph_dist)

print()
print(f"Finished {args.iterations} iterations.\n")

"""
Display Solution Information
"""

# Clean up calculations
best_swap = len([key for key in best_moves_key if key == "s"])
ave_swaps = round(np.average(np.array(list_of_swap_nums)), 3)

end_time = time.perf_counter()
run_time = round(end_time - start_time, ndigits=2)

print(f"# of qubits: {num_nodes}")
print(f"# of entanglements: {num_edges}")
print(f"Runtime: {run_time} seconds")
print(f"Averaged runtime per trial: {round((run_time / iterations) * 1000, ndigits=3)} ms")
print(f"Minimum Swaps Needed: {best_swap}")
print()
print("Best Move List (move #, variables, action):")

for i, (move, key) in enumerate(zip(best_moves_list, best_moves_key)):
    if key == "g":
        print(f"{i}. {move} - Apply gate")
    elif key == "f":
        print(f"{i}. {move} - Apply gate with free swap")
    elif key == "s":
        print(f"{i}. {move} - Swap")
    else:
        print("Error")

# Reconstruct the solution with the fewest swaps
lattice_Graph = ofs.reconstruct_lattice(best_lattice_nodes, lattice_Graph)
QUBO_Graph = ofs.reconstruct_qubo(best_qubo_embed, QUBO_Graph)

# Color graphs
QUBO_Graph = ofs.color_graph(QUBO_Graph)
lattice_Graph = ofs.color_lattice(lattice_Graph, QUBO_Graph, args.architecture)

figure_q = gui_func.makeQUBOGraph(QUBO_Graph)
figure_q.show()

figure_l = gui_func.makeLatticePlot(lattice_Graph)
figure_l.show()

# Extra plots if wanted
if args.verbose:
    figure_hist = gui_func.makeSwapHist(list_of_swap_nums)
    figure_hist.show()

    init_ent_v_swap = gui_func.init_entangles_frac_v_swap_num(init_entangles, num_edges, ave_swap_list)
    init_ent_v_swap.show()

    graph_dist_v_ave_swaps = gui_func.graph_distance_v_ave_swaps(graph_distance, ave_swap_list)
    graph_dist_v_ave_swaps.show()

    attempts_hist = gui_func.makeAttemptHist(attempts)
    attempts_hist.show()




print("Press Enter to finish...")
input()
quit()


