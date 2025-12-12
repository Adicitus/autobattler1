import unittest

from battle import Battle, Battler

class TestBattle(unittest.TestCase):

    def test_battler_creation(self):
        Battler("A", 1, 1)
    
    def test_battler_attack(self):
        a = Battler("A", 1, 1)
        b = Battler("B", 1, 1)
        t = a.attack([a], [b])
        self.assertEqual(t, b)
        self.assertEqual(b.health, 0)
    
    def test_battle_creation_both_empty(self):
        battle = Battle([], [])
        self.assertEqual(battle.teams[0], [])
        self.assertEqual(battle.teams[1], [])
        self.assertEqual(battle.turn_order, [])
    
    def test_battle_creation_one_empty(self):
        team1  = [Battler("A", 1, 1)]
        team2  = []
        battle = Battle(team1, team2)
        self.assertEqual(len(battle.teams[0]), 1)
        self.assertEqual(len(battle.teams[1]), 0)
        self.assertEqual(battle.teams[0], team1)
        self.assertEqual(battle.teams[1], team2)
        self.assertEqual(len(battle.turn_order), 1)
    
    def test_battle_creation(self):
        team1  = [Battler("A", 1, 1)]
        team2  = [Battler("B", 1, 1)]
        battle = Battle(team1, team2)
        self.assertEqual(len(battle.teams[0]), 1)
        self.assertEqual(len(battle.teams[1]), 1)
        self.assertEqual(battle.teams[0], team1)
        self.assertEqual(battle.teams[1], team2)
        self.assertEqual(len(battle.turn_order), 2)
    
    def test_battle_creation_next(self):
        a = Battler("A", 1, 1)
        b = Battler("B", 1, 1)
        team1  = [a]
        team2  = [b]
        battle = Battle(team1, team2)
        turn_num, battler, target = battle.next()
        self.assertEqual(turn_num, battle.current_turn)
        self.assertEqual(turn_num, 1)
        self.assertEqual(battler, a)
        self.assertEqual(target, b)
        self.assertEqual(len(team2), 0)
        self.assertEqual(len(battle.turn_order), 1)
        self.assertEqual(target.health, 0)



if __name__ == "__main__":
    unittest.main()