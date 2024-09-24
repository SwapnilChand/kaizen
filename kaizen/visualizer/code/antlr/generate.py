import subprocess
import os

def generate_antlr_files(grammar_file):
    antlr_jar_path = 'path/to/antlr-4.9.3-complete.jar'  # Update this path
    command = ['java', '-jar', antlr_jar_path, grammar_file]

    try:
        subprocess.run(command, check=True)
        print(f'Successfully generated lexer and parser from {grammar_file}')
    except subprocess.CalledProcessError as e:
        print(f'Error generating files: {e}')

def main():
    # Define the grammar files for Python
    grammar_files = [
        'Python3Lexer.g4',
        'Python3Parser.g4'
    ]

    # Change directory to where your grammar files are located
    os.chdir('/Grammar')  # Update this path

    # Generate lexer and parser for each grammar file
    for grammar_file in grammar_files:
        generate_antlr_files(grammar_file)

if __name__ == '__main__':
    main()