
id_chars = '!$%&*/<=>?@^_+-.'

class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value
    
    def __repr__(self):
        return f"Token({self.type}, {self.value})"

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]
    
    def error(self):
        raise Exception("Invalid character")
    
    def advance(self):
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
    
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace() or self.current_char == ',':
            self.advance()

    def scan_number(self,res = '',isf= False):
        result = res
        is_float = isf
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.' or self.current_char == '_'):
            if self.current_char == '_':
                self.advance()
                continue
            if self.current_char == '.':
                if is_float:
                    self.error()
                is_float = True
            result += self.current_char
            self.advance()
        if is_float:
            return Token('FLOAT', float(result))
        else:
            return Token('INT', int(result))
    
    def scan_identifier(self):
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char in id_chars):
            result += self.current_char
            self.advance()
        if result == 'nil':
            return Token('NIL', result)
        if result == 'true':
            return Token('TRUE', result)
        if result == 'false':
            return Token('FALSE', result)
        return Token('ID', result)
    
    def scan_string(self):
        result = ''
        escape = False
        while True:
            self.advance()
            if self.current_char is None:
                self.error()
            elif escape:
                if self.current_char == 'n':
                    result += '\n'
                elif self.current_char == 't':
                    result += '\t'
                elif self.current_char == '\\':
                    result += '\\'
                elif self.current_char == '\"':
                    result += '\"'
                else:
                    self.error()
                escape = False
            elif self.current_char == '\\':
                escape = True
            elif self.current_char == '"':
                self.advance()
                return Token('STRING', result)
            else:
                result += self.current_char

    def scan_keyword(self):
        result = ':'
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char in id_chars):
            result += self.current_char
            self.advance()
        return Token('KEYWORD', result)
    
    def scan_comment(self):
        result = ''
        while self.current_char is not None and self.current_char != "\n":
            result += self.current_char
            self.advance()
            
        return Token('COMMENT',result.lstrip(';'))
    
    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace() or self.current_char == ',':
                self.skip_whitespace()
                continue
            elif self.current_char.isdigit():
                return self.scan_number()
            elif self.current_char == '.':
                self.advance()
                return self.scan_number('0.',True)
            elif self.current_char == ';':
                self.advance()
                return self.scan_comment()
            elif self.current_char == "'":
                self.advance()
                return Token('QUOTE', "'")
            elif self.current_char == '#':
                self.advance()
                return Token('HASH', '#')
            elif self.current_char == ':':
                self.advance()
                return self.scan_keyword()
            elif self.current_char == '~':
                self.advance()
                return Token('TILDE', '~')
            elif self.current_char == '(':
                self.advance()
                return Token('LPAREN', '(')
            elif self.current_char == ')':
                self.advance()
                return Token('RPAREN', ')')
            elif self.current_char == '[':
                self.advance()
                return Token('LBRACKET', '[')
            elif self.current_char == ']':
                self.advance()
                return Token('RBRACKET', ']')
            elif self.current_char == '{':
                self.advance()
                return Token('LBRACE', '{')
            elif self.current_char == '}':
                self.advance()
                return Token('RBRACE', '}')
            elif self.current_char == '"':
                return self.scan_string()
            elif self.current_char.isalpha() or self.current_char in id_chars:
                return self.scan_identifier()
            else:
                self.error()
        return Token('EOF', None)
    



