from asyncio import events
from sys import flags
import unittest

from campaign import Campaign, CampaignAsset, Door, Room, CampaignEvent

class TestCampaign(unittest.TestCase):

    def test_campaignevent_creation(self):
        def event():
            pass
        CampaignEvent(event)
    
    def test_campaignevent_start(self):
        flags = {
            "triggered": False
        }
        def callback(assets):
            flags["triggered"] = True
        event = CampaignEvent(callback)
        event.start(None)
        self.assertTrue(flags["triggered"])

    def test_campaignasset_creation_basic(self):
        CampaignAsset("Test asset")
    
    def test_campaignasset_on_off(self):
        asset = CampaignAsset("Test_asset")
        event = CampaignEvent(lambda: True)
        asset.on("test", event)
        self.assertTrue(event in asset.events["test"])
        asset.off("test", event)
        self.assertTrue(event not in asset.events["test"])
    
    def test_campaignasset_emit(self):
        state = {
            "complete": False
        }
        asset = CampaignAsset("Test_asset")
        asset.on("emit_test", CampaignEvent(lambda _: state.__setitem__("complete", True)))
        asset.emit("emit_test")
        self.assertTrue(state["complete"])
    
    def test_campaignasset_tick(self):
        flags = {
            "tick": False
        }
        def callback(_):
            flags["tick"] = True
        asset = CampaignAsset("Test asset")
        asset.on("tick", CampaignEvent(callback))
        asset.tick([])
        self.assertTrue(flags["tick"])

    def test_room_creation_basic(self):
        Room("Test room", [])

    def test_door_creation(self):
        room = Room("Test room", [])
        Door("Test door", room)

    def test_room_enter(self):
        flags = {
            "event1_triggered": False
        }
        def event1(party):
            flags["event1_triggered"] = True
        room1 = Room("Test room", [], [CampaignEvent(event1)])
        room1.enter()
        self.assertTrue(flags["event1_triggered"])
    
    def test_door_enter(self):
        flags = {
            "door_event_triggered": False,
            "room_event_triggered": False
        }
        def event1(_):
            flags["door_event_triggered"] = True
        def event2(_): 
            flags["room_event_triggered"] = True
        room = Room("Test room", [], [CampaignEvent(event2)])
        door = Door("Test door", room)
        door.on("enter", CampaignEvent(event1))
        door.enter()
        self.assertTrue(flags["door_event_triggered"])
        self.assertTrue(flags["room_event_triggered"])
    
    def test_campaign_creation_basic(self):
        Campaign([])
    
    def test_campaign_add_remove_asset(self):
        campaign = Campaign()
        asset = CampaignAsset()
        campaign.add_asset(asset)
        self.assertTrue(asset in campaign.assets)
        campaign.remove_asset(asset)
        self.assertTrue(asset not in campaign.assets)

    def test_campaign_tick(self):

        flags = {
            "asset_1_tick": False,
            "asset_2_tick": False,
        }

        def tick1(_):
            flags["asset_1_tick"] = True
        def tick2(_):
            flags["asset_2_tick"] = True

        test_asset1 = CampaignAsset("Test asset 1")
        test_asset1.on("tick", CampaignEvent(tick1))
        test_asset2 = CampaignAsset("Test asset 2")
        test_asset2.on("tick", CampaignEvent(tick2))
        assets = [test_asset1, test_asset2]
        campaign = Campaign(assets)
        campaign.tick()
        self.assertTrue(flags["asset_1_tick"])
        self.assertTrue(flags["asset_2_tick"])

    def test_campaign_walk(self):
        campaign = Campaign([])
        state = {
            "complete": False
        }
        def enter(_):
            print("Entered a dark tunnel.")
        def walk(_):
            d = state["current_room"].doors[0]
            d.enter()
            state["current_room"] = d.room
        def leave(_):
            print("Left the tunnel.")
            state["complete"] = True

        exit_room = Room("Exit", [])
        exit_room.on("enter", CampaignEvent(leave))
        campaign.add_asset(exit_room)

        last_room = exit_room

        for i in range(1, 9):
            room = Room(f"{i}", [Door("Portal", last_room)])
            last_room = room
            room.on("enter", CampaignEvent(lambda r: print(f"{r.name} steps left ({id(r)})...")))
            campaign.add_asset(room)
        
        entry_room = Room("Entrance", [Door("Portal", last_room)])
        entry_room.on("enter", CampaignEvent(enter))
        campaign.add_asset(entry_room)

        state["current_room"] = entry_room
        entry_room.enter()

        walker = CampaignAsset("Walker")            
        walker.on("tick", CampaignEvent(walk))
        campaign.add_asset(walker)
        while not state["complete"]:
            campaign.tick()
        self.assertTrue(state["complete"])
        self.assertEqual(state["current_room"], exit_room)


    
if __name__ == "__main__":
    unittest.main()