#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed July 12th

@author: sambringman
"""

import gurobipy as gb

m = gb.Model("mipl")

# Create variables
x = m.addVar(vtype=gb.GRB.BINARY, name="x")
y = m.addVar(vtype=gb.GRB.BINARY, name="y")
z = m.addVar(vtype=gb.GRB.BINARY, name="z")

# Must call update to add the variables in
m.update()

# Set objective function
m.setObjective(x + y + 2*z, gb.GRB.MAXIMIZE)

# Add Constraints
m.addConstr(x + 2*y + 3*z <= 4, "c0")
m.addConstr(x + y >= 1, "c1")

m.optimize()
m.printAttr("x")

# Tuplelist data type
arcs = gb.tuplelist([('CHI', 'NYC'), ('CHI', 'ATL'), ('ATL', 'MIA'), ('ATL', 'NYC')])

# Each of these tuples in the list is a key in a dictionary that keys to an interger value
# The select() method finds matching subsets
print(arcs.select('CHI', '*'))
# [('CHI', 'NYC'), ('CHI', 'ATL')]

