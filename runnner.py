import os
import requests
from kaizen.retriever.code_chunker import chunk_code

# Function to call the OpenAI API and get PlantUML code
def get_plantuml_code(parsed_output):
    api_key = 'YOUR_OPENAI_API_KEY'  # Replace with your actual OpenAI API key
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    
    # Prepare the prompt for LLM
    prompt = f"Based on the following parsed Python code structure, generate PlantUML code:\n\n{parsed_output}\n\nPlantUML Code:"
    
    data = {
        'model': 'gpt-3.5-turbo',  # You can change this based on your model preference
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': 300,
    }

    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
    
    if response.status_code == 200:
        plantuml_code = response.json()['choices'][0]['message']['content']
        return plantuml_code.strip()
    else:
        print("Error:", response.status_code, response.text)
        return None

# Function to save PlantUML code and generate an image
def save_plantuml_image(plantuml_code, output_path):
    with open('temp.puml', 'w') as f:
        f.write(plantuml_code)

    # Command to generate image using PlantUML (ensure PlantUML is installed and in PATH)
    os.system(f'java -jar plantuml.jar temp.puml -o {output_path}')

# Main script execution
with open('C:\\Users\\swapn\\Desktop\\Desktop\\WEALTH\\Code\\Job\\cloudcode\\kaizen\\kaizen\\visualizer\\sample\\examples.py', 'r') as file:
    code = file.read()

parsed_output = chunk_code(code, 'python')
print("OK")
print(parsed_output)

# Get PlantUML code from LLM
plantuml_code = get_plantuml_code(parsed_output)

if plantuml_code:
    print("Generated PlantUML Code:")
    print(plantuml_code)
    
    # Specify output path for the generated image
    output_path = 'C:\\Users\\swapn\\Desktop\\Desktop\\WEALTH\\Code\\Job\\cloudcode\\kaizen\\kaizen\\visualizer\\output_images'
    
    # Generate and save the image
    save_plantuml_image(plantuml_code, output_path)
else:
    print("Failed to generate PlantUML code.")