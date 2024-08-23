from .command_token import Token

class StackNode:
    def __init__(self):
        self.is_terminal = True
        self.token_info = Token()
        self.oper = None
        self.left = None
        self.right = None