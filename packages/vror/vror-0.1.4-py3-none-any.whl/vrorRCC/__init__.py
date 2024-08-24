# vror/__init__.py

"""
VROR: A package for solving various optimization problems.

Modules:
- CPM: Critical Path Method
- Graphical Method: Linear Programming via Graphical Methods
- Simplex Method: Linear Programming via Simplex Method
- Transportation: Solve Transportation Problems
- Assignment: Solve Assignment Problems
"""

from .cpm import create_graph, add_event, find_critical_path, visualize_graph
from .graphical_method import graphical_method
from .simplex_method import simplex
from .transportation import transportation
from .assignment import assignment
