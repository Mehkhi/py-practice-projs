"""Map connectivity analysis utilities.

This module provides functions to analyze the structure and connectivity
of maps in the world, including building connection graphs and identifying
dead ends, disconnected maps, and orphaned maps.
"""

from typing import Dict, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .world import World


def get_map_graph(world: "World") -> Dict[str, List[Tuple[str, bool]]]:
    """
    Build a directed graph of map connections from warps.

    Returns:
        Dictionary mapping source map_id to list of (target_map_id, is_conditional) tuples.
        is_conditional is True if the warp has requires_flag, requires_item, or blocked_by_flag.
    """
    graph: Dict[str, List[Tuple[str, bool]]] = {}

    for map_id, map_obj in world.maps.items():
        connections: List[Tuple[str, bool]] = []
        for warp in map_obj.warps:
            # Skip warps to non-existent maps
            if warp.target_map_id not in world.maps:
                continue

            # Check if warp is conditional
            is_conditional = bool(
                warp.requires_flag or warp.requires_item or warp.blocked_by_flag
            )

            connections.append((warp.target_map_id, is_conditional))

        graph[map_id] = connections

    return graph


def analyze_map_connectivity(
    world: "World", start_map_id: str = "forest_path"
) -> Tuple[List[str], List[str], List[str], Dict[str, List[Tuple[str, bool]]]]:
    """
    Analyze map connectivity to identify dead ends, disconnected maps, and orphaned maps.

    Args:
        world: The World instance to analyze
        start_map_id: The starting map for reachability analysis (default: "forest_path")

    Returns:
        Tuple of (dead_ends, disconnected, orphaned, graph):
        - dead_ends: Maps with no outgoing warps (or only conditional warps)
        - disconnected: Maps unreachable from start_map_id
        - orphaned: Maps that exist but aren't referenced by any warp's target_map_id
                    (excludes start_map_id since it's the entry point)
        - graph: The map connectivity graph
    """
    graph = get_map_graph(world)

    # Find all maps referenced as warp targets
    referenced_maps: set = set()
    for connections in graph.values():
        for target_map_id, _ in connections:
            referenced_maps.add(target_map_id)

    # Find orphaned maps (exist but never referenced)
    # Exclude start_map_id since it's the entry point and expected to not be referenced
    all_maps = set(world.maps.keys())
    orphaned = sorted(all_maps - referenced_maps - {start_map_id})

    # Find dead ends (maps with no outgoing warps, or only conditional warps)
    dead_ends: List[str] = []
    for map_id, connections in graph.items():
        if not connections:
            # No outgoing warps at all
            dead_ends.append(map_id)
        else:
            # Check if all warps are conditional
            all_conditional = all(is_conditional for _, is_conditional in connections)
            if all_conditional:
                dead_ends.append(map_id)

    # Find disconnected maps (unreachable from start_map_id)
    disconnected: List[str] = []
    if start_map_id in world.maps:
        # BFS to find all reachable maps
        visited: set = set()
        queue: List[str] = [start_map_id]
        visited.add(start_map_id)

        while queue:
            current = queue.pop(0)
            if current in graph:
                for target_map_id, is_conditional in graph[current]:
                    # Only follow non-conditional warps for reachability
                    # (conditional warps may never be accessible)
                    if not is_conditional and target_map_id not in visited:
                        visited.add(target_map_id)
                        queue.append(target_map_id)

        # All maps not visited are disconnected
        disconnected = sorted(all_maps - visited)
    else:
        # Start map doesn't exist, all maps are disconnected
        disconnected = sorted(all_maps)

    return (sorted(dead_ends), disconnected, orphaned, graph)
