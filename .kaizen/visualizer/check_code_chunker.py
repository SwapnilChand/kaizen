# run_chunker.py
from kaizen.retriever.code_chunker import chunk_code
with open('C:\\Users\\swapn\\Desktop\\Desktop\\WEALTH\\Code\\Job\\cloudcode\\kaizen\\kaizen\\visualizer\\sample\\examples.py', 'r') as file:
    code = file.read()

parsed_output = chunk_code(code, 'python')
print(parsed_output)
