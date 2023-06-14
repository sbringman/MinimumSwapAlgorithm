#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  3 16:18:25 2023

@author: sambringman
"""

import main_gui
import pathfinder

gui = False
swap_algo = True


if gui:
    main_gui.main()
elif swap_algo:
    pathfinder.main()