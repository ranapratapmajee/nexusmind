# path: app/pipeline_registry.py

from typing import Dict, Optional
from langgraph.graph.state import CompiledStateGraph

class PipelineRegistry:
    """A simple look-up dictionary to store and retrieve compiled subgraphs."""
    
    def __init__(self) -> None:
        self._registry: Dict[str, CompiledStateGraph] = {}

    def register(self, key: str, compiled_graph: CompiledStateGraph) -> None:
        """Save a compiled subgraph under a string key."""
        self._registry[key] = compiled_graph

    def get(self, key: str) -> Optional[CompiledStateGraph]:
        """Fetch a compiled subgraph by its string key."""
        return self._registry.get(key)

# Global registry instance for easy import across the app
pipeline_registry = PipelineRegistry()