
from typing import Union

import parse

class Codable:
    def __init__(self):
        pass

    def get_payload(self):
        return ""
    
    def get_handle(self):
        return ""
    
    def get_tags(self):
        return []
    
    def insert(self,code):
        pass

class Code(Codable):
    def __init__(self,payload,handle,tags = None):
        self.payload = payload
        self.handle = handle
        self.tags = [] if tags is None else tags
    
    def add_tag(self,tag):
        if self.tags is None:
            self.tags = []
        self.tags.append(tag)

    def get_tags(self):
        return self.tags
    
    def get_handle(self):
        return self.handle
    
    def get_payload(self):
        return self.payload
    
    def __str__(self) -> str:
        return f'payload: "{self.payload}", handle: "{self.handle}"'
    
    def insert(self,code):
        if isinstance(code,Codable):
            payload = code.get_payload()
            if payload is None:
                return
            self.payload += payload
        else:
            raise Exception("insert expected a Codable object")

class Rule:
    def __init__(self):
        pass

    #code: the main file
    def exec(self,code,engine,args,slot=None):
        return Code('','')
    
    def eval_arg(self,code,engine,arg,slot=None):
        if arg.type != 'LIST':
            return engine.primitives(arg)
        return engine.exec(code,arg.val,slot)


id_replacement = ("!$%&*/<=>?@^_+-.","abcdefghijklmnop")

class Engine:
    def __init__(self):
        self.exprcount = 0
        self.debug = True
        self.files = {}
        self.namespace = {}
        self.rules = {}

    #name management
    def get_slot(self,slot):
        if slot is not None:
            return slot
        self.exprcount += 1
        return f"expr{self.exprcount}"
    
    def normalize(self,name):
        newname = ''
        for c in name:
            if c in id_replacement[0]:
                newname += f'_{id_replacement[1][id_replacement[0].index(c)]}_'
            else:
                newname += c
        return newname

    #file management
    def add_file(self,path,code):
        self.files[path] = code

    #namespace management
    def new_namespace(self,space):
        if isinstance(space,str):
            if self.namespace.get(space) is None:
                self.namespace[space] = {}
            return
        if isinstance(space,list):
            if len(space) == 0:
                return
            root = self.namespace.get(space[0])
            if root is None:
                root = {}
            for subspace in space[1:]:
                if root.get(subspace) is None:
                    root[subspace] = {}
            self.namespace[space[0]] = root
            return
        raise Exception("a namespace should be a list or a string")
    

    def set_track(self,space,var,value):
        self.new_namespace(space)
        if isinstance(space,str):
            self.namespace[space]['var+'+var] = value
        if isinstance(space,list):
            if len(space) == 0:
                raise Exception("space is empty")
            handle = self.namespace[space[0]]
            for subspace in space[1:]:
                handle = handle[subspace]
            handle['var+'+var] = value

    def get_track(self,space,var):
        if isinstance(space,str):
            return self.namespace[space].get('var+'+var)
        if isinstance(space,list):
            if len(space) == 0:
                raise Exception("space is empty")
            handle = self.namespace[space[0]]
            for subspace in space[1:]:
                handle = handle[subspace]
            return handle.get('var+'+var)
        

    #transpile primitives 
    def primitives(self,obj):
        pass

    #function calling
    def call_rule(self):
        pass


    #special form/rule handling
    def reg_rule(self,name,rule):
        self.rules[name] = rule

    #transpile
    def transpile(self,path):
        code = Code('','')
        file_obj = self.files[path]
        if not isinstance(file_obj,parse.Obj):
            raise Exception("expected an instance of Obj")
        if file_obj.type != 'FILE':
            raise Exception("expected an FILE Obj")
        for obj in file_obj.val:
            if not isinstance(obj,parse.Obj):
                raise Exception("expected an instance of Obj")
            if obj.type != 'LIST':
                raise Exception("only LIST objects can be at top level in a FILE")

            e = self.exec(code,obj.val)
            code.insert(e)
            code.handle = e.handle

        return code
            
    def exec(self,code,list,slot=None):
        if len(list) == 0:
            raise Exception("can't evaluate an empty list")
        name = list[0]
        if not isinstance(name,parse.Obj) or name.type != 'SYMBOL':
            raise Exception("expected a symbol")
        if name.val == 'using':
            return Code('','')
        args = list[1:] if len(list) > 1 else None
        rule = self.rules.get(name.val)
        if rule is None:
            return self.call_rule().exec(code,self,list,slot)
        else:
            return rule.exec(code,self,args,slot)

    
    def flush(self,code: Codable):
        return code.get_payload() + code.get_handle()
    
    #build the whole project
    def build(self,config,man):
        self.config = config
        self.man = man