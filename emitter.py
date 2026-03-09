from typing import Any, Callable

class Emitter: pass

class Emitter:

    def __init__(self) -> None:
        self.events = {}
    
    def on(self, event_name:str, handler: Callable[[Emitter, Any], bool] ) -> None:
        if event_name not in self.events:
            self.events[event_name] = []
        
        self.events[event_name].append(handler)
        
    def off(self, event_name, handler: Callable[[Emitter, Any], bool]):
        if event_name not in self.events:
            return
        
        self.events[event_name].remove(handler)


    def emit(self, event_name:str, data:Any) -> None:
        if event_name not in self.events:
            return
        
        self.events[event_name] = list(filter(lambda h: h(self, data), self.events[event_name]))