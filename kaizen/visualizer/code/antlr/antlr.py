# import networkx as nx
# import matplotlib.pyplot as plt

# def extract_relationships(tree):
#     graph = nx.DiGraph()
    
#     # Example traversal logic (pseudo-code)
#     for node in tree.children:
#         if isinstance(node, FunctionDef):  # Adjust based on actual node types
#             graph.add_node(node.name)
#             for call in node.calls:  # Assume 'calls' contains called functions
#                 graph.add_edge(node.name, call.name)  # Function -> Called Function
    
#     return graph

# def visualize_graph(graph):
#     pos = nx.spring_layout(graph)  # Choose layout
#     nx.draw(graph, pos, with_labels=True, node_size=2000, node_color='lightblue')
#     plt.title('Code Structure Visualization')
#     plt.show()

# # Example usage after extracting relationships
# graph = extract_relationships(parse_tree)
# visualize_graph(graph)

import subprocess
import os
import antlr4
from antlr4 import FileStream, CommonTokenStream
from Grammar.Python3Lexer import Python3Lexer
from Grammar.Python3Parser import Python3Parser
import networkx as nx
import matplotlib.pyplot as plt

def generate_antlr_files(grammar_file):
    antlr_jar_path = 'antlr-4.13.2-complete.jar'  # Update this path to your ANTLR jar file
    command = ['java', '-jar', antlr_jar_path, grammar_file]

    try:
        subprocess.run(command, check=True)
        print(f'Successfully generated lexer and parser from {grammar_file}')
    except subprocess.CalledProcessError as e:
        print(f'Error generating files: {e}')

def parse_python_code(file_path):
    input_stream = FileStream(file_path)
    lexer = Python3Lexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = Python3Parser(token_stream)
    
    # Parse starting from the 'file_input' rule (entry point)
    tree = parser.file_input()
    
    return tree

def extract_relationships(tree):
    graph = nx.DiGraph()
    
    # Example traversal logic (pseudo-code)
    for node in tree.children:
        if isinstance(node, antlr4.tree.Tree.TerminalNodeImpl):  # Adjust based on actual node types
            continue  # Skip terminal nodes for this example
        
        if hasattr(node, 'name'):  # Check if the node has a name attribute
            graph.add_node(node.name)  # Add node with its name
        
        # Example: Add edges based on function calls (pseudo-code)
        if hasattr(node, 'calls'):  # This is hypothetical; adjust based on actual structure
            for call in node.calls:  # Assume 'calls' contains called functions
                graph.add_edge(node.name, call.name)  # Function -> Called Function
    
    return graph

def visualize_graph(graph):
    pos = nx.spring_layout(graph)  # Choose layout
    nx.draw(graph, pos, with_labels=True, node_size=2000, node_color='lightblue')
    plt.title('Code Structure Visualization')
    plt.show()

def main():
    # Define the grammar files for Python
    grammar_files = [
        'Python3Lexer.g4',
        'Python3Parser.g4'
    ]

    # Change directory to where your grammar files are located
    os.chdir('C:\\Users\\swapn\\Desktop\\visualizer\\code\\antlr\\Grammar')  # Update this path

    # Generate lexer and parser for each grammar file
    for grammar_file in grammar_files:
        generate_antlr_files(grammar_file)

    # Parse the example Python code file
    parse_tree = parse_python_code('C:\\Users\\swapn\\Desktop\\visualizer\\sample\\examples.py')  # Update this path to your example.py

    # Extract relationships and create a graph
    graph = extract_relationships(parse_tree)

    # Visualize the graph
    visualize_graph(graph)

if __name__ == '__main__':
    main()