# MinimumSwapAlgorithm
A program that maps a QUBO to a lattice of quantum bits and attempts to find the minimum number of SWAP gates needed to complete all entanglements

We used two methods to find the minimum swap gates for a given quantum circuit. First, a SAT model that solved the problem exactly using Gurobi software. Second, a heuristics based model that found approximate solutions using a hand made algorithm of applied rules.

Further information on both models can be found in their respective summary documents in this folder.
