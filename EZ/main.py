from my_type import *
from errors import *

def create_number(string):
    try:
        if float(string) % 1 == 0:
            return Number(int(float(string)))
        else:
            return Number(float(string))
    except ValueError:
         raise ConversionError(f"Cannot convert '{string}' to a number.")

def translate_boolean(string):
    match string:
        case "yes":
            return True
        case "no":
            return False
        case True:
            return "yes"
        case False:
            return "no"

def char_condition(snippet, i, char):
    if i == len(snippet):
        return False

    return snippet[i] in char

def indent_condition(lines, i, indentation):
    if i >= len(lines):
        return False
    
    if not lines[i].strip():
        return True

    return lines[i].startswith(" " * 4 * (indentation + 1))

def skip_condition(lines, i, indentation):
    if i >= len(lines):
        return False
    
    if not lines[i].strip():
        return True

    instruction = ""
    _ = 0
    if lines[i].startswith(" " * 4 * (indentation + 1)):
        return True

    while char_condition(lines[i].lower(), _, VALIDS):
        instruction += lines[i][_]
        _ += 1
    if instruction in ("if", "elif", "else"):
        return True
    
    return False

def next_condition(lines, i, indentation):
    if i >= len(lines):
        return False
    
    if not lines[i].strip():
        return True

    instruction = ""
    _ = 0
    if lines[i].startswith(" " * 4 * (indentation + 1)):
        return True

    while char_condition(lines[i].lower(), _, VALIDS):
        instruction += lines[i][_]
        _ += 1
    
    return False

def get_args(snippet, original=[]):
    global variables
    instruction = ""
    i = 0
    arg = ""
    while char_condition(snippet, i, " "):
        i += 1

    if i == len(snippet):
        return original

    while char_condition(snippet.lower(), i, "abcdefghijklmnopqrstuvwxyz0123456789_."):
        instruction += snippet[i]
        i += 1

    if i == len(snippet):
        return original

    nexter = snippet[i]
    if nexter == ":" and instruction not in ("number", "boolean", "nothing", "char", "unsemi"):
        return original + [run(instruction + ":" + snippet[i+1:], variables)]

    if nexter == ":" and instruction == "char":
        arg = snippet[i+1]
        i += 1

    found_semi = False
    i += 1

    temp = arg
    while i < len(snippet):
        if snippet[i] == ";":
            found_semi = True
            break

        if not temp:
            arg += snippet[i]

        i += 1

    if found_semi:
        return get_args(snippet[i+1:], original + [run(instruction + nexter + arg, variables)])

    return original + [run(instruction + nexter + arg, variables)]

