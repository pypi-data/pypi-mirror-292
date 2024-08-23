class InputBuffer:
    def __init__(self, input_string):
        self.input_string = input_string
        self.eof = False
        self.input_buffer = []

    def end_of_input(self):
        if self.input_buffer:
            return False
        else:
            return self.eof
        
    def unget_char(self, c):
        if (c != '$'):
            self.input_buffer.append(c)
    
    def get_char(self):
        if self.input_buffer:
            return self.input_buffer.pop()
        else:
            try:
                c = self.input_string[0]
                self.input_string = self.input_string[1:len(self.input_string)]
                return c
            except:
                self.eof = True
                return '$'