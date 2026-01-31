from os import name


class CampaignEvent:
    def __init__(self, callback) -> None:
        self.callback = callback

    def start(self, caller, event_data:any=None):
        self.callback(caller, event_data)

class CampaignAsset:
    def __init__(self, name:str="") -> None:
        self.name = name
        self.events = {
            "tick": []
        }

    def on(self, event_type: str, event: CampaignEvent):
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
    
    def off(self, event_type, event:CampaignEvent):
        if event_type not in self.events:
            return
        
        if isinstance(event, CampaignEvent):
            self.events[event_type].remove(event)
            return
        
        if "__call__" not in dir(event):
            return
        
        self.events[event_type] = list(filter(lambda e: e.callback != event, self.events[event_type]))

    
    def emit(self, event_type:str, event_data:any=None):
        if event_type not in self.events:
            return
        
        for e in self.events[event_type]:
            e.start(self, event_data)
    
    def tick(self):
        self.emit("tick")

class Walker(CampaignAsset):
    def __init__(self, name: str, starting_room, door_select=None, speed=1) -> None:
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

        self.room = door.enter(self)

class Room(CampaignAsset):
    def __init__(self, name:str, doors:list=[], events:list=[]) -> None:
        super().__init__(name)
        self.doors = []
        for d in doors:
            self.doors.append(d)
        self.events["enter"] = []
        for e in events:
            self.on("enter", e)
        self.visited = False
    
    def add_door(self, door):
        self.doors.append(door)
    
    def connect_to(self, room):
        door1 = Door(name=f"door to {self.name}", room=self)
        door2 = Door(name=f"door to {room.name}", room=room)
        room.add_door(door1)
        self.add_door(door2)
        return (door1, door2)

    def enter(self, walker:Walker):
        self.visited = True
        self.emit("enter", walker)
        return self
    

class Door(CampaignAsset):
    def __init__(self, name:str, room:Room) -> None:
        super().__init__(name)
        self.name = name
        self.room = room
        self.events["enter"] = []
    
    def enter(self, walker:Walker) -> Room:
        self.emit("enter", walker)
        if self.room == None:
            return None
        return self.room.enter(walker)

class Campaign:
    def __init__(self, assets:list=[]) -> None:
        self.assets = assets
    
    def add_asset(self, asset:CampaignAsset):
        if asset in self.assets:
            return
        self.assets.append(asset)
    
    def add_room(self, room:Room, enter_from:Room = None):
        self.add_asset(room)
        if enter_from != None:
            return room.connect_to(enter_from)
    
    def remove_asset(self, asset:CampaignAsset):
        if asset not in self.assets:
            return
        self.assets.remove(asset)
    
    def tick(self):
        for asset in self.assets:
            asset.tick()