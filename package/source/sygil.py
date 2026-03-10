import struct

__SYGIL_VERSION__ = 2

class UnknownVariable():
    def __init__(self):
        pass

class FormatError(Exception): pass

class VersionError(Exception): pass

class readableByteBuffer():
    def __init__(self, value):
        self.bytes = value
    
    def read(self, amount):
        data = self.bytes[0:amount]
        self.bytes = self.bytes[amount:]
        return data
    
    def peek(self, ahead):
        return self.bytes[ahead-1] if not self.eof() else False

    def eof(self):
        try: self.bytes[0]
        except: return True
        else: return False

class context():
    def __init__(self, vars={}, funcs={}):
        self.variables = {}
        self.functions = {}
    def __repr__(self):
        return f"context(variables={self.variables}, functions={self.functions})"

class VM():
    def __init__(self, filePath):
        self.tokens = open(filePath, "rb")
        check = self.tokens.read(7)
        if(check[:5] != b"sygil"):
            raise FormatError(f"The provided file ({filePath}) is not a valid compiled Sygil file.")
        elif(check[5:] != __SYGIL_VERSION__.to_bytes(2)):
            raise VersionError(f"The provided file ({filePath}) is the wrong version ({int.from_bytes(check[5:])}, correct version is {__SYGIL_VERSION__})")
        self.contexts = {
            "__global__":context()
        }
        self.activeContext="__global__"
        self.return_val = None
        self.old_tokens = []

    def read_int(self, intBytes):
        return int.from_bytes(intBytes, "big", signed=True)
    
    def read_float(self, floatBytes):
        return float(struct.unpack(">f", floatBytes)[0])

    def read_exp(self):
        data = b""
        nByte = b""
        while nByte != b"\x09":
            data+=nByte
            nByte = self.read(1)
        return self.eval_exp(data)
    
    def read_str(self):
        data = b""
        nByte = b""
        while nByte != b"\x0f":
            data+=nByte
            nByte = self.read(1)
        return data.decode("utf-8")
    
    def read_list(self):
        data = b""
        nByte = b""
        depth = 0
        while depth > -1:
            data+=nByte
            nByte = self.read(1)
            if(nByte == b"\x06"):
                depth += 1
            elif(nByte == b"\x07"):
                depth -= 1
        return data
    
    def get_new_func_params(self):
        data = b""
        nByte = b""
        while nByte != b"\x0d":
            data+=nByte
            nByte = self.read(1)
        return data

    def read_func_params(self):
        data = b""
        nByte = b""
        depth = 0
        while depth > -1:
            data+=nByte
            nByte = self.read(1)
            if(nByte == b"\x0c"):
                depth += 1
            elif(nByte == b"\x0d"):
                depth -= 1
        return data
    
    def split_func_params(self, params):
        split = []
        curParam = b""
        fDepth = 0
        lSkip = 0
        for p in params:
            p = bytes([p])
            if(lSkip): 
                lSkip -= 1
                curParam += p
                continue
            if(p == b"\x03" and fDepth < 1):
                split.append(curParam)
                curParam = b""
            else:
                if(p == b"\x0c" and not lSkip):
                    fDepth += 1
                elif(p == b"\x0d" and not lSkip):
                    fDepth -= 1
                elif((p == b"\x11" or p == b"\x10" or p == b"\x1b" or p == b"\x16") and not lSkip):
                    lSkip = 1
                elif((p == b"\x30" or p == b"\x31") and not lSkip):
                    lSkip = 4
                elif((p == b"\x38") and not lSkip):
                    lSkip = 2
                elif((p == b"\x32") and not lSkip):
                    lSkip = 6
                curParam += p
        split.append(curParam)
        curParam = b""
        if(split[-1] == b""):
            split=split[:-1]
        return split
    
    def read_func_code(self):
        data = b""
        nByte = b""
        depth = 0
        while nByte != b"\x0b" or depth>0:
            data+=nByte
            nByte = self.read(1)
            if(nByte == b"\x0a"):
                depth+=1
            elif(nByte == b"\x0b"):
                depth-=1
        return data
    
    def eval_exp(self, exp):
        output = None
        mode = "set"
        exp = readableByteBuffer(exp)
        startingContext = self.activeContext
        while not exp.eof():
            b = exp.read(1)
            if(b==b"\x11"):
                nameLen = int.from_bytes(exp.read(1))
                varName = exp.read(nameLen).decode("utf-8")
                varData = self.get_var(varName)
                if(mode == "set"):
                    output = varData
                elif(mode == "add"):
                    output += varData
                elif(mode == "sub"):
                    output -= varData
                elif(mode == "div"):
                    output /= varData
                elif(mode == "mult"):
                    output += varData
                elif(mode == "pow"):
                    output **= varData
                self.activeContext = startingContext
                #print(varName, varData)
            elif(b==b"\x30"):
                data=self.read_int(exp.read(4))
                if(mode == "set"):
                    output = data
                elif(mode == "add"):
                    output += data
                elif(mode == "sub"):
                    output -= data
                elif(mode == "div"):
                    output /= data
                elif(mode == "mult"):
                    output += data
                elif(mode == "pow"):
                    output **= data
            elif(b==b"\x31"):
                data=self.read_float(exp.read(4))
                if(mode == "set"):
                    output = data
                elif(mode == "add"):
                    output += data
                elif(mode == "sub"):
                    output -= data
                elif(mode == "div"):
                    output /= data
                elif(mode == "mult"):
                    output += data
                elif(mode == "pow"):
                    output **= data
            elif(b==b"\x32"):
                data=self.read_int(exp.read(6))
                if(mode == "set"):
                    output = data
                elif(mode == "add"):
                    output += data
                elif(mode == "sub"):
                    output -= data
                elif(mode == "div"):
                    output /= data
                elif(mode == "mult"):
                    output += data
                elif(mode == "pow"):
                    output **= data
            elif(b==b"\x38"):
                data=self.read_int(exp.read(2))
                if(mode == "set"):
                    output = data
                elif(mode == "add"):
                    output += data
                elif(mode == "sub"):
                    output -= data
                elif(mode == "div"):
                    output /= data
                elif(mode == "mult"):
                    output += data
                elif(mode == "pow"):
                    output **= data
            elif(b==b"\x0e"):
                data = self.read_str()
                if(mode == "set"):
                    output = data
                elif(mode == "add"):
                    output += data
            elif(b==b"\x1b"):
                self.old_tokens.append(self.tokens)
                self.tokens = exp
                self.OP_call()
                self.tokens = self.old_tokens.pop()
                data = self.return_val
                if(mode == "set"):
                    output = data
                elif(mode == "add"):
                    output += data
                elif(mode == "sub"):
                    output -= data
                elif(mode == "div"):
                    output /= data
                elif(mode == "mult"):
                    output += data
                elif(mode == "pow"):
                    output **= data
            elif(b==b"\x16"):
                nameLen = int.from_bytes(exp.read(1))
                className = exp.read(nameLen).decode("utf-8")
                if(className == "__global__"):
                    self.activeContext = "__global__"
                elif(className == "__parent__" and self.activeContext not in ["__global__","__function__"]):
                    self.activeContext = ".".join(self.activeContext.split(".")[:-1])
                else:
                    self.activeContext = self.activeContext+"."+className
            elif(b==b"\x40"):
                mode = "sub"
            elif(b==b"\x41"):
                mode = "add"
            elif(b==b"\x42"):
                mode = "div"
            elif(b==b"\x43"):
                mode = "mult"
            elif(b==b"\x44"):
                mode == "pow"
            elif(b in b"\x0c\x0d\x50\x51\x35\x36"):
                return b
            #print(output)
        return output
    
    def eval_func_params(self, params:bytes):
        params = self.split_func_params(params)
        result = []
        for par in params:
            result.append(self.eval_exp(par))
        return result
    
    def read(self, amnt):
        return self.tokens.read(amnt)
    
    def set_func(self, funcName, params, code, defaults):
        if(self.contexts[self.activeContext].functions.get(funcName, UnknownVariable()) != UnknownVariable()):
            self.contexts[self.activeContext].functions.update({funcName:[params, code,defaults]})
        else:
            self.contexts[self.activeContext].functions.__setitem__(funcName, [params, code, defaults])
    
    def get_func(self, funcName):
        return self.contexts[self.activeContext].functions.get(funcName)
    
    def set_var(self, varName, value):
        if(self.contexts[self.activeContext].variables.get(varName, UnknownVariable()) != UnknownVariable()):
            self.contexts[self.activeContext].variables.update({varName:value})
        else:
            self.contexts[self.activeContext].variables.__setitem__(varName, value)

    def get_var(self, varName):
        return self.contexts[self.activeContext].variables.get(varName)

    def OP_set_variable(self):
        nameLen = int.from_bytes(self.tokens.read(1))
        varName = self.tokens.read(nameLen).decode("utf-8")
        sep = self.read(1)
        nByte = self.read(1)
        if(nByte == b"\x30"):
            data = self.read_int(self.read(4))
        elif(nByte == b"\x31"):
            data = self.read_float(self.read(4))
        elif(nByte == b"\x32"):
            data = self.read_int(self.read(6))
        elif(nByte == b"\x38"):
            data = self.read_int(self.read(2))
        elif(nByte == b"\x06"):
            data = [self.eval_exp(e) for e in self.split_func_params(self.read_list())]
        elif(nByte == b"\x08"):
            data = self.read_exp()
        elif(nByte == b"\x0e"):
            data = self.read_str()
        elif(nByte == b"\x35"):
            data = True
        elif(nByte == b"\x36"):
            data = False
        self.set_var(varName, data)
        
    def OP_set_function(self):
        nameLen = int.from_bytes(self.tokens.read(1))
        funcName = self.tokens.read(nameLen).decode("utf-8")
        self.read(1) # get the mandatory "<" token out of the stream
        params: list[bytes] = self.split_func_params(self.get_new_func_params())
        defaults = []
        for n, par in enumerate(params):
            if(b"\x02" in par):
                defaults.append(self.eval_exp(par[par.index(b"\x02"):]))
                params[n] = params[n][:par.index(b"\x02")]
            else:
                defaults.append(None)
        self.read(1) #remove the mandatory "|" token from the stream
        code = self.read_func_code()
        self.set_func(funcName, [p[2:] for p in params], code, defaults)

    def OP_call(self):
        nameLen = int.from_bytes(self.tokens.read(1))
        funcName = self.tokens.read(nameLen).decode("utf-8")
        self.read(1) # get the mandatory "<" token out of the stream
        params = self.eval_func_params(self.read_func_params())
        self.return_val = None
        if(funcName in list(self.contexts[self.activeContext].functions.keys())):
            func_data = self.contexts[self.activeContext].functions[funcName]
            param_names = func_data[0]
            func_code = func_data[1]  
            param_defaults = func_data[2]

            self.contexts.update({
                "__function__":context()
            })
        
            prevContext = self.activeContext

            self.activeContext = "__function__"

            for i, val in enumerate(params):
                p_name = param_names[i].decode('utf-8')
                if i < len(param_names):
                    self.contexts[self.activeContext].variables[p_name] = val
                else:
                    self.contexts[self.activeContext].variables[p_name] = param_defaults[i]

            self.run(readableByteBuffer(func_code))
            self.activeContext = prevContext

            self.contexts = {k: v for k, v in self.contexts.items() if not k.startswith("__function__")}
        elif(funcName == "print"):
            print(*params)
        elif(funcName == "if"):
            code = self.read_func_code()
            if(params[0] == b"\x35" and len(params)<2):
                self.run(readableByteBuffer(code))
            elif(params[1] == b"\x50"):
                if(params[0] == params[2]):
                    self.run(readableByteBuffer(code))
            elif(params[1] == b"\x51"):
                if(params[0] != params[2]):
                    self.run(readableByteBuffer(code))
        elif(funcName == "while"):
            code = self.read_func_code()
            if(params[0] == b"\x35" and len(params)<2):
                while True:
                    if self.run(readableByteBuffer(code)) == "RET": break
        elif(funcName == "return"):
            self.return_val = params[0]
            return "RET"
        
    def OP_set_class(self):
        nameLen = int.from_bytes(self.tokens.read(1))
        className = self.activeContext + "." + self.tokens.read(nameLen).decode("utf-8")
        subObjects = self.read_func_code()
        self.contexts.update({
            className:context()
        })
        prevContext = self.activeContext
        self.activeContext = className
        self.run(readableByteBuffer(subObjects))
        self.activeContext = prevContext

    def run(self, code=None):
        if(code == None):
            code = self.tokens
        else:
            self.old_tokens.append(self.tokens)
            self.tokens = code
        while code.peek(1):
            op = int.from_bytes(code.read(1))

            if(op == 0x10):
                self.OP_set_variable()
            elif(op == 0x1a):
                self.OP_set_function()
            elif(op == 0x1b):
                if self.OP_call() == "RET": break
            elif(op == 0x15):
                self.OP_set_class()
        if(len(self.old_tokens)>0): self.tokens = self.old_tokens.pop()
        return "RET"