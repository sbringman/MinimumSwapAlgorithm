# Minimum Swap Algorithm

This program finds the minimum swaps to entangle qubits to solve a QUBO problem.

## Outline of the Algorithm

## Definitions: 
* QUBO graph - A graph where the nodes are the variables in the QUBO and the edges are the entanglements needed to solve the QUBO.
* Qubit lattice - The graph depicting the qubits on the quantum computer and the connections between them
* Qubit tail - A chain of nodes in the QUBO graph starting with a node of degree 1 and continuing along neighboring nodes until it reaches a node of degree greater than 2. That node is not counted as part of the chain.
* Connecting node - The node where qubit tail attaches to the main QUBO graph
* Swap Path - The sequence of swaps from the initial mapping to the final position where all qubits that need to be entangled have been entangled

## Algorithm

### Preparation:
1. A path is labelled on the lattice graph forming a spiral out from the center. The first set of qubits will be placed onto the lattice graph along this path.

### Placement
1. Place a random qubit from the QUBO graph that is not part of a qubit tail onto the first node in the path.
2. Get a list of the unplaced neighbors of the last qubit placed. Place a random qubit from this list and place it onto the next node in the path. If there are no unplaced neighbors, place a random unplaced qubit from the QUBO graph onto the lattice on the next node of the path.
3. Repeat step 3 until all the qubits that are not part of a qubit tail are placed.
4. Pick one qubit tail at random. Attempt to place the tail onto the lattice as a neighbor of its connecting node. If that is not possible, place the qubit tail as close as possible to the connecting node. Repeat this for all qubit tails

### Check Graph
1. Do all the entanglements that are possible just from the initial state of the graph.
2. If the number of entanglements left is more than half the total entanglements, then scrap the graph and start again. Continue to generate graphs until you get a graph that can do at least half the entanglements in the initial mapping. This process is useful because the most successful swap paths always start with a high number of initial swaps.
3. If the graph has a high enough initial entanglement count, then make a copy of the graph and proceed.

### Swapping
1. Make a list of all the entanglments that need to be done, keeping track of which entanglements have the shortest path between qubits.
2. Randomly choose a swap from the list of swaps that have the hortest path length
3. Perform the swaps and entangle
4. Repeat steps 1 - 3

### Repeat
 1. Once a list of swaps has been made that will entangle every qubit that needs to be entangled, record the number of swaps it took.
 2. Reset the graph back to the way it was before the swapping started. This graph already passed the initial entanglements test, so it has a good chance at getting a low total swap number. Repeat the swapping process 20 times. Because the swap process is randomized, the same starting condition should provide different swap paths, and this graphs are worth investigating.
 3. After running the same graph 20 times, repeat from the beginning with a fresh mapping. Continue to run the program until a set number of iterations has been finished

### Speed Up Notes
* If a graph has done an equal number or more swaps than the best solution found so far, that attempt is immediately stopped and a new attempt started.
* Only graphs that show promise are investigated






