from . import sygil
from . import tokenizer
from sys import argv
import os

def compileTo__syc__(path:str):
    tk = tokenizer.Tokenizer(path)
    nPath = path[:-3]
    if("/" in path):
        sep = "/"
    else:
        sep = "\\"
    nPath = nPath.split(sep)
    file = nPath[-1]+".syc"
    nPath = sep.join(nPath[:-1])+sep
    os.makedirs(nPath+"__syc__"+sep, exist_ok=True)
    nPath = nPath+"__syc__"+sep+file
    tk.tokenize(nPath)
    return nPath

if(__name__ == "__main__"):
    if(len(argv)<2):
        print()
    elif(argv[1] == "compile"):
        tk = tokenizer.Tokenizer(argv[2])
        tk.tokenize(argv[3])
    elif(argv[1] == "run"):
        if(argv[2].endswith(".sy")):
            path = compileTo__syc__(argv[2])
        else:
            path = argv[2]
        vm = sygil.VM(path)
        vm.run()