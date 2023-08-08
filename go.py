
from engine import Engine,Code,Rule

class GoEngine(Engine):
    def __init__(self):
        super().__init__()
        self.lang = "go"
        self.new_namespace('global')

    def primitives(self, obj):
        return super().primitives(obj)
    
    def build(self, config, man):
        return super().build(config, man)
    
    def call_rule(self):
        return super().call_rule()