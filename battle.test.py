import unittest
import random

from battle import BattleEvent, BattleEventType, Battle, Battler, StatBlock

class TestBattle(unittest.TestCase):

    def test_statblock_default(self):
        b = StatBlock()
        self.assertEqual(b.health, 0)
        self.assertEqual(b.damage, 0)
    
    def test_statblock(self):
        b = StatBlock(health=1, damage=1)
        self.assertEqual(b.health, 1)
        self.assertEqual(b.damage, 1)
    
    def test_statblock_clone(self):
        a = StatBlock()
        b = a.clone()

        self.assertEqual(a, b)
        self.assertNotEqual(id(a), id(b))
        self.assertEqual(b.health, a.health)
        self.assertEqual(b.damage, b.health)
    
    def test_statblock_addition(self):
        a = StatBlock(health=1, damage=1)
        b = StatBlock(health=1, damage=1)
        c = a + b
        self.assertEqual(c.health, 2)
        self.assertEqual(c.damage, 2)

    def test_statblock_subtraction(self):
        a = StatBlock(health=1, damage=1)
        b = StatBlock(health=1, damage=1)
        c = a - b
        self.assertEqual(c.health, 0)
        self.assertEqual(c.damage, 0)

    def test_battler_creation(self):
        Battler("A", 1, 1)
    
    def test_battler_attack(self):
        a = Battler("A", 1, 1)
        b = Battler("B", 1, 1)
        act = a.attack([a], [b])
        self.assertIsInstance(act, BattleEvent)
        self.assertEqual(act.type, BattleEventType.ATTACK)
        self.assertEqual(act.battler, a)
        self.assertEqual(act.target, b)
        self.assertEqual(b.stats.health, 0)
    
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
        self.assertEqual(battle.teams[0], team1)
        self.assertEqual(battle.teams[1], team2)
        self.assertEqual(len(battle.teams[0]), len(team1))
        self.assertEqual(len(battle.teams[1]), len(team2))
        self.assertEqual(len(battle.turn_order), 2)
    
    def test_battle_next(self):
        a = Battler("A", 1, 1)
        b = Battler("B", 1, 1)
        team1  = [a]
        team2  = [b]
        battle = Battle(team1, team2)
        self.assertEqual(len(battle.turn_order), 2, f"Battle turn order should contain all battlers (2), but contains {len(battle.turn_order)} instead.")
        turn_num, act = battle.next()
        self.assertEqual(turn_num, battle.current_turn)
        self.assertEqual(turn_num, 1)
        self.assertIsInstance(act, BattleEvent)
        self.assertEqual(act.battler, a, f"Battler '{a}' was expected to the first since team1 should be going first, but found {act.battler} instead")
        self.assertEqual(act.target, b, f"Battler '{b}' is expected to be the target since it is alone on team 2, but found '{act.target}' instead")
        self.assertEqual(b.stats.health, 0, f"Since '{a}' does 1 damage and '{b}' has 1 health, '{b}' should be reduced to 0 health")
        self.assertEqual(len(team2), 0, f"Since '{b}' was reduced to 0 health, '{b}' should have been removed from team 2 (which should be empty).")
        self.assertEqual(len(battle.turn_order), 1, f"Since '{b}' was killed in the first turn, the turn order should only contain 1 battler ('{a}').")
    
    def test_battle_basic_battle(self):
        a = Battler("A", 1, 1)
        b = Battler("B", 2, 1)
        team1  = [a]
        team2  = [b]
        battle = Battle(team1, team2)
        turns = []
        while 1 < len(battle.turn_order):
            turns.append(battle.next())
        
        self.assertEqual(len(turns), 2)
        self.assertEqual(len(battle.turn_order), 1)
    
    def test_battle_random_1v1_battle(self):
        a = Battler("A", random.randint(1, 15), random.randint(1, 6))
        b = Battler("B", random.randint(1, 15), random.randint(1, 6))
        team1  = [a]
        team2  = [b]
        battle = Battle(team1, team2)
        turns = []

        print()
        print("Random 1v1 batle test!")
        print(f"On team 1:")
        for b in team1:
            print(f" - {b.name}: {b.stats.health} HP, {b.stats.damage} DMG")
        print(f"On team 2:")
        for b in team2:
            print(f" - {b.name}: {b.stats.health} HP, {b.stats.damage} DMG")

        while 1 < len(battle.turn_order):
            turn = battle.next()
            turns.append(turn)
            ev = turn[1]
            print(f"Turn {turn[0]}: {ev.battler.name} attacks {ev.target.name} for {ev.before.health - ev.after.health} HP ({ev.before.health} -> {ev.after.health})")
            if ev.after.health <= 0:
                print(f"{ev.target.name} was defeated!")
        
        if len(team1) == 0:
            print("Team 2 wins!")
        else:
            print("Team 1 Wins!")



if __name__ == "__main__":
    unittest.main()