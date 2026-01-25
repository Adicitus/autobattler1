
class CampaignEvent:
    def __init__(self, callback) -> None:
        self.callback = callback
    
    def start(self, caller):
        self.callback(caller)

class CampaignAsset:
    def __init__(self, name:str="") -> None:
        self.name = name
        self.events = {
            "tick": []
        }

    def on(self, event_type: str, event: CampaignEvent):
        if event_type not in self.events:
            self.events[event_type] = []

        if event in self.events[event_type]:
            return
        
        self.events[event_type].append(event)
    
    def off(self, event_type, event:CampaignEvent):
        if event_type not in self.events:
            return
        
        self.events[event_type].remove(event)
    
    def emit(self, event_type:str):
        if event_type not in self.events:
            return
        
        for e in self.events[event_type]:
            e.start(self)
    
    def tick(self, campaign_assets:list):
        self.emit("tick")

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
    
    def enter(self):
        self.visited = True
        self.emit("enter")
    

class Door(CampaignAsset):
    def __init__(self, name:str, room:Room) -> None:
        super().__init__(name)
        self.name = name
        self.room = room
        self.events["enter"] = []
    
    def enter(self):
        self.emit("enter")
        self.room.emit("enter")

class Campaign:
    def __init__(self, assets:list=[]) -> None:
        self.assets = assets
    
    def add_asset(self, asset:CampaignAsset):
        if asset in self.assets:
            return
        self.assets.append(asset)
    
    def remove_asset(self, asset:CampaignAsset):
        if asset not in self.assets:
            return
        self.assets.remove(asset)
    
    def tick(self):
        for asset in self.assets:
            asset.tick(self.assets)