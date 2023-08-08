
from lexer import Lexer
from parse import Parser

if __name__ == "__main__":

    with open("code.ab") as f:
        text = f.read()

    lexer = Lexer(text)
    # while True:
    #     tkn = lexer.get_next_token()
    #     if tkn.type == 'EOF':
    #         break
    #     print(tkn)

    parser = Parser(lexer)
    obj = parser.parse()
    print(obj)