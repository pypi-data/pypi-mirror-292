import os

def compile():
    
    current_directory = os.getcwd()

    os.chdir(os.path.dirname(__file__))
    os.system('make clean')
    os.system('make compile')
    os.system('make tests')
    os.system(f'cd {current_directory}')

if __name__ == '__main__':
    compile()
