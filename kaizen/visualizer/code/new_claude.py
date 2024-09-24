import argparse
import os
import networkx as nx
import matplotlib.pyplot as plt
from kaizen.retriever.code_chunker import chunk_code
from kaizen.retriever.tree_sitter_utils import ParserFactory
from typing import Dict, Any, Union, List
def build_code_graph(parsed_body: Dict[str, Any]) -> nx.Graph:
    G = nx.Graph()
    
    for element_type, elements in parsed_body.items():
        if isinstance(elements, dict):
            for name, details in elements.items():
                G.add_node(name, type=element_type, details=details)
        elif isinstance(elements, list):
            for i, element in enumerate(elements):
                name = f"{element_type}_{i}"
                G.add_node(name, type=element_type, details=element)

    # Add edges (simplified for demonstration)
    for node in G.nodes():
        for other_node in G.nodes():
            if node != other_node:
                if G.nodes[node]['type'] in ['functions', 'methods'] and G.nodes[other_node]['type'] in ['classes', 'components']:
                    if node in G.nodes[other_node]['details'].get('code', ''):
                        G.add_edge(node, other_node)

    return G
def visualize_code_graph(G: nx.Graph, output_file: str = 'code_graph.png', highlighted_file: str = None):
    plt.figure(figsize=(10, 8))
    pos = nx.planar_layout(G)  # Reduced k value for closer nodes
    # k = 0.5 , iterations=50) for spring layout 
    node_colors = {
        'imports': '#AED6F1',
        'global_variables': '#A2D9CE',
        'functions': '#F9E79F',
        'async_functions': '#F5CBA7',
        'classes': '#D7BDE2',
        'components': '#F5B7B1',
        'hooks': '#FADBD8',
        'type_definitions': '#D5DBDB'
    }

    # Draw edges
    nx.draw_networkx_edges(G, pos, alpha=0.3, edge_color='gray', arrows=True, arrowsize=10)

    # Draw nodes
    for node_type, color in node_colors.items():
        node_list = [node for node, data in G.nodes(data=True) if data['type'] == node_type]
        nx.draw_networkx_nodes(G, pos, nodelist=node_list, node_color=color, node_size=2000, alpha=0.8)

    # Highlight nodes from the selected file
    if highlighted_file:
        highlighted_nodes = [node for node, data in G.nodes(data=True) 
                             if highlighted_file in data['details'].get('file', '')]
        nx.draw_networkx_nodes(G, pos, nodelist=highlighted_nodes, node_color='orange', 
                               node_size=2200, alpha=0.9, edgecolors='darkorange')

    # Draw labels below the nodes
    label_pos = {k: (v[0], v[1]-0.1) for k, v in pos.items()}  # Adjust label position
    nx.draw_networkx_labels(G, label_pos, font_size=8, font_weight='bold')

    # Add legend
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', label=node_type.replace('_', ' ').title(),
                                  markerfacecolor=color, markersize=10) 
                       for node_type, color in node_colors.items()]
    plt.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05),
               ncol=4, fontsize=8)

    # Add title in a box
    title = f"Code Structure: {os.path.abspath(highlighted_file)}" if highlighted_file else "Code Structure Visualization"
    plt.title(title, fontsize=12, fontweight='bold', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))

    # Add class-method relationships
    for node, data in G.nodes(data=True):
        if data['type'] == 'classes':
            methods = [m for m, d in G.nodes(data=True) if d['type'] in ['functions', 'methods'] and node in d['details'].get('code', '')]
            for method in methods:
                plt.annotate("", xy=pos[method], xytext=pos[node],
                             arrowprops=dict(arrowstyle="->", color="red", lw=1, alpha=0.5))

    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_file, format='png', dpi=300, bbox_inches='tight')
    plt.close()
def process_file(file_path: str, language: str) -> Dict[str, Any]:
    with open(file_path, 'r', encoding='utf-8') as file:
        code = file.read()
    parsed_body = chunk_code(code, language)
    # Add file information to each element
    for key, elements in parsed_body.items():
        if isinstance(elements, dict):
            for name, details in elements.items():
                if isinstance(details, dict):
                    details['file'] = file_path
                else:
                    elements[name] = {'code': details, 'file': file_path}
        elif isinstance(elements, list):
            for i, element in enumerate(elements):
                if isinstance(element, dict):
                    element['file'] = file_path
                else:
                    elements[i] = {'code': element, 'file': file_path}
    return parsed_body
def visualize_code(input_path: Union[str, List[str]], language: str, output_file: str = 'code_graph.png'):
    if isinstance(input_path, str):
        if os.path.isfile(input_path):
            parsed_bodies = [process_file(input_path, language)]
            highlighted_file = input_path
        elif os.path.isdir(input_path):
            parsed_bodies = []
            for root, _, files in os.walk(input_path):
                for file in files:
                    if file.endswith(f'.{language}'):
                        file_path = os.path.join(root, file)
                        parsed_bodies.append(process_file(file_path, language))
            highlighted_file = None
        else:
            raise ValueError("Input path must be a file or directory")
    elif isinstance(input_path, list):
        parsed_bodies = [process_file(file, language) for file in input_path if os.path.isfile(file)]
        highlighted_file = None
    else:
        raise ValueError("Input must be a string path or list of file paths")

    # Combine parsed bodies
    combined_parsed_body = {}
    for parsed_body in parsed_bodies:
        for key, value in parsed_body.items():
            if key not in combined_parsed_body:
                combined_parsed_body[key] = value
            elif isinstance(combined_parsed_body[key], dict) and isinstance(value, dict):
                combined_parsed_body[key].update(value)
            elif isinstance(combined_parsed_body[key], list) and isinstance(value, list):
                combined_parsed_body[key].extend(value)
            else:
                # If types don't match, convert to list and extend
                if not isinstance(combined_parsed_body[key], list):
                    combined_parsed_body[key] = [combined_parsed_body[key]]
                if not isinstance(value, list):
                    value = [value]
                combined_parsed_body[key].extend(value)

    graph = build_code_graph(combined_parsed_body)
    visualize_code_graph(graph, output_file, highlighted_file)
    print(f"Code visualization saved to {output_file}")
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Visualize code structure')
    parser.add_argument('input_path', type=str, help='Path to the code file or directory')
    parser.add_argument('language', type=str, choices=['python', 'javascript', 'typescript', 'rust'], 
                        help='Programming language of the code file(s)')
    parser.add_argument('--output', type=str, default='code_graph.png', 
                        help='Output file name (default: code_graph.png)')

    args = parser.parse_args()

    visualize_code(args.input_path, args.language, args.output)