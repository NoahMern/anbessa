
#this is a module manager code

from lexer import Lexer
from parse import Parser
from web import WEBEngine
from go import GoEngine

import re
import os

config_file_name = "config.ab"

class Eman:
    def __init__(self,path,engines):
        self.path = path
        self.engines = engines
        self.load_config()
        self.build()

    def load_config(self):
        files = os.listdir(self.path)
        if config_file_name not in files:
            raise Exception(f"The path {self.path} is not an anbessa module")
        with open(os.path.join(self.path,config_file_name)) as c:
            config = c.read()
        lexer = Lexer(config)
        parser = Parser(lexer)
        obj = parser.parse()
        if len(obj.val) != 1:
            raise Exception("expected a single entry in the config file")
        map_ = obj.val[0]
        if map_.type != "MAP":
            raise Exception("expected a map in the config file")
        # print(map_)
        self.config = {'root':self.path}
        self.eat_conf(map_)
        if not self.config.get('name'):
            raise Exception("a project should have a (:)name")
        if not self.config.get('version'):
            raise Exception("a project should have a (:)version")
        if not self.config.get('main'):
            raise Exception("a project should have a (:)main")

    def eat_conf(self,map_):
        i = 0
        while i < len(map_.val):
            obj = map_.val[i]
            if obj.type != 'KEYWORD':
                raise Exception("expected a keyword")
            if obj.val == ':name':
                #consume name
                i += 1
                obj2 = map_.val[i]
                if obj2.type != "STRING":
                    raise Exception("a project name can only be a string")
                self.config['name'] = obj2.val
            elif obj.val == ':version':
                i += 1
                obj2 = map_.val[i]
                if obj2.type != "STRING":
                    raise Exception("a project version can only be a string")
                if not self.is_valid_semantic_version(obj2.val):
                    raise Exception(f'invalid version {obj.val} given. Anbessa expects a semantic version')
                self.config['version'] = obj2.val 
            elif obj.val == ':description':
                i += 1
                obj2 = map_.val[i]
                if obj2.type != "STRING":
                    raise Exception("a project description can only be a string")
                self.config['description'] = obj2.val 
            elif obj.val == ':main':
                i += 1
                obj2 = map_.val[i]
                if obj2.type != "STRING":
                    raise Exception("a main can only be a string")
                if not obj2.val.endswith(".ab"):
                    raise Exception("the main file should be an Anbessa file ending with .ab")
                self.config['main'] = obj2.val 
            else:
                raise Exception(f"unexpected {obj}")
                
            i += 1

    def build(self):
        main = self.config['main']
        with open(os.path.join(self.config['root'],main)) as file:
            code = file.read()
        lexer = Lexer(code)
        parser = Parser(lexer)
        file = parser.parse()
        self.config['main_code'] = file
        ex = Exception(f"file {main} should start with the engine to use")
        if len(file.val) == 0:
            raise ex
        using = file.val[0]
        if using.type != 'LIST':
            raise ex
        if len(using.val) != 2:
            raise ex
        using_sym = using.val[0]
        if using_sym.type != 'SYMBOL' or using_sym.val != "using":
            raise ex
        engine = using.val[1]
        if engine.type != 'STRING':
            raise ex
        engine_ = self.engines.get(engine.val)
        if not engine_:
            raise Exception(f"the engine {engine.val} does not exist")
        engine_.build(self.config,self)
        
    
    def is_valid_semantic_version(self,version_string):
        pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$'
        if re.match(pattern, version_string):
            return True
        else:
            return False
        
    
    


web = WEBEngine()
go = GoEngine()
e = Eman("test",{'web':web,'go':go})


# {
#     :name "project name"
#     :version "project version"
#     :description  ""

#     :main "code.ab"

#     :dep [
#         "project-name"
#         "git-path"
#     ]

#     :sub [
#         "name"
#         "name"
#     ]
# }