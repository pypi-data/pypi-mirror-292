from .enums.token_type import TokenType

class Token:
    def __init__(self):
        self.lexeme = ""
        self.TokenType = TokenType.ERROR