def run(snippet, variables, original=False, indentation=0, in_if=False):
    global line, lines
    if original and snippet.startswith(" " * 4 * (indentation + 1)):
        raise SyntaxError("Unexpected indent!")

    i = 0
    while char_condition(snippet, i, " "):
        i += 1

    if original and snippet[i] == "$":
        # comment
        return Nothing()

    instruction = ""
    while char_condition(snippet.lower(), i, VALIDS):
        instruction += snippet[i]
        i += 1

    while char_condition(snippet, i, " "):
        i += 1

    if i == len(snippet):
        nexter = ""
    else:
        nexter = snippet[i]

    if nexter.lower() in VALIDS:
        nexter = " "

    match nexter:
        case " ":
            # variables and stuff (if elif else condition)
            if not original:
                raise SyntaxError("Variables definition/if elif else statements in the wrong place!")

            match instruction:
                case "if":
                    in_if = True
                    snip = snippet[i:]
                    conditions = get_args(snip)
                    if len(conditions) != 1:
                        raise ArgumentError("Can't check 0 or multiple conditions at the same time!")
                    
                    '''
                    Option 1: check for condition and perform the block
                    Option 2: store the block of conditions
                    i think i prefer option 1 because... doing option 1 seems easier and we don't have to go over again
                    but option 2 i think it's faster and can reuse in many more mechanics like functions and loops
                    '''

                    condition = conditions[0]
                    line += 1
                    if translate_boolean(condition.value):
                        # perform the block below
                        while indent_condition(lines, line, indentation):
                            if lines[line].strip():
                                run(lines[line][4 * (indentation + 1):], variables, True, indentation+1)

                            line += 1
                        
                        while skip_condition(lines, line, indentation):
                            line += 1
                    else:
                        while next_condition(lines, line, indentation):
                            if not lines[line].strip():
                                line += 1
                                continue

                            line += 1
                        
                        run(lines[line], variables, True, indentation, in_if)
                case "elif":
                    if not in_if:
                        raise SyntaxError("No parent if!")
                    
                    snip = snippet[i:]
                    conditions = get_args(snip)
                    if len(conditions) != 1:
                        raise ArgumentError("Can't check 0 or multiple conditions at the same time!")

                    condition = conditions[0]
                    line += 1
                    if translate_boolean(condition.value):
                        # perform the block below
                        while indent_condition(lines, line, indentation):
                            if lines[line].strip():
                                run(lines[line][4 * (indentation + 1):], variables, True, indentation+1)

                            line += 1
                        
                        while skip_condition(lines, line, indentation):
                            line += 1
                    else:
                        while next_condition(lines, line, indentation):
                            if not lines[line].strip():
                                line += 1
                                continue

                            line += 1
                        
                        run(lines[line], variables, True, indentation, in_if)
                case "else":
                    raise ArgumentError("Else does not have any condition!")
                case _:
                    var_name = instruction
                    keyword = ""
                    while char_condition(snippet.lower(), i, VALIDS):
                        keyword += snippet[i]
                        i += 1

                    if keyword != "is":
                        raise SyntaxError("Invalid syntax! The syntax for defining a variable is: <var_name> is (now must if your variable is defined else no) <value>")

                    while char_condition(snippet, i, " "):
                        i += 1

                    if var_name in variables:
                        # must use now
                        keyword = ""
                        while char_condition(snippet.lower(), i, VALIDS):
                            keyword += snippet[i]
                            i += 1

                        if keyword != "now":
                            raise SyntaxError(f"Invalid syntax! Your variable was defined so the syntax is: <var_name> is now <value>")

                    while char_condition(snippet, i, " "):
                        i += 1

                    # value
                    if not snippet[i:]:
                        variables.update({var_name: Nothing()})
                        return Nothing()

                    args = get_args(snippet[i:])
                    if len(args) != 1:
                        raise ArgumentError("Can't assign multiple values to a variable!")
                    
                    value = args[0]
                    variables.update({var_name: value})
        case "":
            # especially for else!
            if not in_if:
                raise SyntaxError("No parent if!")
            
            in_if = False
            snip = snippet[i:]
            if snip:
                raise ArgumentError("Else branch has no conditions!")
            
            line += 1
            while indent_condition(lines, line, indentation):
                if lines[line].strip():
                    run(lines[line][4 * (indentation + 1):], variables, True, indentation+1)
                
                line += 1
            
            while skip_condition(lines, line, indentation):
                line += 1
        case ":":
            # instructions
            match instruction:
                case "text":
                    if i == len(snippet) - 1:
                        return Text("")

                    argument = snippet[i+1:]
                    return Text(argument)
                case "char":
                    if i == len(snippet) - 1:
                        return Char(" ")

                    argument = snippet[i+1:]
                    return Char(argument)
                case "unsemi":
                    if i == len(snippet) - 1:
                        return Unsemi("")

                    argument = snippet[i+1:]
                    return Unsemi(argument)
                case "number":
                    argument = snippet[i+1:].strip()
                    if not argument:
                        return Number(0)
                    return create_number(argument)
                case "boolean":
                    argument = snippet[i+1:].strip()
                    if not argument:
                        return Boolean("no")
                    
                    if argument not in ("yes", "no"):
                        raise ConversionError(f"Cannot convert '{argument}' to a boolean.")

                    return Boolean(argument)
                case "nothing":
                    snip = snippet[i+1:].strip()
                    arguments = get_args(snip)
                    if arguments:
                        raise ArgumentError("Expect 0 arguments in nothing.")

                    return Nothing()
                case "show":
                    snip = snippet[i+1:]
                    arguments = get_args(snip)
                    for argument in arguments:
                        print(argument.value)

                    return Nothing()
                case "ask":
                    snip = snippet[i+1:]
                    arguments = get_args(snip)
                    if len(arguments) != 1:
                        raise ArgumentError("Expect 1 argument in ask.")

                    return Text(input(arguments[0].value))
                case "calculate":
                    argument = snippet[i+1:]
                    tokens = []
                    OPERATORS = "+-*/^()"
                    current = ""
                    for char in argument:
                        if char == " ":
                            continue

                        if char in OPERATORS:
                            if current:
                                tokens.append(current)

                            tokens.append(char)
                            current = ""
                        else:
                            current += char

                    if current:
                        tokens.append(current)

                    # we need to calculate based on the tokens
                    new = []
                    for token in tokens:
                        if token in OPERATORS:
                            new.append(token)
                            continue

                        new.append(run(token, variables))

                    # syntax checking + stack usage
                    prev = None
                    stack = []
                    bracket_dictionary = {}
                    for i, token in enumerate(new):
                        if token in ("*", "/", "^") and prev in ("*", "/", "^", None):
                            if prev:
                                raise SyntaxError(f"Invalid syntax! '{token}' does not stand after '{prev}'!")

                            raise SyntaxError(f"Invalid syntax! An expression does not start with '{token}'!")

                        if token in ("(", ")"):
                            if token == ")" and not stack:
                                raise SyntaxError("')' has no matching bracket")
                            elif token == "(":
                                stack.append(i)
                            else:
                                # add to the dictionary
                                start = stack.pop(-1)
                                bracket_dictionary.update({start: i, i: start})

                        if not isinstance(token, (Number, str)):
                            raise TypeError(f"Snippet\n\n{tokens[i]}\n\ndoes not return a number!")

                        prev = token
                    if stack:
                        raise SyntaxError("Unclosed '('!")

                    ev = ""
                    for token in new:
                        if isinstance(token, Number):
                            ev += str(token.value)
                        elif token == "^":
                            ev += "**"
                        else:
                            ev += token

                    return create_number(str(eval(ev)))
                case "join":
                    snip = snippet[i+1:]
                    arguments = get_args(snip)
                    string = ""
                    for argument in arguments:
                        string += str(argument.value)

                    return Text(string)
                case "type":
                    snip = snippet[i+1:]
                    arguments = get_args(snip)
                    if len(arguments) > 1:
                        raise ArgumentError("Expect 0 or 1 argument(s)!")

                    if arguments == []:
                        return Type("nothing")

                    argument = arguments[0]
                    if isinstance(argument, Type):
                        return Type("type")

                    if isinstance(argument, Text):
                        return Type("text")

                    if isinstance(argument, Number):
                        return Type("number")

                    if isinstance(argument, Boolean):
                        return Type("boolean")

                    if isinstance(argument, Nothing):
                        return Type("nothing")

                    if isinstance(argument, Char):
                        return Type("char")

                    if isinstance(argument, Unsemi):
                        return Type("unsemi")

                case "cnum":
                    snip = snippet[i+1:]
                    arguments = get_args(snip)
                    if len(arguments) > 1:
                        raise ArgumentError("Expect 0 or 1 argument(s)!")

                    if arguments == []:
                        return Number(0)

                    argument = arguments[0]
                    if isinstance(argument, Boolean):
                        match argument.value:
                            case "yes":
                                return Number(1)
                            case "no":
                                return Number(0)

                    if isinstance(argument, Nothing):
                        return Number(0)

                    return create_number(argument.value)
                case "ctext":
                    '''
                    Mode:
                    0: text
                    1: unsemi
                    2: char

                    determined in the second arg
                    '''
                    snip = snippet[i+1:]
                    arguments = get_args(snip)
                    if len(arguments) != 2:
                        raise ArgumentError("Expect 2 arguments!")

                    value, mode = arguments[0], arguments[1]
                    match mode.value:
                        case 0:
                            return Text(value.value)
                        case 1:
                            return Unsemi(value.value)
                        case 2:
                            return Char(value.value)
                case "cbool":
                    snip = snippet[i+1:]
                    arguments = get_args(snip)
                    if len(arguments) != 1:
                        raise ArgumentError("Expect 1 argument!")

                    # truthy + falsy value
                    argument = arguments[0]
                    if isinstance(argument, Boolean):
                        return argument

                    if isinstance(argument, Nothing):
                        return Boolean("no")

                    if isinstance(argument, Number):
                        return Boolean(translate_boolean(argument.value != 0))

                    if isinstance(argument, (Text, Unsemi)):
                        return Boolean(translate_boolean(argument.value != ""))

                    if isinstance(argument, Char):
                        return Boolean("yes")

                    if isinstance(argument, Type):
                        return Boolean(translate_boolean(argument.value != "nothing"))
                case _:
                    raise SyntaxError(f"Unexpected instruction '{instruction}'!")
        case "@":
            # retrieve variables value
            if instruction:
                raise SyntaxError("Before @ does not contain anything!")
                
            var_name = ""
            i += 1
            while char_condition(snippet.lower(), i, VALIDS):
                var_name += snippet[i]
                i += 1

            if var_name not in variables:
                raise SyntaxError(f"Variable '{var_name}' not found!")

            return variables[var_name]
        case _:
            raise SyntaxError(f"Expect ' ', ':', ';', '@', not '{nexter}'!")

if __name__ == "__main__":
    file = input("Which file do you want to open? ")
    with open(f"{file}.ez") as file:
        CODE = file.read()

    line = 0
    lines = CODE.split("\n")
    variables = {}
    VALIDS = "abcdefghijklmnopqrstuvwxyz0123456789"
    while line < len(lines):
        if lines[line].strip():
            run(lines[line], variables, True)

        line += 1
