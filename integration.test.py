import unittest

from campaign import Campaign, Room, Walker
from battle import Battle, Battler

class IntegrationTest(unittest.TestCase):
    def test_battle_event_room(self):
        campaign = Campaign()
        
        entrance = Room("Ouside the cave")
        cave = Room("Inside the cave")
        entrance.connect_to(cave, "Cave-mouth")
        party = Walker("Party", entrance)

        campaign.add_asset(entrance)
        campaign.add_asset(cave)
        campaign.add_asset(party)

        battle = Battle([Battler("Evan", 1, 1), Battler("John", 1, 1)], [Battler("Goblin 1", 1, 1),Battler("Goblin 2", 1, 1),Battler("Goblin 3", 1, 1)])

        flags = {
            "ended": False
        }
        def do_battle(*_):

            for n, e in battle:
                print(f"{n}: {e.battler.name} used {e.action.name} on {e.target.name}... {battle.turn_order}")
                if e.target.stats.health <= 0:
                    print(f"{e.target.name} dies.")

            flags["ended"] = True
        
        cave.on("enter", do_battle)

        while not flags["ended"]:
            campaign.tick()



    def test_walker_battle(self):
        pass

if __name__ == "__main__":
    unittest.main()