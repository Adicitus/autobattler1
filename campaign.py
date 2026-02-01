from collections.abc import Iterable
from typing import Any, Callable, Optional, Tuple

# Empty type declarations so that the names can be used in type hints
class CampaignEvent: pass
class CampaignAsset: pass
class Walker: pass
class Room: pass
class Door: pass
class Campaign: pass

class CampaignEvent:
    def __init__(self, callback:Callable[[CampaignAsset, Any], None]) -> None:
        self.callback: Callable[[CampaignAsset, Any], None] = callback

    def start(self, caller, event_data:any=None):
        self.callback(caller, event_data)

class CampaignAsset:
    def __init__(self, name:str="") -> None:
        self.name: str = name
        self.events: dict[str, list[Callable[[CampaignAsset, Any], None]]] = {
            "tick": []
        }

    def on(self, event_type: str, event: CampaignEvent | Callable[[CampaignAsset, Any], None]) -> None:
        e = event
        if not isinstance(e, CampaignEvent):
            if "__call__" in dir(e):
                e = CampaignEvent(e)
            else:
                raise Exception("Tried to create a CampaignEvent using a non-callable object.")

        if event_type not in self.events:
            self.events[event_type] = []

        if event in self.events[event_type]:
            return
        
        self.events[event_type].append(e)
    
    def off(self, event_type, event: CampaignEvent | Callable[[CampaignAsset, Any], None]):
        if event_type not in self.events:
            return
        
        if isinstance(event, CampaignEvent):
            self.events[event_type].remove(event)
            return
        
        if "__call__" not in dir(event):
            return
        
        self.events[event_type] = list(filter(lambda e: e.callback != event, self.events[event_type]))

    
    def emit(self, event_type:str, event_data:Any=None):
        if event_type not in self.events:
            return
        
        for e in self.events[event_type]:
            e.start(self, event_data)
    
    def tick(self):
        self.emit("tick")

class Walker(CampaignAsset):
    def __init__(self, name: str, starting_room: Room, door_select:Optional[Callable[[Iterable[Door]], Door]]=None) -> None:
        super().__init__(name)
        # Number of ticks between movements
        self.speed = 1
        self.ticks_passed = 0
        self.door_select = door_select

        if self.door_select == None:
            def select(doors:list):
                candidates = list(filter(lambda d: not d.room.visited, doors))
                if 0 < len(candidates):
                    return candidates[0]
                
                return None
                
            self.door_select = select

        # The room that the walker is currently located in
        self.room = starting_room

    def tick(self):
        super().tick()

        self.ticks_passed += 1
        if (self.ticks_passed < self.speed):
            return
        self.ticks_passed = 0

        # Just pick the first door for now
        door = self.door_select(self.room.doors)

        if door == None:
            return

        new_room = door.enter(self)
        if new_room == None:
            return
        self.room = new_room

class Room(CampaignAsset):
    def __init__(self, name:str, events:list=[]) -> None:
        super().__init__(name)
        self.doors: list[Door] = []
        self.events["enter"] = []
        for e in events:
            self.on("enter", e)
        self.visited = False
    
    def add_door(self, door):
        self.doors.append(door)
    
    def connect_to(self, room:Room) -> Tuple[Door, Door]:
        door1 = Door(name=f"door", room=room)
        door2 = Door(name=f"door", room=self)
        self.add_door(door1)
        room.add_door(door2)
        return (door1, door2)
    
    def disconnect_from(self, room:Room) -> None:
        self.doors = list(filter(lambda d: d.room != room, self.doors))

    def enter(self, walker:Walker) -> Room:
        
        self.visited = True
        self.emit("enter", walker)
        return self
    

class Door(CampaignAsset):
    def __init__(self, name:str="door", room:Room=None) -> None:
        super().__init__(name)
        self.name = name
        self.room = room
        self.events["enter"] = []
    
    def enter(self, walker:Walker) -> Optional(Room):
        self.emit("enter", walker)
        if self.room == None:
            return None
        return self.room.enter(walker)

class Campaign:
    def __init__(self, assets:Iterable[CampaignAsset]=[]) -> None:
        self.assets: list[CampaignAsset] = []
        self.rooms: list[Room]  = []

        for asset in assets:
            self.add_asset(asset)
    
    def add_asset(self, asset:CampaignAsset) -> None:
        if asset in self.assets:
            return

        if isinstance(asset, Room):
            self.rooms.append(asset)
        
        self.assets.append(asset)
    
    def add_room(self, room:Room, enter_from:Room = None) -> None | Tuple[Door, Door]:
        self.add_asset(room)
        if enter_from != None:
            return room.connect_to(enter_from)
    
    def remove_asset(self, asset:CampaignAsset) -> None:
        if asset not in self.assets:
            return
        
        if isinstance(asset, Room):
            for r in self.rooms:
                r.disconnect_from(asset)
            self.rooms.remove(asset)

        self.assets.remove(asset)
    
    def tick(self):
        for asset in self.assets:
            asset.tick()