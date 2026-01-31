import unittest

from campaign import Campaign, CampaignAsset, Door, Room, CampaignEvent, Walker

class TestCampaign(unittest.TestCase):

    def test_campaignevent_creation(self):
        def event():
            pass
        CampaignEvent(event)
    
    def test_campaignevent_start(self):
        flags = {
            "triggered": False
        }
        event = CampaignEvent(lambda *_: flags.__setitem__("triggered", True))
        event.start(None)
        self.assertTrue(flags["triggered"])

    def test_campaignasset_creation_basic(self):
        CampaignAsset("Test asset")
    
    def test_campaignasset_on_off(self):
        asset = CampaignAsset("Test_asset")
        event1 = CampaignEvent(lambda: True)
        event2 = lambda: True
        # 'on' method should always accept CampaignEvent objects
        asset.on("test", event1)
        # 'on' method should accept callable objects (has the '__call__' method)
        asset.on("test", event2)
        with self.assertRaises(Exception, msg="'on' method should raise an exception if it receives a non-callable object."):
            asset.on("strings are not callable")
        
        self.assertIn(event1, asset.events["test"])
        self.assertTrue(1 == len(list(filter(lambda e: e.callback == event2, asset.events["test"]))))

        asset.off("test", event1)
        self.assertNotIn(event1, asset.events["test"])
        
        asset.off("test", event2)
        self.assertTrue(0 == len(list(filter(lambda e: e.callback == event2, asset.events["test"]))))
    
    def test_campaignasset_emit(self):
        state = {
            "complete": False
        }
        asset = CampaignAsset("Test_asset")
        asset.on("emit_test", CampaignEvent(lambda *_: state.__setitem__("complete", True)))
        asset.emit("emit_test")
        self.assertTrue(state["complete"])
    
    def test_campaignasset_tick(self):
        flags = {
            "tick": False
        }
        def callback(*_):
            flags["tick"] = True
        asset = CampaignAsset("Test asset")
        asset.on("tick", CampaignEvent(callback))
        asset.tick()
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
        def event1(*_):
            flags["event1_triggered"] = True
        room1 = Room("Test room", [], [CampaignEvent(event1)])
        room1.enter(None)
        self.assertTrue(flags["event1_triggered"])
    
    def test_door_enter(self):
        flags = {
            "door_event_triggered": False,
            "room_event_triggered": False
        }
        def event1(*_):
            flags["door_event_triggered"] = True
        def event2(*_): 
            flags["room_event_triggered"] = True
        room = Room("Test room", [], [CampaignEvent(event2)])
        door = Door("Test door", room)
        door.on("enter", CampaignEvent(event1))
        door.enter(None)
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

        def tick1(*_):
            flags["asset_1_tick"] = True
        def tick2(*_):
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
        def enter(_, w):
            print(f"{w.name} entered a dark tunnel.")
        def leave(_, w):
            print(f"{w.name} left the tunnel.")
            state["complete"] = True

        entry_room = Room("Entrance", [Door("Portal", last_room)])
        entry_room.on("enter", CampaignEvent(enter))
        campaign.add_room(entry_room)

        last_room = exit_room

        for i in range(1, 9):
            room = Room(f"{i}")
            room.on("enter", CampaignEvent(lambda r, w: print(f"{w.name} takes a step, {r.name} steps left ({r})...")))
            campaign.add_room(room, last_room)
            last_room = room
        
        
        exit_room = Room("Exit", [])
        exit_room.on("enter", CampaignEvent(leave))
        campaign.add_room(exit_room, last_room)

        walker = Walker("Jay", entry_room)
        entry_room.enter(walker)
        campaign.add_asset(walker)
        while not state["complete"]:
            campaign.tick()
        self.assertTrue(state["complete"])
        self.assertEqual(walker.room, exit_room)


    
if __name__ == "__main__":
    unittest.main()