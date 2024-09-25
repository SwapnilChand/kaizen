import os
import ast
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# Define a color palette for different node types
node_colors = {
    'imports': '#AED6F1',  # Light blue
    'global_variables': '#A2D9CE',  # Light green
    'functions': '#F9E79F',  # Light yellow
    'async_functions': '#F5CBA7',  # Light orange
    'classes': '#D7BDE2',  # Light purple
    'components': '#F5B7B1',  # Light pink
    'hooks': '#FADBD8',  # Light coral
    'type_definitions': '#D5DBDB',  # Light gray
}

class CodeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.graph = nx.DiGraph()  # Directed graph for code relationships
        self.node_colors = {}  # Store color for each node

    def visit_ClassDef(self, node):
        # Add class to the graph
        self.graph.add_node(node.name, type='class')
        self.node_colors[node.name] = node_colors['classes']  # Set class color
        
        # Add functions within the class
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self.graph.add_node(item.name, type='function')
                self.graph.add_edge(node.name, item.name)
                self.node_colors[item.name] = node_colors['functions']  # Set function color
                self.generic_visit(item)

    def visit_FunctionDef(self, node):
        # Add the function to the graph
        self.graph.add_node(node.name, type='function')
        self.node_colors[node.name] = node_colors['functions']  # Set function color

        # Add function arguments to the graph
        for arg in node.args.args:
            self.graph.add_node(arg.arg, type='arg')
            self.graph.add_edge(node.name, arg.arg)
            self.node_colors[arg.arg] = node_colors['global_variables']  # Set argument color
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        # Add async function to the graph
        self.graph.add_node(node.name, type='async_function')
        self.node_colors[node.name] = node_colors['async_functions']  # Set async function color
        self.generic_visit(node)

def visualize_static(code_path, all_files_directory=None):
    """ Visualize a single Python file's structure. """
    
    # Step 1: Parse and visualize the selected file
    with open(code_path, 'r') as file:
        tree = ast.parse(file.read())
        visitor = CodeVisitor()
        visitor.visit(tree)

    # If the entire codebase is provided, analyze other files too (but don't highlight them)
    if all_files_directory:
        for filename in os.listdir(all_files_directory):
            if filename.endswith('.py') and filename != os.path.basename(code_path):
                file_path = os.path.join(all_files_directory, filename)
                with open(file_path, 'r') as other_file:
                    other_tree = ast.parse(other_file.read())
                    visitor.visit(other_tree)

    # Step 2: Generate layout for the graph
    pos = nx.spring_layout(visitor.graph, k=0.5)  # Adjust k for spacing

    # Step 3: Prepare the plot
    plt.figure(figsize=(12, 8))

    # Draw edges (relationships between classes/functions/variables)
    nx.draw_networkx_edges(visitor.graph, pos, edge_color='gray', alpha=0.5)

    # Draw nodes and highlight the selected file
    node_colors_list = [visitor.node_colors.get(node, 'lightgray') for node in visitor.graph.nodes()]
    nx.draw_networkx_nodes(visitor.graph, pos, node_color=node_colors_list, node_size=2000, alpha=0.9)

    # Add labels (class/function names)
    nx.draw_networkx_labels(visitor.graph, pos, font_size=10, font_color='black')

    # Step 4: Add title
    plt.title(f'Visualization for {os.path.basename(code_path)}', fontsize=15)

    # Step 5: Create a color legend showing the entire palette
    legend_elements = [
        Patch(facecolor=node_colors['classes'], edgecolor='black', label='Classes'),
        Patch(facecolor=node_colors['functions'], edgecolor='black', label='Functions'),
        Patch(facecolor=node_colors['async_functions'], edgecolor='black', label='Async Functions'),
        Patch(facecolor=node_colors['global_variables'], edgecolor='black', label='Global Variables'),
        Patch(facecolor=node_colors['imports'], edgecolor='black', label='Imports'),
        Patch(facecolor=node_colors['components'], edgecolor='black', label='Components'),
        Patch(facecolor=node_colors['hooks'], edgecolor='black', label='Hooks'),
        Patch(facecolor=node_colors['type_definitions'], edgecolor='black', label='Type Definitions'),
    ]
    plt.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(0.5, -0.1),
               fancybox=True, shadow=True, ncol=4)

    # Step 6: Save and show the plot
    plt.savefig('code_structure_visualization.png', format='png', bbox_inches='tight')
    plt.show()

# Example usage:
# Visualize the file "example.py" within the directory "sample_codebase"
visualize_static('C:\\Users\\swapn\\Desktop\\Desktop\\WEALTH\\Code\\Job\\cloudcode\\kaizen\\kaizen\\visualizer\\sample\\examples.py')