import struct

__SYGIL_VERSION__ = 1

class Tokenizer():
    tokens = {
        "SEPARATOR": b"\x01",
        "DEFAULT": b"\x02",
        "COMMA": b"\x03",
        "VARIABLE": b"\x04",
        "FUNCTION": b"\x05",
        "LCURL": b"\x06",
        "RCURL": b"\x07",
        "LBRACK": b"\x08",
        "RBRACK": b"\x09",
        "LPIPE": b"\x0a",
        "RPIPE": b"\x0b",
        "LANGLE": b"\x0c",
        "RANGLE": b"\x0d",
        "LQUOTE": b"\x0e",
        "RQUOTE": b"\x0f",
        "DECL_VAR": b"\x10",
        "USE_VAR": b"\x11",
        "DECL_CLASS": b"\x15",
        "USE_CLASS": b"\x16",
        "USE_SUBCLASS": b"\x17",
        "DECL_FUNC": b"\x1a",
        "CALL": b"\x1b",
        "INT": b"\x30",
        "FLOAT": b"\x31",
        "LONG": b"\x32",
        "LIST": b"\x33",
        "DICT": b"\x34",
        "TRUE": b"\x35",
        "FALSE": b"\x36",
        "STR": b"\x37",
        "SUB": b"\x40",
        "ADD": b"\x41",
        "DIV": b"\x42",
        "MULT": b"\x43",
        "POW": b"\x44",
        "EQU": b"\x50",
        "NEQ": b"\x51"
    }

    symbols = {
        ":": "DECL_VAR",
        "::": "DECL_FUNC",
        ":@":"DECL_CLASS",
        "@": "USE_CLASS",
        "$@": "USE_SUBCLASS",
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
        "|": "LPIPE",
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

    def __init__(self, inputPath):
        with open(inputPath, "r") as f:
            self.source = f.read()
        self.pos = 0
        self.in_pipe = False
        self.in_quote = False

    def tokenize(self, outputPath):
        with open(outputPath, "wb") as out:
            out.write(b"sygil"+int(__SYGIL_VERSION__).to_bytes(2))
            while self.pos < len(self.source):
                char = self.source[self.pos]

                # Skip whitespace (except newlines which are tokens)
                if char in " \t\r":
                    self.pos += 1
                    continue

                # Handle Multi-char symbols (:: and ?0/?1)
                if char == ":" and self.peek() == ":":
                    out.write(self.tokens["DECL_FUNC"])
                    self.pos += 2
                    self.handle_identifier(out)
                    continue
                
                if char == "?" and self.peek() in "01":
                    t_key = "TRUE" if self.peek() == "1" else "FALSE"
                    out.write(self.tokens[t_key])
                    self.pos += 2
                    continue

                if char == ":" and self.peek() == "@":
                    out.write(self.tokens["DECL_CLASS"])
                    self.pos += 2
                    self.handle_identifier(out)
                    continue

                if char == "$" and self.peek() == "@":
                    out.write(self.tokens["USE_SUBCLASS"])
                    self.pos += 2
                    self.handle_identifier(out)
                    continue

                # Handle Strings
                if char == '"':
                    token_type = "RQUOTE" if self.in_quote else "LQUOTE"
                    out.write(self.tokens[token_type])
                    self.in_quote = not self.in_quote
                    self.pos += 1
                    if self.in_quote:
                        self.handle_string_content(out)
                    continue

                # Handle Single-char symbols
                if char in self.symbols:
                    s_key = self.symbols[char]
                    
                    # Special case for Pipe toggling
                    if char == "|":
                        s_key = "RPIPE" if self.in_pipe else "LPIPE"
                        self.in_pipe = not self.in_pipe
                    
                    out.write(self.tokens[s_key])
                    self.pos += 1
                    
                    # If it's a declaration or call, the next string is an identifier
                    if s_key in ["DECL_VAR", "CALL", "USE_VAR", "USE_CLASS"]:
                        self.handle_identifier(out)
                    continue

                # Handle raw numbers (if not preceded by symbols)
                elif char.isdigit():
                    self.handle_number(out)
                    continue

                self.pos += 1

    def peek(self):
        return self.source[self.pos + 1] if self.pos + 1 < len(self.source) else ""

    def handle_identifier(self, out_file):
        name = ""
        # Identifiers stop at any symbol or whitespace
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == "_"):
            name += self.source[self.pos]
            self.pos += 1
        
        if name:
            name_bytes = name.encode('utf-8')
            # [Length byte] [Name bytes]
            out_file.write(len(name_bytes).to_bytes(1))
            out_file.write(name_bytes)

    def handle_string_content(self, out_file):
        content = ""
        while self.pos < len(self.source) and self.source[self.pos] != '"':
            content += self.source[self.pos]
            self.pos += 1
        
        if content:
            content_bytes = content.encode('utf-8')
            out_file.write(content_bytes)

    def handle_number(self, out_file):
        num = ""
        while self.pos < len(self.source) and (self.source[self.pos].isdigit() or self.source[self.pos] == "."):
            num += self.source[self.pos]
            self.pos += 1
        
        if num:
            is_float = "." in num
            is_long = int(num) > 2147483647
            if(is_float):
                out_file.write(self.tokens["FLOAT"])
                val_bytes = struct.pack(">f", float(num))
            elif(is_long):
                out_file.write(self.tokens["LONG"])
                val_bytes = int(num).to_bytes(6, 'big', signed=True)
            else:
                out_file.write(self.tokens["INT"])
                val_bytes = int(num).to_bytes(4, 'big', signed=True)
            out_file.write(val_bytes)