from string import ascii_letters
DIGITS = list("0123456789")
LETTERS = list(ascii_letters + "_")
ALLOWED = DIGITS + LETTERS
NONE_VALUES_DICT = {
    "PLUS": "+",
    "MINUS": "-",
    "MUL": "*",
    "DIV": "/",
    "POW": "^",
    "LPAREN": "(",
    "RPAREN": ")",
    "EE": "=",
    "NE": "!",
    "GT": ">",
    "LT": "<",
    "GE": ">",
    "LE": "<",
    "COLON": ":",
    "COMMA": ","
}

class Error:
    def __init__(self, error, reason):
        self.error = error
        self.reason = reason
    
    def as_string(self):
        return f"{self.error}: {self.reason}"

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value
    
    def __repr__(self):
        return f"(TOKEN {self.type}{'' if self.value == None else f': {self.value}'})"

class Value:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value
    
    def equal(self, other):
        return None, Error("TypeError", f"Unexpected operation between '{self.type}' and '{other.type}'")
    
    def not_equal(self, other):
        return None, Error("TypeError", f"Unexpected operation between '{self.type}' and '{other.type}'")
    
    def greater_than(self, other):
        return None, Error("TypeError", f"Unexpected operation between '{self.type}' and '{other.type}'")
    
    def smaller_than(self, other):
        return None, Error("TypeError", f"Unexpected operation between '{self.type}' and '{other.type}'")
    
    def greater_or_equal(self, other):
        return None, Error("TypeError", f"Unexpected operation between '{self.type}' and '{other.type}'")
    
    def smaller_or_equal(self, other):
        return None, Error("TypeError", f"Unexpected operation between '{self.type}' and '{other.type}'")
    
    def add(self, other):
        return None, Error("TypeError", f"Unexpected operation between '{self.type}' and '{other.type}'")
    
    def subtract(self, other):
        return None, Error("TypeError", f"Unexpected operation between '{self.type}' and '{other.type}'")
    
    def multiply(self, other):
        return None, Error("TypeError", f"Unexpected operation between '{self.type}' and '{other.type}'")
    
    def divide(self, other):
        return None, Error("TypeError", f"Unexpected operation between '{self.type}' and '{other.type}'")
    
    def power(self, other):
        return None, Error("TypeError", f"Unexpected operation between '{self.type}' and '{other.type}'")

