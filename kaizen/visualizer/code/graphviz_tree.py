import os
from tree_sitter import Language, Parser

# Load the Python language
# Language.build_library(
#     'build/my-languages.so',
#     [
#         'tree-sitter-python',
#     ]
# )

# Create a parser for Python
python_language = Language('build/my-languages.so', 'python')
parser = Parser()
parser.set_language(python_language)

def generate_graph(code_path, output_path):
    # Read the code from the file
    with open(code_path, 'r') as file:
        code = file.read()

    # Parse the code
    tree = parser.parse(bytes(code, 'utf8'))

    # Generate Graphviz DOT representation
    dot_graph = generate_dot_graph(tree.root_node)

    # Save DOT representation to a temporary file
    with open('temp.dot', 'w') as f:
        f.write(dot_graph)

    # Render the DOT graph using Graphviz
    os.system(f'dot -Tpng temp.dot -o {output_path}')

def generate_dot_graph(node):
    dot_graph = 'digraph G {\n'
    
    def traverse(node):
        if node.is_named:
            node_id = f'{node.id} [label="{node.type}"];\n'
            dot_graph += node_id
            
            for child in node.children:
                dot_graph += f'{node.id} -> {child.id};\n'
                traverse(child)

    traverse(node)
    dot_graph += '}'
    
    return dot_graph

# Example usage
if __name__ == "__main__":
    generate_graph('C:\\Users\\swapn\\Desktop\\Desktop\\WEALTH\\Code\\Job\\cloudcode\\kaizen\\kaizen\\visualizer\\sample\\examples.py', 'output.png')