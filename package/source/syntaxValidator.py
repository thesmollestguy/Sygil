class SygilSyntaxError(Exception):
    def __init__(self, message):
        import colorama
        colorama.just_fix_windows_console()
        print(f"{colorama.Fore.LIGHTMAGENTA_EX}SygilSyntaxError{colorama.Fore.RESET}: {colorama.Fore.MAGENTA}{message}{colorama.Fore.RESET}")
        raise SystemExit()

class Checker():
    symbols = {
        ":": "DECL_VAR",
        "::": "DECL_FUNC",
        ":@":"DECL_CLASS",
        "@": "USE_CLASS",
        "_": "CALL",
        "?1": "TRUE",
        "?0": "FALSE",
        "{": "LCURL",
        "}": "RCURL",
        "[": "LBRACK",
        "]": "RBRACK",
        "<": "LANGLE",
        ">": "RANGLE",
        "~": "DEFAULT",
        "|": "PIPE",
        '"': "QUOTE",
        ";": "SEPARATOR",
        "$": "USE_VAR",
        "-": "SUB",
        "+": "ADD",
        "*": "MULT",
        "/": "DIV",
        "^": "POW",
        ",": "COMMA",
        "!": "NEQ",
        "=": "EQU"
    }

    expects = {
        "DECL_VAR":["SEPARATOR","COMMA","RANGLE"],
        "DECL_FUNC":"LANGLE",
        "USE_VAR":None,
        "CALL":"LANGLE",
        "DECL_CLASS":"SEPARATOR",
        "USE_CLASS":["USE_CLASS","USE_VAR","CALL"]
    }

    reserved = [
        "__global__",
        "__function__",
        "__parent__"
    ]

    def __init__(self, inputPath):
        with open(inputPath, "r") as f:
            self.source = f.read()
        self.pos = 0
        self.in_pipe = False
        self.in_quote = False
        self.expecting = None
        self.prevToken = None
        self.line = 1
        self.linePos = 1

    def expect(self, token):
        self.expecting = token

    def incPos(self, amount):
        self.pos+=amount
        self.linePos+=amount

    def check(self):
        COMMENT = "#"
        MULTI_COMMENT = "`"
        commenting = 0
        while self.pos < len(self.source):
                char = self.source[self.pos]
                if(char == "\n"):
                    self.line+=1
                    self.linePos = 0
                if char == COMMENT:
                    commenting = 1
                    self.incPos(1)
                    continue
                elif char == MULTI_COMMENT:
                    commenting = 0 if commenting == 2 else 2
                    self.incPos(1)
                    continue
                elif char in " \t\r\n":
                    self.incPos(1)
                    if(commenting == 1):
                        commenting = 0
                    continue

                elif(commenting>0):
                    self.incPos(1)
                    continue

                # Handle Multi-char symbols (:: and ?0/?1)
                elif char == ":" and self.peek() == ":":
                    self.incPos(2)
                    self.handle_identifier(True)
                    s_key = "DECL_FUNC"
                
                elif char == "?" and self.peek() in "01":
                    s_key = "TRUE" if self.peek() == "1" else "FALSE"
                    self.incPos(2)

                elif char == ":" and self.peek() == "@":
                    self.incPos(2)
                    self.handle_identifier(True)
                    s_key = "DECL_CLASS"

                # Handle Strings
                elif char == '"':
                    s_key = "RQUOTE" if self.in_quote else "LQUOTE"
                    self.in_quote = not self.in_quote
                    self.incPos(1)
                    if self.in_quote:
                        self.handle_string_content()

                # Handle Single-char symbols
                elif char in self.symbols:
                    s_key = self.symbols[char]
                    self.incPos(1)
                    
                    # If it's a declaration or call, the next string is an identifier
                    if s_key in ["CALL", "USE_VAR", "USE_CLASS"]:
                        self.handle_identifier()
                    elif s_key == "DECL_VAR":
                        self.handle_identifier(True)

                # Handle raw numbers (if not preceded by symbols)
                elif char.isdigit():
                    self.handle_number()
                    
                if(self.expecting != None):
                    if(isinstance(self.expecting, list)):
                        if(s_key not in self.expecting):
                            raise SygilSyntaxError(f"Token after {self.prevToken} was not in {self.expecting} ({self.line}, {self.linePos})")
                    else:
                        if(s_key != self.expecting):
                            raise SygilSyntaxError(f"Token after {self.prevToken} was not {self.expecting} ({self.line}, {self.linePos})")
                self.prevToken = s_key
                self.expect(self.expects.get(s_key, None))

    def peek(self):
        return self.source[self.pos + 1] if self.pos + 1 < len(self.source) else ""

    def handle_identifier(self, new=False):
        name = ""
        # Identifiers stop at any symbol or whitespace
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == "_"):
            name += self.source[self.pos]
            self.incPos(1)
        
        if name:
            if(name in self.reserved and new):
                raise SygilSyntaxError(f"\"{name}\" is a reserved keyword")

    def handle_string_content(self):
        content = ""
        while self.pos < len(self.source) and self.source[self.pos] != '"':
            content += self.source[self.pos]
            self.incPos(1)
        
        if content: pass

    def handle_number(self):
        num = ""
        while self.pos < len(self.source) and (self.source[self.pos].isdigit() or self.source[self.pos] == "."):
            num += self.source[self.pos]
            self.incPos(1)
        
        if num:
            is_float = "." in num
            is_long = abs(int(num)) > 2147483647
            is_short = abs(int(num)) < 32768
            if(is_float): pass
            elif(is_long): pass
            elif(is_short): pass
            else: pass