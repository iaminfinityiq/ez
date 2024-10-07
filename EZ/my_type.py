from errors import ArgumentError

class Type:
    def __init__(self, value):
        """
        A representation of a type...
        """
        self.value = value

class Text:
    def __init__(self, value):
        """
        Just a normal text, not safe at all...
        """
        self.value = value

class Char:
    def __init__(self, value):
        """
        A character...
        """
        if len(value) != 1:
            raise ArgumentError(f"The argument for a char must only contain a character!")
        
        self.value = value

class Unsemi:
    def __init__(self, value):
        """
        Safer than Text but no semicolons allowed...
        """
        if ";" in value:
            raise ArgumentError(f"The argument for an Unsemi must not contain a semicolon!")
        
        self.value = value
        
class Number:
    def __init__(self, value):
        """
        A number...
        """
        self.value = value
        
class Nothing:
    def __init__(self):
        """
        What am I capable of?
        
        Programming!
        
        No, NOTHING!

        
        Am I useful in any case?
        
        ``show: boolean: yes``
        
        NUH UH, NO (oh wait, that's a boolean type :skull:)
        
        OMFG I can't type 💀💀💀?
        
        Oh wait I just typed it...

        My mind has ``nothing``...
        """
        self.value = "nothing"
        
class Boolean:
    def __init__(self, value):
        """
        Are you smart?

        Me and probably my partner: ``show: boolean: yes``

        Are you serious? Are you crazy???

        Me and probably my partner again: ``show: join: boolean: yes; char ; boolean: no``

        What language are yall saying?

        My partner and me: EZ! Please try out our new programming language: EZ. EZ has an EZ syntax (in 2 ways lol). It is very EZ to learn EZ xD
        """
        self.value = value

