from . import sygil
from . import tokenizer
from . import syntaxValidator
from sys import argv
import os

def compileTo__syc__(path: str):
    sv = syntaxValidator.Checker(path)
    sv.check()
    tk = tokenizer.Tokenizer(path)
    dir = os.path.dirname(path)
    file = os.path.splitext(os.path.basename(path))[0] + ".syc"
    nDir = os.path.join(dir, "__syc__")
    os.makedirs(nDir, exist_ok=True)
    out_path = os.path.join(nDir, file)
    tk.tokenize(out_path)
    return out_path

if(__name__ == "__main__"):
    if(len(argv)<2):
        print()
    elif(argv[1] == "compile"):
        sv = syntaxValidator.Checker(argv[2])
        sv.check()
        tk = tokenizer.Tokenizer(argv[2])
        tk.tokenize(argv[3])
    elif(argv[1] == "run"):
        if(argv[2].endswith(".sy")):
            path = compileTo__syc__(argv[2])
        else:
            path = argv[2]
        vm = sygil.VM(path)
        vm.run()
    elif(argv[1] == "validate"):
        sv = syntaxValidator.Checker(argv[2])
        sv.check()