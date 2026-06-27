# path: app/graphs/__init__.py

import os
import importlib
from pathlib import Path

# Automatically discover and register all scripts ending in _graph.py inside this directory
graphs_dir = Path(__file__).parent

for file in os.listdir(graphs_dir):
    if file.endswith("_graph.py") and not file.startswith("__"):
        module_name = file[:-3]  # Strip out .py extension
        # Dynamically import the file which triggers its internal registry setup hook
        importlib.import_module(f"app.graphs.{module_name}")