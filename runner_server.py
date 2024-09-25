import os
import google.generativeai as genai
from kaizen.retriever.code_chunker import chunk_code
from plantuml import PlantUML, PlantUMLHTTPError

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

# Function to save PlantUML code and generate an image using the public PlantUML server
def save_plantuml_image(plantuml_code, output_path):
    plantuml_server = PlantUML(url='http://www.plantuml.com/plantuml/')
    
    try:
        # Generate image from PlantUML code
        result = plantuml_server.processes(plantuml_code)
        
        # Save the image to the specified output path
        with open(os.path.join(output_path, 'diagram.png'), 'wb') as f:
            f.write(result)
    
    except PlantUMLHTTPError as e:
        # Handle specific HTTP errors from the PlantUML server
        print(f"HTTP Error: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response}")
            if hasattr(e.response, 'headers'):
                print(f"Diagram Description: {e.response.headers.get('X-PlantUML-Diagram-Description')}")
                print(f"Diagram Error: {e.response.headers.get('X-PlantUML-Diagram-Error')}")
                print(f"Error Line: {e.response.headers.get('X-PlantUML-Diagram-Error-Line')}")
    
    except Exception as e:
        # Handle other exceptions
        print(f"An error occurred: {str(e)}")

# Main script execution
with open('examples.py', 'r') as file:
    code = file.read()
parsed_output = chunk_code(code, 'python')
plantuml_code = get_plantuml_code(parsed_output)

if plantuml_code:
    print("Generated PlantUML Code:")
    print(plantuml_code)
    
    output_path = 'output_images'
    os.makedirs(output_path, exist_ok=True)  # Create output directory if it doesn't exist
    save_plantuml_image(plantuml_code, output_path)
else:
    print("Failed to generate PlantUML code.")