class Number(Value):
    def __init__(self, value):
        super().__init__("number", value)
    
    def add(self, other):
        if other.type != "number":
            return None, Error(f"Unexpected operation between 'number' and '{other.type}'")
        
        return Number(self.type + other.type), None
    
    def subtract(self, other):
        if other.type != "number":
            return None, Error(f"Unexpected operation between 'number' and '{other.type}'")
        
        return Number(self.type - other.type), None
    
    def multiply(self, other):
        if other.type != "number":
            return None, Error(f"Unexpected operation between 'number' and '{other.type}'")
        
        return Number(self.type * other.type), None
    
    def divide(self, other):
        if other.type != "number":
            return None, Error(f"Unexpected operation between 'number' and '{other.type}'")
        
        if other.value == 0:
            return None, Error("MathError", f"Cannot divide {self.value} by 0")

        return Number(self.type / other.type), None

    def power(self, other):
        if other.type != "number":
            return None, Error(f"Unexpected operation between 'number' and '{other.type}'")
        
        return Number(self.type ** other.type), None
    
    def __repr__(self):
        return str(self.value)

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = -1
        self.current_char = None
        self.advance()
    
    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if 0 <= self.pos < len(self.text) else None
    
    def move_back(self):
        self.pos -= 1
        self.current_char = self.text[self.pos] if 0 <= self.pos < len(self.text) else None
    
    def make_tokens(self):
        tokens = []
        while self.current_char != None:
            match self.current_char:
                case "+":
                    element = get_last(tokens)
                    if element:
                        if element.type in ["PLUS", "MINUS"]:
                            self.advance()
                            continue

                    tokens += [Token("PLUS")]
                case "-":
                    element = get_last(tokens)
                    if element:
                        if element.type in ["PLUS", "MINUS"]:
                            tokens[-1] = Token("PLUS") if element.type == "PLUS" else Token("MINUS")
                            
                            self.advance()
                            continue

                    tokens += [Token("MINUS")]
                case "*":
                    tokens += [Token("MUL")]
                case "/":
                    tokens += [Token("DIV")]
                case "^":
                    tokens += [Token("POW")]
                case "(":
                    tokens += [Token("LPAREN")]
                case ")":
                    tokens += [Token("RPAREN")]
                case _:
                    if self.current_char in " \t\n":
                        self.advance()
                        continue

                    if self.current_char in DIGITS:
                        res, error = self.make_number()
                        if error:
                            return None, error

                        tokens += [res]
                    else:
                        return None, Error("SyntaxError", f"Unexpected character '{self.current_char}'")
            
            self.advance()
        
        return tokens, None
        
    def make_number(self):
        number = ""
        dot_count = 0
        while self.current_char in DIGITS + ["."]:
            number += self.current_char
            dot_count += self.current_char == "."
            self.advance()
        
        self.move_back()
        match dot_count:
            case 0:
                return Token("NUMBER", int(number)), None
            case 1:
                return Token("NUMBER", float(number)), None
            case _:
                return None, Error("SyntaxError", f"A number can't have more than 1 '.', got {dot_count}/1")

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = -1
        self.current_tok = None
        self.advance()
    
    def advance(self):
        self.pos += 1
        self.current_tok = self.tokens[self.pos] if 0 <= self.pos < len(self.tokens) else None
    
    def move_back(self):
        self.pos -= 1
        self.current_tok = self.tokens[self.pos] if 0 <= self.pos < len(self.tokens) else None
    
    def generate_syntax_branch(self):
        res, error = self.postfix()
        if error:
            return "postfix", None, error
        
        return "postfix", res, None
    
    def postfix(self):
        postfix = []
        op_stack = []
        precedence = {
            "(": 0,
            "OR": 1,
            "AND": 2,
            "NOT": 3,
            "EE": 4,
            "NE": 4,
            "GT": 4,
            "GE": 4,
            "SE": 4,
            "ST": 4,
            "PLUS": 5,
            "MINUS": 5,
            "MUL": 6,
            "DIV": 6,
            "POW": 7,
            "II": 8
        }
        while self.current_tok != None:
            if self.current_tok.type == "NUMBER":
                postfix += [Number(self.current_tok.value)]
                self.advance()
                continue

            match self.current_tok.type:
                case "LPAREN":
                    op_stack += ["("]
                case "RPAREN":
                    if "(" not in op_stack:
                        return None, Error("SyntaxError", f"Unexpected ')'")

                    while op_stack[-1] != "(":
                        postfix += [op_stack.pop()]
                    
                    op_stack.pop()
                case _:
                    if not op_stack:
                        op_stack += [self.current_tok.type]
                        self.advance()
                        continue

                    if self.current_tok.type not in precedence:
                        return None, Error("SyntaxError", f"Unexpected character: '{NONE_VALUES_DICT.get(self.current_tok.type, self.current_tok.value)}'")
                    
                    if precedence[self.current_tok.type] <= precedence[op_stack[-1]] and precedence[self.current_tok.type] != precedence["POW"] and precedence[op_stack[-1]] != precedence["POW"]:
                        postfix += [Token(op_stack.pop())]
                        
                    op_stack += [self.current_tok.type]
            
            self.advance()
        
        if "(" in op_stack:
            return None, Error("SyntaxError", "Unclosed '('")
        
        return postfix + op_stack[::-1], None

def get_last(array):
    if not array:
        return None
    
    return array[-1]

def run(text):
    global line
    lexer = Lexer(text)
    tokens, error = lexer.make_tokens()
    print("Tokens:", tokens)
    if error:
        print(f"Line {line+1}: {error.as_string()}")
        return
    
    parser = Parser(tokens)
    type_, branch, error = parser.generate_syntax_branch()
    if error:
        print(f"Line {line+1}: {error.as_string()}")
        return
    
    print("Type, branch:", type_, branch)

file = input("Which file do you want to run (don't include '.ez')? ")
with open(f"{file}.ez") as file:
    text = file.read()

def actual_run(text):
    global line
    lines = text.split("\n")
    line = 0
    while line < len(lines):
        if lines[line].strip():
            run(lines[line])
        
        line += 1

actual_run(text)