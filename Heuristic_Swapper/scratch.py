"""
Created on Sun Nov. 19

@author: sambringman
"""

from pandas import read_csv
import networkx as nx
import matplotlib.pyplot as plt

Heavy_Hex_nodes_filepath = "./Heuristic_Swapper/Heavy_Hex_Nodes.txt"
Heavy_Hex_edges_filepath = "./Heuristic_Swapper/Heavy_Hex_Edges.txt"

# This makes the qubit lattice from an imported file
def import_lattice():
    # This will just be a premade lattice with a certain number of qubits


    lattice_node_info = read_csv(Heavy_Hex_nodes_filepath, skiprows=1)
    lattice_edges_info = read_csv(Heavy_Hex_edges_filepath, skiprows=1)

    lattice_graph = nx.Graph()

    for index, row in lattice_node_info.iterrows():

        lattice_graph.add_node(index, qubit=-1)

    for index, row in lattice_edges_info.iterrows():

        lattice_graph.add_edge(row['Node1'], row['Node2'])
    
    return lattice_graph



HH_Lattice = import_lattice()
lattice_node_info = read_csv(Heavy_Hex_nodes_filepath, skiprows=1)
for index, row in lattice_node_info.iterrows():
        HH_Lattice.nodes[index]['pos'] = (row['x_coor'], row['y_coor'])

nx.draw_networkx(HH_Lattice, pos=HH_Lattice.nodes.data('pos'))
#plt.savefig("Heavy Hex Spiral", dpi=2400)
