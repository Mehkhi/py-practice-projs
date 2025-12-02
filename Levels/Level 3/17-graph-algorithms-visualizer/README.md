# Graph Algorithms Visualizer

An interactive Python application for visualizing and analyzing graph algorithms including BFS/DFS traversals, Dijkstra's shortest paths, A* search with heuristics, and comprehensive performance benchmarking.

## Features

### Required Features ✅
- **R1. Graph Ingestion (2/5)** - Load graphs from edge list files with validation
- **R2. BFS/DFS Traversals (2/5)** - Implement breadth-first and depth-first search
- **R3. Shortest Paths (Dijkstra) (3/5)** - Dijkstra's algorithm with priority queue
- **R4. Drawing (2/5)** - Graph visualization with matplotlib and highlighting

### Bonus Features ✅
- **B1. Interactive GUI (3/5)** - PySimpleGUI-based interactive visualizer
- **B2. A* Heuristic (3/5)** - A* algorithm with Euclidean distance heuristic
- **B3. Performance Benchmarking (2/5)** - Comprehensive algorithm benchmarking

## Installation

1. Clone or download the project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Command Line Interface

```bash
# Create a sample graph file
python main.py create-sample

# Demonstrate BFS/DFS traversals
python main.py demo-traversal sample_graph.txt

# Demonstrate shortest path algorithms
python main.py demo-paths sample_graph.txt

# Demonstrate visualization
python main.py demo-viz sample_graph.txt

# Run performance benchmarks
python main.py benchmark

# Launch interactive GUI
python main.py gui
```

### Interactive GUI

The GUI provides:
- **Load Graph**: Browse and load graph files
- **Algorithm Selection**: Choose from BFS, DFS, Dijkstra, A*
- **Step-through Execution**: Run algorithms step by step
- **Animation**: Play/pause with adjustable speed
- **Real-time Visualization**: See algorithm progress on graph
- **Output Log**: Track algorithm execution and results

### Graph File Format

Graphs are loaded from text files with one edge per line:
```
node1 node2 [weight]
```

Example:
```
A B 4.0
A C 2.0
B C 1.0
C D 8.0
D E 2.0
```

- Weights are optional (default: 1.0)
- Lines starting with # are comments
- Invalid edges are reported but don't stop loading

## Algorithms Implemented

### BFS/DFS Traversals
- **BFS**: Breadth-first search using queue (O(V + E))
- **DFS**: Depth-first search using stack (O(V + E))
- Handles disconnected graphs
- Returns visitation order and parent pointers

### Shortest Path Algorithms
- **Dijkstra**: Priority queue implementation (O((V + E) log V))
- **A***: Heuristic search with configurable heuristics
- Supports negative weight detection
- Euclidean distance heuristic for geometric graphs

### Visualization
- Matplotlib-based graph drawing
- Highlight nodes and edges in red
- Multiple layout options (spring, circular, random)
- High-DPI PNG export
- Edge weight labels

## Benchmarking

Comprehensive performance analysis:
- **Graph Sizes**: 10 to 100 nodes
- **Densities**: 0.1 to 0.5 edge probability
- **Algorithms**: BFS, DFS, Dijkstra, A* (zero and heuristic)
- **Metrics**: Mean execution time with standard deviation
- **Visualization**: Performance plots and analysis

Run benchmarks:
```bash
python main.py benchmark
```

Results saved to `output/` directory.

## Project Structure

```
├── main.py                 # Command-line interface
├── gui.py                  # Interactive GUI application
├── graph_ingestion.py      # Graph loading and validation
├── traversals.py          # BFS/DFS implementations
├── shortest_paths.py      # Dijkstra and A* algorithms
├── visualization.py       # Graph drawing utilities
├── benchmark.py           # Performance benchmarking
├── requirements.txt       # Python dependencies
├── CHECKLIST.md          # Implementation checklist
├── SPEC.md               # Detailed specifications
├── README.md             # This file
└── output/               # Generated visualizations and reports
```

## Technical Details

- **Python 3.8+** required
- **NetworkX** for graph data structures
- **Matplotlib** for visualization
- **PySimpleGUI** for GUI (bonus feature)
- All algorithms tested against NetworkX reference implementations
- Comprehensive error handling and input validation

## Educational Value

This project demonstrates:
- Graph algorithm implementation
- Data structure usage (queues, stacks, heaps)
- Algorithm analysis and Big-O complexity
- Interactive GUI development
- Performance benchmarking techniques
- Code organization and testing

## License

This project is educational and for demonstration purposes.
