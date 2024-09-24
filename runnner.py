import os
import google.generativeai as genai
from kaizen.retriever.code_chunker import chunk_code

# Configure the Google Generative AI library with your API key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])  # Ensure your API key is set in the environment

# Function to call the Google Gemini API and get PlantUML code
def get_plantuml_code(parsed_output):
    # Prepare the prompt for Gemini
    prompt = f"Based on the following parsed code structure, generate PlantUML code:\n\n{parsed_output}\n\nPlantUML Code:"
    
    # Instantiate the model
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # Generate content using the model
    response = model.generate_content(prompt)
    
    if response:
        return response.text.strip()
    else:
        print("Failed to generate PlantUML code.")
        return None

# Function to save PlantUML code and generate an image
def save_plantuml_image(plantuml_code, output_path):
    with open('temp.puml', 'w') as f:
        f.write(plantuml_code)
    os.system(f'java -jar "C:\Program Files\Java\jdk-22\lib\plantuml.jar" temp.puml -o {output_path}')

# Main script execution
with open('examples.py', 'r') as file:
    code = file.read()
parsed_output = chunk_code(code, 'python')
plantuml_code = get_plantuml_code(parsed_output)

if plantuml_code:
    print("Generated PlantUML Code:")
    print(plantuml_code)
    
    output_path = 'output_images'
    save_plantuml_image(plantuml_code, output_path)
else:
    print("Failed to generate PlantUML code.")