# Minimum Swap Algorithm

This program finds the minimum swaps to entangle qubits to solve a QUBO problem.

## Definitions: 
* QUBO graph - A graph where the nodes are the variables in the QUBO and the edges are the entanglements needed to solve the QUBO.
* Qubit lattice - The graph depicting the qubits on the quantum computer and the connections between them
* Qubit tail - A chain of nodes in the QUBO graph starting with a node of degree 1 and continuing along neighboring nodes until it reaches a node of degree greater than 2. That node is not counted as part of the chain.
* Connecting node - The node where qubit tail attaches to the main QUBO graph
* Swap Path - The sequence of swaps from the initial mapping to the final position where all qubits that need to be entangled have been entangled
* Distance function of graph - This is the total sum of the distances on the lattice between each pair of qubits that needs to be entangled.
* Distance function of a qubit - This is the total sum of the distances on the lattice between that qubit and all the other qubits that it needs to be entangled with.

## Algorithm

### Preparation:
1. A path is labelled on the lattice graph forming a spiral out from the center. The first set of qubits will be placed onto the lattice graph along this path.
2. The shortest path from any node on the lattice to any other node on the lattice is computed. This is saved for reference later, and doesn't change when the qubits are placed.

### Placement
1. Place a random qubit from the QUBO graph that is not part of a qubit tail onto the first node in the path.
2. Get a list of the unplaced neighbors of the last qubit placed. Place a random qubit from this list and place it onto the next node in the path. If there are no unplaced neighbors, place a random unplaced qubit from the QUBO graph onto the lattice on the next node of the path.
3. Repeat step 3 until all the qubits that are not part of a qubit tail are placed.
4. Pick one qubit tail at random. Attempt to place the tail onto the lattice as a neighbor of its connecting node. If that is not possible, place the qubit tail as close as possible to the connecting node. Repeat this for all qubit tails

### Check Graph
1. Do all the entanglements that are possible just from the initial state of the graph.
2. Pick two random qubits on the graph. If it would lower the distance function of the graph to swap them, do so. Continue to do this until there 50 qubit pairs in a row are checked that would not lower the distance function of the graph if swapped. The value of 50 was picked by experimenting with various numbers and choosing the one that lowered the average amount of bad graphs generated before a useful graph was found without increasing the time the total program took to run.
3. Find how many entanglements are achieved without moving any of the qubits. If this number is less than half the total number of entanglements, regenerate the graph. Find the total distance function of the graph. If this number is greater than 1.5 * total number of entanglements needed, then regenerate the graph. This metric assumes that at least half of the original entanglements have already been done, and that the remaining entanglements will average about 3 swaps per entanglement. Both of these conditions are based on graphing total number of swaps v. initial entanglements/initial distance function and selecting a cutoff point that retains all the best solutions while removing initial conditions that virtually always give sub optimal solutions.

### Swapping
1. Make a list of all the entanglments that need to be done, keeping track of which entanglements have the shortest path between qubits.
2. Randomly choose a swap from the list of swaps that have the shortest path length. A path between the two qubits is found using the astar function in the networkx package.
3. The distance function of each qubit is evaluated before and after the first swap it would make towards the other one. The qubit with the smallest change in its distance function is moved, with ties going to the secodn qubit.
4. Continue evaluating the distance function for each qubit, swapping the one with the smallest change, until the two qubits are neighbors on the lattice and can be entangled.

### Repeat
 1. Once a list of swaps has been made that will entangle every qubit that needs to be entangled, record the number of swaps it took.
 2. Reset the graph back to the way it was before the swapping started. This graph already passed the initial entanglements test, so it has a good chance at getting a low total swap number. Repeat the swapping process 20 times. Because the swap process is randomized, the same starting condition should provide different swap paths, and this graphs are worth investigating.
 3. After running the same graph 10 times (less if the total number of iterations is small), repeat from the beginning with a fresh mapping. Continue to run the program until a set number of iterations has been finished

### Speed Up Notes
* If a graph has done an equal number or more swaps than the best solution found so far, that attempt is immediately stopped and a new attempt started.






