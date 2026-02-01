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
    """
    Wrapper around basic callables when used in Campaign eventing.
    """
    def __init__(self, callback:Callable[[CampaignAsset, Any], None]) -> None:
        self.enabled: bool = True
        """Determines if this event can start or not."""
        self.callback: Callable[[CampaignAsset, Any], None] = callback
        """Callable to run then this event starts"""

    def start(self, caller:CampaignAsset, event_data:any=None):
        """
        Calls the wrapped callable if this event is enabled, otherwise does nothing.

        The callable is called using the given 'caller' as the first argument, and the given event_data as the second argument:
            callable(caller, event_data)
        """
        if self.enabled:
            self.callback(caller, event_data)

class CampaignAsset:
    """
    Basic asset used in campaigns, implements .tick and basic event emitter functionality.
    TODO: Inherit pymitter (https://pypi.org/project/pymitter/)?
    """
    def __init__(self, name:str="") -> None:
        self.name: str = name
        self.events: dict[str, list[Callable[[CampaignAsset, Any], None]]] = {
            "tick": []
        }

    def on(self, event_type: str, event: CampaignEvent | Callable[[CampaignAsset, Any], None]) -> None:
        """
        Adds the given callable or CampaignEvent to the list of event handlers for the given event_type.

        Note: This method can be used to add event handlers for events not emitted by this object.
        """
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
    
    def off(self, event_type:str, event: CampaignEvent | Callable[[CampaignAsset, Any], None]) -> None:
        """
        Removes the given callable or CampaignEvent as handlers for the given event_type.

        Does nothing if the given event has not been added for the event_type.
        """
        if event_type not in self.events:
            return
        
        if isinstance(event, CampaignEvent):
            self.events[event_type].remove(event)
            return
        
        if "__call__" not in dir(event):
            return
        
        self.events[event_type] = list(filter(lambda e: e.callback != event, self.events[event_type]))

    
    def emit(self, event_type:str, event_data:Any=None) -> None:
        """
        Calls any CampaignEvent objects registered for the given event_type, using the given event_data.

        Does nothing if no CampaignEvents are registered for the event_type. 
        """
        if event_type not in self.events:
            return
        
        for e in self.events[event_type]:
            e.start(self, event_data)
    
    def tick(self):
        """
        Advances any game logic associated with this asset. Emits the "tick" event.
        """
        self.emit("tick")

class Walker(CampaignAsset):
    def __init__(self, name: str, starting_room: Room, door_select:Optional[Callable[[Iterable[Door]], Door]]=None) -> None:
        super().__init__(name)
        # Number of ticks between movements
        self.speed: int = 1
        self.ticks_passed: int = 0
        self.door_select: Callable[[Iterable[Door]], Door] = door_select

        if self.door_select == None:
            def select(doors:list):
                candidates = list(filter(lambda d: not d.room.visited, doors))
                if 0 < len(candidates):
                    return candidates[0]
                
                return None
                
            self.door_select = select

        # The room that the walker is currently located in
        self.room: Room = starting_room
        self.room.enter(self)

    def tick(self) -> None:
        """
        Emits the "tick" event, then tries to enter the door given by self.door_select (unless it returns None).
        """
        super().tick()

        self.ticks_passed += 1
        if (self.ticks_passed < self.speed):
            return
        self.ticks_passed = 0

        door = self.door_select(self.room.doors)

        if door == None:
            return

        new_room = door.enter(self)
        if new_room == None:
            return
        self.room.leave(self)
        self.room = new_room

class Room(CampaignAsset):
    def __init__(self, name:str, events:list=[]) -> None:
        super().__init__(name)
        self.doors: list[Door] = []
        self.walkers: list[Walker] = []
        self.events["enter"] = []
        for e in events:
            self.on("enter", e)
        self.visited = False
    
    def add_door(self, door:Door) -> None:
        """
        Manually adds a single door instance to the room. This can be used to add special doors (like random teleportation).
        """
        self.doors.append(door)
    
    def connect_to(self, room:Room) -> Tuple[Door, Door]:
        """
        Connects this room to another room by creating a new door in each room.

        Returns a tuple with the new doors: The first door is the one added to this room, the second is the door added to the other room.
        """
        door1 = Door(name=f"door", room=room)
        door2 = Door(name=f"door", room=self)
        self.add_door(door1)
        room.add_door(door2)
        return (door1, door2)
    
    def disconnect_from(self, room:Room) -> None:
        """
        Removes the door connecting this door to the given room.

        Does not remove the door in the given room, it needs to be removed manually.
        """
        self.doors = list(filter(lambda d: d.room != room, self.doors))

    def enter(self, walker:Walker) -> Room:
        """
        Adds the given walker to this room, if it is not already present.

        If the walker is added to the room, the "enter" event is emitted.

        Returns this room.
        """
        if walker not in self.walkers:
            self.visited = True
            self.walkers.append(walker)
            self.emit("enter", walker)
        return self
    
    def leave(self, walker:Walker) -> None:
        """
        If the given walker is present in this room, removes the walker and emits the "leave" event.

        If the walker is not present in this room, this method does nothing.
        """
        if walker not in self.walkers:
            return
        self.walkers.remove(walker)
        self.emit("leave", walker)

class Door(CampaignAsset):
    def __init__(self, name:str="door", room:Room=None) -> None:
        super().__init__(name)
        self.name = name
        self.room = room
        self.events["enter"] = []
    
    def enter(self, walker:Walker) -> Optional[Room]:
        """
        Attempts to pass the walker through this door, emitting the "enter" event.

        Returns a Room object representing the room on the other side of the door, or None if passage is rejected.
        """
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