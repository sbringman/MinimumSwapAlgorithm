# Minimum Swap Algorithm

This program finds the minimum swaps to entangle qubits to solve a QUBO problem.

## Outline of the Algorithm

## Definitions: 
* QUBO graph - A graph where the nodes are the variables in the QUBO and the edges are the entanglements needed to solve the QUBO.
* Qubit lattice - The graph depicting the qubits on the quantum computer and the connections between them
* Qubit tail - A chain of nodes in the QUBO graph starting with a node of degree 1 and continuing along neighboring nodes until it reaches a node of degree greater than 2. That node is not counted as part of the chain.
* Connecting node - The node where qubit tail attaches to the main QUBO graph

## Algorithm

### Preparation:
1. A path is labelled on the lattice graph forming a spiral out from the center. The first set of qubits will be placed onto the lattice graph along this path.

### Placement
1. Place a random qubit from the QUBO graph that is not part of a qubit tail onto the first node in the path.
2. Get a list of the unplaced neighbors of the last qubit placed. Place a random qubit from this list and place it onto the next node in the path. If there are no unplaced neighbors, place a random unplaced qubit from the QUBO graph onto the lattice on the next node of the path.
3. Repeat step 3 until all the qubits that are not part of a qubit tail are placed.
4. Pick one qubit tail at random. Attempt to place the tail onto the lattice as a neighbor of its connecting node. If that is not possible, place the qubit tail as close as possible to the connecting node. Repeat this for all qubit tails

### Swapping
1. Make a list of all the entanglments that need to be done, keeping track of which entanglement has the shortest path between qubits.
2. Perform the swaps of the shortest path and entangle
3. Repeat steps 1 and 2

### Repeat
 1. Once a list of swaps has been made that will entangle every qubit that needs to be entangled, record the number of swaps it took.
 2. Repeat the entire process from the start for many iterations, keeping track of which initial placement and swap list gives the minimum number of swaps.

### Speed Up Notes
* If a graph has done an equal number or more swaps than the best solution found so far, that attempt is immediately stopped and a new attempt started.
* If an entanglement has a path length of three, i.e., if there is only one qubit between two qubits that need to be entangled, immediately choose that swap path. That is the shortest possible path.





