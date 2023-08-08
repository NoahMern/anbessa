
from engine import Engine,Code,Rule

import os

class CallRule(Rule):
    def exec(self, code, engine, args, slot=None):
        call = args[0]
        new_args = args[1:] if len(args) > 1 else []
        exec_args = [self.eval_arg(code,engine,arg,slot) for arg in new_args]
        b = engine.bmap.get(call.val)
        if b:
            return self.exec_rule(engine,b,exec_args,slot)
    
    def exec_rule(self,engine,name,args,slot):
        code = Code('','',['inline'])
        for arg in args:
            code.insert(arg)
        handle = f"{name}(" + ",".join([arg.handle for arg in args]) + ')'
        code.handle = handle
        return code

class DefRule(Rule):
    def exec(self, code, engine, args, slot=None):
        c = Code('','')
        if len(args) != 2:
            raise Exception("def expected 2 arguments")
        name = args[0]
        if name.type != 'SYMBOL':
            raise Exception("the first argument is expected to be a symbol in def")
        normal = engine.normalize(name.val)
        val = args[1]
        arg_code = self.eval_arg(code,engine,val)
        c.insert(arg_code)
        c.payload += f'let {normal} = {arg_code.handle};'
        c.handle = normal
        engine.set_track('global',normal,'var') #register the creation of a variable in the global namespace
        return c
    
class OP(Rule):
    def __init__(self,rule):
        super().__init__()
        self.rule = rule
    def exec(self, code, engine, args, slot=None):
        c = Code('','',['inline'])
        for arg in args:
            self.eval_arg(code,engine)
        return c
        
        

call_rule = CallRule()

class WEBEngine(Engine):
    def __init__(self):
        super().__init__()
        self.lang = "web"
        self.new_namespace('global')
        self.bmap = {
            'print':'print_',
            'browser.alert': 'alert',
            'lang.author': '"Noah.Y"'
        }
        #rules
        self.reg_rule('def',DefRule())

    def build(self,config,man):
        super().build(config,man)
        #add config to b maps
        self.bmap['project.name'] = f'"{config["name"]}"'
        self.bmap['project.version'] = f'"{config["version"]}"'
        main = self.config['main']
        self.add_file(main,self.config['main_code'])
        gen = self.flush(self.transpile(main))
        gen_name = os.path.join(self.config['root'], main+'.js')
        with open(gen_name,'w') as file:
            file.write(self.load_runtime())
            file.write(gen)
        os.system(f'node {gen_name}')

    def load_runtime(self):
        with open('runtime/web/runtime.js') as lib:
            code = lib.read()
        return code

    def call_rule(self):
        return call_rule
    
    def primitives(self, obj):
        if obj.type == 'STRING':
            return Code('',f'"{obj.val}"',['inline'])
        if obj.type == 'SYMBOL':
            b = self.bmap.get(obj.val)
            if b is not None:
                return Code('',b)
            if not self.get_track('global', self.normalize(obj.val)):
                raise Exception(f'unknown variable {obj.val}')
            return Code('',f'{self.normalize(obj.val)}',['inline'])
        if obj.type == 'INT' or obj.type == 'FLOAT':
            pass
    