
class Obj:
    def __init__(self,type_,val):
        self.type = type_
        self.val = val

    def __str__(self):
        if isinstance(self.val,list):
            return f"\n{self.type}("+",".join([str(v) for v in self.val]) + ")"
        return f"{self.type}({self.val})"
    
can_be_keys = ["STRING","KEYWORD","INT","FLOAT"]

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
    
    def error(self):
        raise Exception("Invalid syntax")
    
    def eat(self, type_):
        if self.current_token.type == type_:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def parse_form(self):
        form = []
        while True:
            if self.current_token.type == "RPAREN":
                break
            form.append(self.parse_atom())
        return form
    
    def parse_vec(self):
        form = []
        while True:
            if self.current_token.type == "RBRACKET":
                break
            form.append(self.parse_atom())
        return form
    
    def parse_map(self):
        form = []
        while True:
            if self.current_token.type == "RBRACE":
                break
            key = self.parse_atom()
            if key is None: #comments inside maps
                continue
            if key.type not in can_be_keys:
                raise Exception("shit")
            value = self.parse_atom()
            form.append(key)
            form.append(value)
        return form

    
    def parse_atom(self):
        token = self.current_token
        if token.type == 'INT':
            self.eat('INT')
            return Obj("INT",token.value)
        elif token.type == 'FLOAT':
            self.eat('FLOAT')
            return Obj("FLOAT",token.value)
        elif token.type == 'STRING':
            self.eat('STRING')
            return Obj("STRING",token.value)
        elif token.type == 'KEYWORD':
            self.eat('KEYWORD')
            return Obj("KEYWORD",token.value)
        elif token.type == 'TRUE':
            self.eat('TRUE')
            return Obj("TRUE",token.value)
        elif token.type == 'FALSE':
            self.eat('FALSE')
            return Obj("FALSE",token.value)
        elif token.type == 'NIL':
            self.eat('NIL')
            return Obj("NIL",token.value)
        # elif token.type == 'QUOTE':
        #     self.eat('QUOTE')
        #     return ['quote', self.parse_form()]
        elif token.type == 'HASH':
            self.eat('HASH')
            return Obj('PRAT', self.parse_atom())
        # elif token.type == 'TILDE':
        #     self.eat('TILDE')
        #     return ['unquote', self.parse_form()]
        elif token.type == 'LPAREN':
            self.eat('LPAREN')
            form = self.parse_form()
            self.eat('RPAREN')
            return Obj("LIST",form)
        elif token.type == 'LBRACKET':
            self.eat('LBRACKET')
            form = self.parse_vec()
            self.eat('RBRACKET')
            return Obj("VEC",form)
        elif token.type == 'LBRACE':
            self.eat('LBRACE')
            form = self.parse_map()
            self.eat('RBRACE')
            return Obj("MAP",form)
        elif token.type == 'ID':
            self.eat('ID')
            return Obj("SYMBOL",token.value)
        elif token.type == "COMMENT":
            self.eat('COMMENT')
            return None
        return Obj("EOF","EOF")
    
    def parse(self):
        form = []
        while True:
            atom = self.parse_atom()
            if atom is None:
                continue
            if atom.type == "EOF":
                break
            form.append(atom)
        return Obj("FILE",form)
    