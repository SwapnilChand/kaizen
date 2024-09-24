# After generating the lexer and parser, you can parse your example.py file using the generated classes:
import antlr4
from Python3Lexer import Python3Lexer
from Python3Parser import Python3Parser

def parse_python_code(file_path):
    input_stream = antlr4.FileStream(file_path)
    lexer = Python3Lexer(input_stream)
    token_stream = antlr4.CommonTokenStream(lexer)
    parser = Python3Parser(token_stream)
    
    # Parse starting from the 'file_input' rule (entry point)
    tree = parser.file_input()
    
    return tree

# Example usage
parse_tree = parse_python_code('/sample/examples.py')
print(parse_tree.toStringTree(recog=parser))