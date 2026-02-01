import unittest

from campaign import Campaign, CampaignAsset, Door, Room, CampaignEvent, Walker

class TestCampaign(unittest.TestCase):

    def test_campaignevent_creation(self):
        CampaignEvent(lambda: True)
    
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
        Room("Test room")

    def test_door_creation(self):
        room = Room("Test room")
        Door("Test door", room)
    
    def test_room_connect_disconnect(self):
        room1 = Room("R1")
        room2 = Room("R1")
        door1, door2 = room1.connect_to(room2)

        self.assertIsInstance(door1, Door)
        self.assertIsInstance(door2, Door)
        self.assertIn(door1, room1.doors)
        self.assertIn(door2, room2.doors)
        self.assertEqual(len(room1.doors), 1)
        self.assertEqual(room1.doors[0].room, room2)
        self.assertEqual(len(room2.doors), 1)
        self.assertEqual(room2.doors[0].room, room1)

        room1.disconnect_from(room2)
        self.assertEqual(len(room1.doors), 0)
        room2.disconnect_from(room1)
        self.assertEqual(len(room2.doors), 0)


    def test_room_enter(self):
        flags = {
            "event1_triggered": False
        }
        def event1(*_):
            flags["event1_triggered"] = True
        room1 = Room("Test room", [CampaignEvent(event1)])
        
        self.assertEqual(len(room1.walkers), 0)
        r = room1.enter(None)

        self.assertEqual(r, room1)
        self.assertEqual(len(r.walkers), 1)
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
        
        room = Room("Test room", [CampaignEvent(event2)])
        door = Door("Test door", room)
        door.on("enter", CampaignEvent(event1))
        r = door.enter(None)
        self.assertEqual(room, r)
        self.assertEqual(len(r.walkers), 1)
        self.assertTrue(flags["door_event_triggered"])
        self.assertTrue(flags["room_event_triggered"])
    
    def test_door_enter_reject(self):
        # A false door:
        door = Door("portal", None)
        room = door.enter(None)
        self.assertIsNone(room)

    def test_walker_enter_leave(self):
        room0 = Room("Room 0")
        room1 = Room("Room 1")
        self.assertEqual(len(room0.doors), 0, "A newly created Room shouldn't have any doors")
        self.assertEqual(len(room0.walkers), 0, "A newly created Room shouldn't contain any Walkers")
        self.assertEqual(len(room1.doors), 0, "A newly created Room shouldn't have any doors")
        self.assertEqual(len(room1.walkers), 0, "A newly created Room shouldn't contain any Walkers")

        walker = Walker("Jay", room0)
        self.assertEqual(walker.room, room0, f"Walker '{walker.name}' should have had its current room set to Room 0 since it is their starting room")
        self.assertIn(walker, room0.walkers, f"Walker '{walker.name}' should have been added to Room 0 since it is their starting room")
        
        room1.enter(walker)
        self.assertIn(walker, room1.walkers, f"Walker '{walker.name}' should have been added Room 1 when it entered")
        room0.leave(walker)
        self.assertEqual(len(room0.walkers), 0, f"Walker '{walker.name}' should have been removed from Room 0 by the .leave method")
    
    def test_walker_tick_basic(self):
        room0 = Room("Room 0")
        room1 = Room("Room 1")
        self.assertEqual(len(room0.doors), 0, "A newly created Room shouldn't have any doors")
        self.assertEqual(len(room0.walkers), 0, "A newly created Room shouldn't contain any Walkers")
        self.assertEqual(len(room1.doors), 0, "A newly created Room shouldn't have any doors")
        self.assertEqual(len(room1.walkers), 0, "A newly created Room shouldn't contain any Walkers")

        room0.connect_to(room1)
        self.assertEqual(len(room0.doors), 1, "Room 0 should have been connected to room 1")
        self.assertEqual(len(room1.doors), 1, "Room 1 should have been connected to room 0")
        
        walker = Walker("Jay", room0)
        self.assertEqual(walker.room, room0, f"Walker '{walker.name}' should have had its current room set to {room0.name} since it is their starting room")
        self.assertIn(walker, room0.walkers, f"Walker '{walker.name}' should have been added to {room0.name} since it is their starting room")

        walker.tick()
        self.assertEqual(walker.room, room1, f"Walker '{walker.name}' should have moved into {room1.name} since it is the only room connected to {room0.name}")
        self.assertIn(walker, room1.walkers, f"Walker '{walker.name}' should have been added to {room1.name}")
        self.assertEqual(len(room0.walkers), 0, f"Walker '{walker.name}' should have been removed from {room0.name}")

    def test_walker_tick_custom_select(self):
        room0 = Room("Room 0")
        room1 = Room("Room 1")
        room2 = Room("Room 2")

        room0.connect_to(room1)
        room0.connect_to(room2)

        walker1 = Walker("Jay", room0, door_select=lambda doors: doors[0])
        walker2 = Walker("Kay", room0, door_select=lambda doors: doors[-1])

        self.assertIn(walker1, room0.walkers)
        self.assertIn(walker2, room0.walkers)

        walker1.tick()
        walker2.tick()

        self.assertIn(walker1, room1.walkers, f"Walker {walker1.name} should have entered {room1.name} since it connects through the first door in {room0.name}")
        self.assertIn(walker2, room2.walkers, f"Walker {walker1.name} should have entered {room2.name} since it connects through the last door in {room0.name}")
    
    def test_campaign_creation_basic(self):
        Campaign()
    
    def test_campaign_add_remove_asset(self):
        campaign = Campaign()
        asset = CampaignAsset()
        campaign.add_asset(asset)
        self.assertTrue(asset in campaign.assets)
        campaign.remove_asset(asset)
        self.assertTrue(asset not in campaign.assets)

    def test_campaign_add_remove_room(self):
        campaign = Campaign()
        room1 = Room("Room1")
        room2 = Room("Room2")

        campaign.add_room(room1)
        self.assertIn(room1, campaign.assets)
        self.assertIn(room1, campaign.rooms)
        self.assertEqual(len(room1.doors), 0)
        
        campaign.add_room(room2, room1)
        
        self.assertIn(room2, campaign.assets)
        self.assertIn(room2, campaign.rooms)
        self.assertEqual(len(room1.doors), 1)
        self.assertEqual(room1.doors[0].room, room2)
        self.assertEqual(len(room2.doors), 1)
        self.assertEqual(room2.doors[0].room, room1)

        campaign.remove_asset(room1)

        self.assertNotIn(room1, campaign.assets)
        self.assertNotIn(room1, campaign.rooms)
        self.assertEqual(len(room2.doors), 0)

    def test_campaign_tick(self):

        flags = {
            "asset_1_tick": False,
            "asset_2_tick": False,
        }

        test_asset1 = CampaignAsset("Test asset 1")
        test_asset1.on("tick", lambda *_: flags.__setitem__("asset_1_tick", True))
        test_asset2 = CampaignAsset("Test asset 2")
        test_asset2.on("tick", lambda *_: flags.__setitem__("asset_2_tick", True))
        assets = [test_asset1, test_asset2]
        campaign = Campaign(assets)
        campaign.tick()
        self.assertTrue(flags["asset_1_tick"])
        self.assertTrue(flags["asset_2_tick"])

    def test_campaign_walk(self):
        
        campaign = Campaign()
        state = {
            "complete": False
        }
        def enter(_, w):
            print(f"{w.name} entered a dark tunnel.")
        def leave(_, w):
            print(f"{w.name} left the tunnel.")
            state["complete"] = True

        entry_room = Room("Entrance", [enter])
        campaign.add_room(entry_room)

        last_room = entry_room

        for i in range(1, 9):
            room = Room(f"{9-i}")
            room.on("enter", CampaignEvent(lambda r, w: print(f"{w.name} takes a step, {r.name} steps left ({r})...")))
            campaign.add_room(room, last_room)
            last_room = room
        
        
        exit_room = Room("Exit", [leave])
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