import os
import argparse
import networkx as nx
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, text
from kaizen.helpers import output
from kaizen.llms.provider import LLMProvider
from tqdm import tqdm
from kaizen.retriever.code_chunker import chunk_code

"""
To use this in your Python package, you would typically import and use the CodeVisualizer class in your main package code. For example:

from kaizen.code_visualizer import CodeVisualizer

def visualize_repo(repo_id):
    visualizer = CodeVisualizer()
    visualizer.visualize_repository(repo_id)

def visualize_file(file_path):
    visualizer = CodeVisualizer()
    visualizer.visualize_single_file(file_path)

"""
class CodeVisualizer:
    def __init__(self):
        self.engine = create_engine(
            f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}:{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DB']}",
            pool_size=10,
            max_overflow=20,
        )
        self.graph = nx.DiGraph()
        self.graphs_folder = ".kaizen/graphs"
        self.images_folder = os.path.join(self.graphs_folder, "images")
        self.uml_folder = os.path.join(self.graphs_folder, "uml")
        self.llm_provider = LLMProvider()

    def build_graph(self, repo_id):
        print("\nBuilding graph from repository data...")
        with self.engine.connect() as connection:
            functions = self._fetch_functions(connection, repo_id)
            edges = self._fetch_edges(connection, repo_id)

        for function in tqdm(functions, desc="Adding nodes", unit="function"):
            self.graph.add_node(function.function_id, name=function.function_name, file=function.file_path)

        for edge in tqdm(edges, desc="Adding edges", unit="edge"):
            self.graph.add_edge(edge.parent_node_id, edge.child_node_id)

        print("Graph building completed.")

    def _fetch_functions(self, connection, repo_id):
        function_query = text("""
            SELECT fa.function_id, fa.function_name, f.file_path
            FROM function_abstractions fa
            JOIN files f ON fa.file_id = f.file_id
            WHERE f.repo_id = :repo_id
        """)
        return connection.execute(function_query, {"repo_id": repo_id}).fetchall()

    def _fetch_edges(self, connection, repo_id):
        edge_query = text("""
            SELECT parent_node_id, child_node_id
            FROM node_relationships
            WHERE relationship_type = 'calls'
            AND parent_node_id IN (SELECT function_id FROM function_abstractions WHERE file_id IN (SELECT file_id FROM files WHERE repo_id = :repo_id))
            AND child_node_id IN (SELECT function_id FROM function_abstractions WHERE file_id IN (SELECT file_id FROM files WHERE repo_id = :repo_id))
        """)
        return connection.execute(edge_query, {"repo_id": repo_id}).fetchall()

    def generate_graph_image(self, output_name="code_graph"):
        print("\nGenerating graph image...")
        plt.figure(figsize=(20, 20))
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=False, node_size=3000, node_color="skyblue", font_size=8,  arrows=True)

        labels = {}
        for node, data in self.graph.nodes(data=True):
            if 'type' in data:
                labels[node] = f"{data.get('name', node)}\n({data['type']})"
            else:
                labels[node] = data.get('name', node)
        nx.draw_networkx_labels(self.graph, pos, labels, font_size=6)

        plt.title("Code Structure")
        plt.axis('off')
        plt.tight_layout()

        output_file = os.path.join(self.images_folder, f"{output_name}.png")
        output.create_folder(self.images_folder)
        plt.savefig(output_file, format="png", dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Graph image saved to {output_file}")

    def generate_plantuml(self, output_name="code_structure"):
        print("\nGenerating PlantUML diagram...")
        plantuml_content = "@startuml\n"
        plantuml_content += "skinparam packageStyle rectangle\n"
        plantuml_content += "skinparam defaultTextAlignment center\n\n"

        files = {}
        for node, data in self.graph.nodes(data=True):
            if 'file' in data:  # Repository visualization
                file = data['file']
                if file not in files:
                    files[file] = []
                files[file].append((node, data['name']))
            else:  # Single file visualization
                plantuml_content += f"[{data.get('name', node)}] as {node.replace(' ', '_')} <<{data.get    ('type', 'component')}>>\n"

        if files:  # Repository visualization
            for file, functions in files.items():
                plantuml_content += f"package \"{os.path.basename(file)}\" {{\n"
                for node, name in functions:
                    plantuml_content += f"    [{name}] as {node}\n"
                plantuml_content += "}\n\n"

        for edge in self.graph.edges():
            source = self.graph.nodes[edge[0]].get('name', edge[0])
            target = self.graph.nodes[edge[1]].get('name', edge[1])
            plantuml_content += f"[{source}] --> [{target}]\n"

        plantuml_content += "@enduml\n"

        output_file = os.path.join(self.uml_folder, f"{output_name}.puml")
        output.create_folder(self.uml_folder)
        with open(output_file, 'w') as f:
            f.write(plantuml_content)
        print(f"PlantUML diagram saved to {output_file}")

    def visualize_repository(self, repo_id):
        print(f"Starting visualization for repository ID: {repo_id}")
        self.build_graph(repo_id)
        self.generate_graph_image()
        self.generate_plantuml()
        print("\nVisualization complete. Check the following files:")
        print(f"- Graph image: {os.path.join(self.images_folder, 'code_graph.png')}")
        print(f"- PlantUML diagram: {os.path.join(self.uml_folder, 'code_structure.puml')}")

    def visualize_single_file(self, file_path):
        print(f"Starting visualization for file: {file_path}")
        
        # Read file content
        with open(file_path, 'r') as file:
            content = file.read()
    
        # Determine the language based on file extension
        language = self._get_language_from_extension(file_path)
    
        # Use code_chunker to parse the code
        parsed_code = chunk_code(content, language)
    
        # Create graph from parsed code
        self._create_graph_from_parsed_code(parsed_code)
    
        # Generate visualizations
        self.generate_graph_image(output_name=f"single_file_{os.path.basename(file_path)}")
        self.generate_plantuml(output_name=f"single_file_{os.path.basename(file_path)}")
    
        print("\nVisualization complete. Check the following files:")
        print(f"- Graph image: {os.path.join(self.images_folder, f'single_file_{os.path.basename(file_path)}.png')}")
        print(f"- PlantUML diagram: {os.path.join(self.uml_folder, f'single_file_{os.path.basename(file_path)}.puml')}")
    
    def _get_language_from_extension(self, file_path):
        extension = os.path.splitext(file_path)[1].lower()
        extension_to_language = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.rs': 'rust',
            # Add more mappings as needed
        }
        return extension_to_language.get(extension, 'python')  # Default to Python if unknown
    
    def _create_graph_from_parsed_code(self, parsed_code):
        self.graph.clear()
        for section, items in parsed_code.items():
            if isinstance(items, dict):
                for name, code in items.items():
                    self.graph.add_node(name, type=section, code=code)
                    # You can add more sophisticated relationship detection here
                    for other_name in items.keys():
                        if other_name != name and other_name in code:
                            self.graph.add_edge(name, other_name)
    


    def _generate_file_analysis(self, content):
        prompt = f"""
        Analyze the following code/document and provide a structured summary of its components and their relationships. 
        For code files, focus on functions, classes, and their interactions. 
        For document files, focus on main sections and their hierarchical structure.
        
        File content:
        {content}

        Provide your analysis in the following JSON format:
        {{
            "components": [
                {{
                    "name": "component_name",
                    "type": "function/class/section",
                    "description": "brief description",
                    "relationships": ["name_of_related_component1", "name_of_related_component2"]
                }}
            ]
        }}
        """

        response, _ = self.llm_provider.chat_completion_with_json(prompt)
        return response

    def _create_graph_from_analysis(self, analysis):
        self.graph.clear()
        for component in analysis['components']:
            self.graph.add_node(component['name'], type=component['type'], description=component['description'])
            for related in component['relationships']:
                self.graph.add_edge(component['name'], related)

    
# if __name__ == "__main__":
#     visualizer = CodeVisualizer()
#     visualizer.visualize_repository("repo_id")
#     visualizer.visualize_single_file("path/to/your/file.py")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualize code structure")
    parser.add_argument("path", help="Path to the file or repository to visualize")
    parser.add_argument("--repo", action="store_true", help="Treat the path as a repository ID")
    args = parser.parse_args()

    visualizer = CodeVisualizer()
    if args.repo:
        visualizer.visualize_repository(args.path)
    else:
        visualizer.visualize_single_file(args.path)