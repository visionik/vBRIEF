"""
vBRIEF v0.5 DAG Validator

Validates directed acyclic graph (DAG) constraints for Plan edges:
- Detects cycles using DFS-based algorithm (O(V+E) complexity)
- Validates edge references point to existing items
- Supports hierarchical IDs with dot notation
"""

from typing import Dict, List, Set, Tuple, Optional
from enum import Enum


class ValidationError(Exception):
    """Raised when DAG validation fails."""
    pass


class EdgeType(str, Enum):
    """Core edge types defined in vBRIEF v0.5 specification."""
    BLOCKS = "blocks"
    INFORMS = "informs"
    INVALIDATES = "invalidates"
    SUGGESTS = "suggests"


class DAGValidator:
    """Validates DAG constraints for vBRIEF Plans."""
    
    def __init__(self, items: List[Dict], edges: List[Dict]):
        """
        Initialize validator.
        
        Args:
            items: List of PlanItem dictionaries
            edges: List of Edge dictionaries with 'from', 'to', 'type' fields
        """
        self.items = items
        self.edges = edges
        self.item_ids = self._collect_item_ids(items)
        self.graph = self._build_adjacency_list()
    
    def _collect_item_ids(self, items: List[Dict], prefix: str = "") -> Set[str]:
        """
        Recursively collect all item IDs including nested subItems.
        
        Args:
            items: List of PlanItem dictionaries
            prefix: Hierarchical prefix for nested items
            
        Returns:
            Set of all item IDs in the plan
        """
        ids = set()
        for item in items:
            item_id = item.get("id")
            if item_id:
                # Support hierarchical IDs
                full_id = f"{prefix}.{item_id}" if prefix else item_id
                ids.add(full_id)
                
                # Recursively process subItems
                sub_items = item.get("subItems", [])
                if sub_items:
                    ids.update(self._collect_item_ids(sub_items, full_id))
        
        return ids
    
    def _build_adjacency_list(self) -> Dict[str, List[str]]:
        """
        Build adjacency list representation of the graph.
        
        Returns:
            Dictionary mapping each node to its list of outgoing edges
        """
        graph = {item_id: [] for item_id in self.item_ids}
        
        for edge in self.edges:
            from_id = edge.get("from")
            to_id = edge.get("to")
            
            if from_id and to_id:
                if from_id not in graph:
                    graph[from_id] = []
                graph[from_id].append(to_id)
        
        return graph
    
    def validate_references(self) -> List[str]:
        """
        Validate that all edge references point to existing items.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        for i, edge in enumerate(self.edges):
            from_id = edge.get("from")
            to_id = edge.get("to")
            edge_type = edge.get("type")
            
            if not from_id:
                errors.append(f"Edge {i}: missing 'from' field")
            elif from_id not in self.item_ids:
                errors.append(f"Edge {i}: 'from' references non-existent item '{from_id}'")
            
            if not to_id:
                errors.append(f"Edge {i}: missing 'to' field")
            elif to_id not in self.item_ids:
                errors.append(f"Edge {i}: 'to' references non-existent item '{to_id}'")
            
            if not edge_type:
                errors.append(f"Edge {i}: missing 'type' field")
        
        return errors
    
    def detect_cycles(self) -> Optional[List[str]]:
        """
        Detect cycles using depth-first search.
        
        Returns:
            List of node IDs forming a cycle, or None if no cycle exists
        """
        # Track visit states: WHITE (unvisited), GRAY (visiting), BLACK (visited)
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {node: WHITE for node in self.graph}
        parent = {node: None for node in self.graph}
        
        def dfs(node: str) -> Optional[List[str]]:
            """
            DFS visit function.
            
            Args:
                node: Current node being visited
                
            Returns:
                Cycle path if found, None otherwise
            """
            color[node] = GRAY
            
            for neighbor in self.graph.get(node, []):
                # Skip neighbors not in the graph (validation handles this)
                if neighbor not in color:
                    continue
                
                if color[neighbor] == GRAY:
                    # Back edge found - cycle detected
                    # Reconstruct cycle path
                    cycle = [neighbor]
                    current = node
                    while current != neighbor:
                        cycle.append(current)
                        current = parent.get(current)
                        if current is None:
                            break
                    cycle.append(neighbor)
                    return list(reversed(cycle))
                
                if color[neighbor] == WHITE:
                    parent[neighbor] = node
                    cycle = dfs(neighbor)
                    if cycle:
                        return cycle
            
            color[node] = BLACK
            return None
        
        # Start DFS from all unvisited nodes
        for node in self.graph:
            if color[node] == WHITE:
                cycle = dfs(node)
                if cycle:
                    return cycle
        
        return None
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Perform complete DAG validation.
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Step 1: Validate edge references
        ref_errors = self.validate_references()
        errors.extend(ref_errors)
        
        # Step 2: Detect cycles (only if references are valid)
        if not ref_errors:
            cycle = self.detect_cycles()
            if cycle:
                cycle_str = " -> ".join(cycle)
                errors.append(f"Cycle detected: {cycle_str}")
        
        return (len(errors) == 0, errors)


def validate_plan_dag(plan: Dict) -> Tuple[bool, List[str]]:
    """
    Convenience function to validate a Plan's DAG.
    
    Args:
        plan: Plan dictionary with 'items' and optional 'edges' fields
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    items = plan.get("items", [])
    edges = plan.get("edges", [])
    
    # Empty edges is valid (no DAG constraints)
    if not edges:
        return (True, [])
    
    validator = DAGValidator(items, edges)
    return validator.validate()


if __name__ == "__main__":
    # Example usage
    import json
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python dag_validator.py <plan.vbrief.json>")
        sys.exit(1)
    
    with open(sys.argv[1], 'r') as f:
        doc = json.load(f)
    
    plan = doc.get("plan", {})
    is_valid, errors = validate_plan_dag(plan)
    
    if is_valid:
        print("✓ DAG is valid (no cycles, all references resolve)")
    else:
        print("✗ DAG validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
