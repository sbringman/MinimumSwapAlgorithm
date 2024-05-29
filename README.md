# MinimumSwapAlgorithm
A program that maps a QUBO to a lattice of quantum bits and attempts to find the minimum number of SWAP gates needed to complete all entanglements

We used two methods to find the minimum swap gates for a given quantum circuit. First, a SAT model that solved the problem exactly using Gurobi software. Second, a heuristics based model that found approximate solutions using a hand made algorithm of applied rules.

Further information on both models can be found in their respective summary documents in this folder.

# Use
The main file can be run in the terminal with the command ```python main.py``` followed by any needed arguments. The usage is as follows: 
```

usage: PROGRAM NAME [-h] [-f FILENAME] [-thr THREEREG] [-a {Hex,HHex}] [-i ITERATIONS]
                    [-ies INIT_ENTANGLES_FRAC] [-gds INIT_GRAPH_DIST] [-nt] [-v]

options:
  -h, --help            show this help message and exit
  -f FILENAME, --filename FILENAME
                        Name of the file listing which variables need to be entangled with each other.
                        (default: graph.txt)
  -thr THREEREG, --threeReg THREEREG
                        The number of nodes in a random 3-regular graph that will be generated to
                        represent the variable graph. This option will be used if a variable graph file
                        is not provided and a valid number of nodes is given.(default: -1)
  -a {Hex,HHex}, --architecture {Hex,HHex}
                        The physical structure of the qubit connections in the quantum computer. Either
                        'Hex' for hexagonal or 'HHex' for a heavy hexagonal structure. (default: HHex)
  -i ITERATIONS, --iterations ITERATIONS
                        The number of attempts to find the minimum swap path. (default: 1_000)
  -ies INIT_ENTANGLES_FRAC, --init_entangles_frac INIT_ENTANGLES_FRAC
                        When a candidate starting position is generated, a minimum fraction of qubit
                        pairs must be able to be entangled without using any SWAP gates or free swaps. If
                        not, a new starting position is generated. This fraction is given by the value of
                        this argument. (default: 1.0)
  -gds INIT_GRAPH_DIST, --init_graph_dist INIT_GRAPH_DIST
                        When a candidate starting position is generated, the 'distance function' of the
                        position is calculated. The distance function of the graph must be less than the
                        value of this argument to be accepted. If the candidate position has a distance
                        function greater than this value, a new candidate starting position is generated.
                        (default: 10_000)
  -nt, --no_truncate    If false, will stop solving the graph once the number of swaps in that
                        solution.meets or exceeds the current minimum number of swaps. (default: False)
  -v, --verbose         If true, will display all graphs generated during the optimization process.
                        (default: False)
```
