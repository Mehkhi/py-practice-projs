#!/usr/bin/env python3
"""Command-line tool to visualize map connectivity graph."""

import argparse
import json
import os
import sys
from typing import Dict, List, Tuple

# Add parent directory to path to import core modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.world import load_world_from_data, analyze_map_connectivity, get_map_graph


def format_text_output(
    dead_ends: List[str],
    disconnected: List[str],
    orphaned: List[str],
    graph: Dict[str, List[Tuple[str, bool]]],
    start_map_id: str,
) -> str:
    """Generate text-based graph representation."""
    lines: List[str] = []

    lines.append("=" * 70)
    lines.append("Map Connectivity Analysis")
    lines.append("=" * 70)
    lines.append(f"Starting map: {start_map_id}")
    lines.append("")

    # Graph representation
    lines.append("Map Connections:")
    lines.append("-" * 70)
    for source_map in sorted(graph.keys()):
        connections = graph[source_map]
        if connections:
            for target_map, is_conditional in connections:
                conditional_marker = " [CONDITIONAL]" if is_conditional else ""
                lines.append(f"  {source_map} -> {target_map}{conditional_marker}")
        else:
            lines.append(f"  {source_map} -> (no exits)")
    lines.append("")

    # Dead ends
    if dead_ends:
        lines.append("Dead Ends (maps with no exits or only conditional exits):")
        lines.append("-" * 70)
        for map_id in dead_ends:
            lines.append(f"  - {map_id}")
        lines.append("")
    else:
        lines.append("No dead ends found.")
        lines.append("")

    # Disconnected maps
    if disconnected:
        lines.append(f"Disconnected Maps (unreachable from {start_map_id}):")
        lines.append("-" * 70)
        for map_id in disconnected:
            lines.append(f"  - {map_id}")
        lines.append("")
    else:
        lines.append(f"All maps are reachable from {start_map_id}.")
        lines.append("")

    # Orphaned maps
    if orphaned:
        lines.append("Orphaned Maps (never referenced as warp targets):")
        lines.append("-" * 70)
        for map_id in orphaned:
            lines.append(f"  - {map_id}")
        lines.append("")
    else:
        lines.append("No orphaned maps found.")
        lines.append("")

    lines.append("=" * 70)

    return "\n".join(lines)


def format_dot_output(
    graph: Dict[str, List[Tuple[str, bool]]],
    dead_ends: List[str],
    disconnected: List[str],
) -> str:
    """Generate Graphviz DOT format output."""
    lines: List[str] = []

    lines.append("digraph MapConnectivity {")
    lines.append("  rankdir=LR;")
    lines.append("  node [shape=box, style=rounded];")
    lines.append("")

    # Define all nodes with styling
    all_maps = set(graph.keys())
    for target_list in graph.values():
        for target_map, _ in target_list:
            all_maps.add(target_map)

    for map_id in sorted(all_maps):
        style_attrs = []
        if map_id in dead_ends:
            style_attrs.append('color=red')
        if map_id in disconnected:
            style_attrs.append('style=dashed')

        attrs_str = f" [{', '.join(style_attrs)}]" if style_attrs else ""
        lines.append(f'  "{map_id}"{attrs_str};')

    lines.append("")

    # Add edges
    for source_map in sorted(graph.keys()):
        for target_map, is_conditional in graph[source_map]:
            edge_attrs = []
            if is_conditional:
                edge_attrs.append('style=dashed')
                edge_attrs.append('color=gray')

            attrs_str = f" [{', '.join(edge_attrs)}]" if edge_attrs else ""
            lines.append(f'  "{source_map}" -> "{target_map}"{attrs_str};')

    lines.append("}")

    return "\n".join(lines)


def format_json_output(
    dead_ends: List[str],
    disconnected: List[str],
    orphaned: List[str],
    graph: Dict[str, List[Tuple[str, bool]]],
) -> str:
    """Generate JSON format output."""
    # Convert graph to JSON-serializable format
    graph_json = {}
    for source_map, connections in graph.items():
        graph_json[source_map] = [
            {"target": target, "conditional": is_conditional}
            for target, is_conditional in connections
        ]

    output = {
        "dead_ends": dead_ends,
        "disconnected": disconnected,
        "orphaned": orphaned,
        "graph": graph_json,
    }

    return json.dumps(output, indent=2)


def main():
    """Main entry point for the visualization tool."""
    parser = argparse.ArgumentParser(
        description="Visualize map connectivity graph"
    )
    parser.add_argument(
        "--format",
        choices=["text", "dot", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--start-map",
        default="forest_path",
        help="Starting map for reachability analysis (default: forest_path)",
    )
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Data directory containing maps (default: data)",
    )

    args = parser.parse_args()

    # Load world
    try:
        world = load_world_from_data(args.data_dir)
    except Exception as e:
        print(f"Error loading world: {e}", file=sys.stderr)
        sys.exit(1)

    if not world.maps:
        print("No maps loaded.", file=sys.stderr)
        sys.exit(1)

    # Analyze connectivity
    dead_ends, disconnected, orphaned, graph = analyze_map_connectivity(
        world, args.start_map
    )

    # Generate output
    if args.format == "text":
        output = format_text_output(dead_ends, disconnected, orphaned, graph, args.start_map)
    elif args.format == "dot":
        output = format_dot_output(graph, dead_ends, disconnected)
    elif args.format == "json":
        output = format_json_output(dead_ends, disconnected, orphaned, graph)

    print(output)


if __name__ == "__main__":
    main()
