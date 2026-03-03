from . import symbolic
from . import tokenizer
from sys import argv

if(__name__ == "__main__"):
    if(len(argv)<2):
        print()
    elif(argv[1] == "compile"):
        tk = tokenizer.Tokenizer(argv[2])
        tk.tokenize(argv[3])
    elif(argv[1] == "run"):
        vm = symbolic.VM(argv[2])
        vm.run()