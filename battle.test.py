import unittest
import random


from combat.stats import BattleStats
from combat.actions import BASIC_ATTACK, Action
from combat.battle import BattleEvent, BattleEventType, Battle, Battler, TurnManager

class TestTurnManager(unittest.TestCase):
    def test_creation_empty(self):
        tm = TurnManager([])
        self.assertIsInstance(tm, TurnManager)
    
    def test_len_empty(self):
        tm = TurnManager([])
        self.assertEqual(len(tm), 0)
    
    def test_creation(self):
        battlers = [Battler('A', 1, 1), Battler('B', 1, 1)]
        tm = TurnManager(battlers)
        self.assertIsInstance(tm, TurnManager)
        self.assertEqual(len(tm), len(battlers))
        self.assertListEqual(tm.battlers, battlers)
    
    def test_next_battler_on_empty(self):
        tm = TurnManager([])
        self.assertIsNone(tm.next_battler())
    
    def test_next_battler(self):
        battlers = [Battler('A', 1, 1)]
        tm = TurnManager(battlers)
        self.assertEqual(tm.next_battler(), battlers[0])
    
    def test_new_round(self):
        flags = {
            'round_start': False,
            'round_end': False
        }
        b = Battler('A')
        b.on('round_start', lambda *_: flags.__setitem__('round_start', True))
        b.on('round_end', lambda *_: flags.__setitem__('round_end', True))
        tm = TurnManager([b])

        self.assertEqual(tm.next_battler(), b)
        self.assertEqual(b.stats.reflex_current, 0)
        self.assertTrue(flags['round_start'])
        self.assertFalse(flags['round_end'])
        self.assertEqual(tm.round, 1)
        tm.new_round()
        self.assertEqual(tm.round, 2)
        self.assertEqual(b.stats.reflex_current, b.stats.reflex_base)
        self.assertTrue(flags['round_start'])
        self.assertTrue(flags['round_end'])

    def test_next_battler_order(self):
        battlers = [Battler('Faster', reflex=2), Battler('Slower', reflex=1)]
        tm = TurnManager(battlers)
        self.assertEqual(tm.next_battler(), battlers[0])
        self.assertEqual(battlers[0].stats.reflex_current, 1)
        self.assertEqual(tm.turn, 1)
        self.assertEqual(tm.next_battler(), battlers[1])
        self.assertEqual(battlers[1].stats.reflex_current, 0)
        self.assertEqual(tm.turn, 2)
        self.assertEqual(tm.next_battler(), battlers[0])
        self.assertEqual(battlers[0].stats.reflex_current, 0)
        self.assertEqual(tm.turn, 3)
    
    def test_next_battler_new_round_trigger(self):
        battlers = [Battler('Faster', reflex=2), Battler('Slower', reflex=1)]
        tm = TurnManager(battlers)
        self.assertEqual(tm.round, 1)
        self.assertEqual(tm.next_battler(), battlers[0])
        self.assertEqual(tm.next_battler(), battlers[1])
        self.assertEqual(tm.next_battler(), battlers[0])
        self.assertEqual(tm.round, 1)
        self.assertEqual(tm.next_battler(), battlers[0])
        self.assertEqual(tm.round, 2)
        self.assertEqual(battlers[0].stats.reflex_current, 1)
        self.assertEqual(battlers[1].stats.reflex_current, 1)
    
    def test_next_battler_reorder(self):
        battlers = [Battler('Faster', reflex=2), Battler('Slower', reflex=1)]
        tm = TurnManager(battlers)
        self.assertEqual(tm.round, 1)
        self.assertEqual(tm.next_battler(), battlers[0]) # 1 Reflex left
        self.assertEqual(tm.next_battler(), battlers[1]) # 0 Reflex left
        self.assertEqual(tm.next_battler(), battlers[0]) # 0 Reflex left
        # Make Slower quicker
        battlers[1].stats.reflex_base = 3;
        self.assertEqual(tm.next_battler(), battlers[1]) # 2 Reflex left
        self.assertEqual(tm.round, 2)
        self.assertEqual(tm.next_battler(), battlers[0]) # 1 Reflex left
        self.assertEqual(tm.next_battler(), battlers[1]) # 1 Reflex left
        self.assertEqual(tm.next_battler(), battlers[0]) # 0 Reflex left
        self.assertEqual(tm.next_battler(), battlers[1]) # 0 Reflex left
        self.assertEqual(tm.next_battler(), battlers[1]) # New round, 2 Reflex left
        self.assertEqual(tm.round, 3)
        
    def test_next_battler_consecutive_turns(self):
        battlers = [Battler('Faster', reflex=8), Battler('Slower', reflex=1)]
        tm = TurnManager(battlers)
        self.assertEqual(tm.next_battler(), battlers[0]) # 1, costs 1
        self.assertEqual(tm.next_battler(), battlers[0]) # 2, costs 2
        self.assertEqual(tm.next_battler(), battlers[0]) # 3, costs 4
        



class TestBattle(unittest.TestCase):

    def test_statblock_default(self):
        b = BattleStats()
        self.assertEqual(b.health, 0)
        self.assertEqual(b.damage, 0)
    
    def test_statblock(self):
        b = BattleStats(health=1, damage=1)
        self.assertEqual(b.health, 1)
        self.assertEqual(b.damage, 1)
    
    def test_statblock_clone(self):
        a = BattleStats()
        b = a.clone()

        self.assertEqual(a, b)
        self.assertNotEqual(id(a), id(b))
        self.assertEqual(b.health, a.health)
        self.assertEqual(b.damage, b.health)
    
    def test_statblock_addition(self):
        a = BattleStats(health=1, damage=1)
        b = BattleStats(health=1, damage=1)
        c = a + b
        self.assertEqual(c.health, 2)
        self.assertEqual(c.damage, 2)

    def test_statblock_subtraction(self):
        a = BattleStats(health=1, damage=1)
        b = BattleStats(health=1, damage=1)
        c = a - b
        self.assertEqual(c.health, 0)
        self.assertEqual(c.damage, 0)

    def test_battler_creation(self):
        Battler("A", 1, 1)
    
    def test_battler_attack(self):
        a = Battler("A", 1, 1)
        b = Battler("B", 1, 1)
        events = a.act([a], [b])
        act = events[0]
        self.assertIsInstance(act, BattleEvent)
        self.assertEqual(act.type, BattleEventType.ATTACK)
        self.assertEqual(act.battler, a)
        self.assertEqual(act.target, b)
        self.assertEqual(b.stats.health, 0)
    
    def test_battle_creation_both_empty(self):
        battle = Battle([], [])
        self.assertEqual(battle.team1, [])
        self.assertEqual(battle.team2, [])
        self.assertEqual(len(battle.turn_order), 0)
    
    def test_battle_creation_one_empty(self):
        team1  = [Battler("A", 1, 1)]
        team2  = []
        battle = Battle(team1, team2)
        self.assertEqual(len(battle.team1), 1)
        self.assertEqual(len(battle.team2), 0)
        self.assertEqual(battle.team1, team1)
        self.assertEqual(battle.team2, team2)
        self.assertEqual(len(battle.turn_order), 1)
    
    def test_battle_creation(self):
        team1  = [Battler("A", 1, 1)]
        team2  = [Battler("B", 1, 1)]
        battle = Battle(team1, team2)
        self.assertEqual(battle.team1, team1)
        self.assertEqual(battle.team2, team2)
        self.assertEqual(len(battle.team1), len(team1))
        self.assertEqual(len(battle.team2), len(team2))
        self.assertEqual(len(battle.turn_order), 2)
    
    def test_battle_is_done(self):
        battle = Battle([], [])
        self.assertTrue(battle.is_done(), "If both teams are empty, then the battle is over.")

        
        team1  = [Battler("A", 1, 1)]
        team2  = []
        battle = Battle(team1, team2)
        self.assertTrue(battle.is_done(), "If one team is empty and the other isn't, then the battle is over and the team with members won.")
        
        team1  = []
        team2  = [Battler("B", 1, 1)]
        battle = Battle(team1, team2)
        self.assertTrue(battle.is_done(), "If one team is empty and the other isn't, then the battle is over and the team with members won.")
        
        team1  = [Battler("A", 1, 1)]
        team2  = [Battler("B", 1, 1)]
        battle = Battle(team1, team2)
        self.assertFalse(battle.is_done(), "If both teams have battlers still on them, then the battle isn't over.")
    
    def test_battle_next(self):
        a = Battler("A", 1, 1)
        b = Battler("B", 1, 1)
        team1  = [a]
        team2  = [b]
        battle = Battle(team1, team2)
        self.assertEqual(len(battle.turn_order), 2, f"Battle turn order should contain all battlers (2), but contains {len(battle.turn_order)} instead.")
        turn_num, events = battle.next()
        self.assertIsInstance(events[0].action, Action, "The action performed in the event should be an Action object.")
        self.assertEqual(events[0].action, BASIC_ATTACK, "By default the battlers should only be able to use the BASIC_ATTACK action")
        self.assertEqual(turn_num, battle.turn_order.turn)
        self.assertEqual(turn_num, 1)
        self.assertIsInstance(events[0], BattleEvent)
        self.assertEqual(events[0].battler, a, f"Battler '{a}' was expected to the first since team1 should be going first, but found {events[0].battler} instead")
        self.assertEqual(events[0].target, b, f"Battler '{b}' is expected to be the target since it is alone on team 2, but found '{events[0].target}' instead")
        self.assertEqual(b.stats.health, 0, f"Since '{a}' does 1 damage and '{b}' has 1 health, '{b}' should be reduced to 0 health")
        self.assertEqual(len(team2), 0, f"Since '{b}' was reduced to 0 health, '{b}' should have been removed from team 2 (which should be empty).")
        self.assertEqual(len(battle.turn_order), 1, f"Since '{b}' was killed in the first turn, the turn order should only contain 1 battler ('{a}').")
    
    def test_battle_basic_battle_manual(self):
        a = Battler("A", 1, 1)
        b = Battler("B", 2, 1)
        team1  = [a]
        team2  = [b]
        battle = Battle(team1, team2)
        turns = []
        while 1 < len(battle.turn_order): turns.append(battle.next())
        
        self.assertEqual(len(turns), 2)
        self.assertEqual(len(battle.turn_order), 1)
    
    def test_battle_basic_battle_iterable(self):
        team1  = [Battler("A", 1, 1)]
        team2  = [Battler("B", 2, 1)]
        battle = Battle(team1, team2)
        turns = []
        for r in battle: turns.append(r)
        
        self.assertEqual(len(turns), 2)
        self.assertEqual(len(battle.turn_order), 1)
    
    def test_battle_basic_battle_resolve(self):
        team1  = [Battler("A", 1, 1)]
        team2  = [Battler("B", 2, 1)]
        battle = Battle(team1, team2)
        turns = battle.resolve()
        
        self.assertEqual(len(turns), 2)
        self.assertEqual(len(battle.turn_order), 1)
    
    def test_battle_random_1v1_battle(self):
        a = Battler("A", random.randint(5, 15), random.randint(1, 6), random.randint(1, 6))
        b = Battler("B", random.randint(5, 15), random.randint(1, 6), random.randint(1, 6))
        team1  = [a]
        team2  = [b]
        battle = Battle(team1, team2)
        turns = []

        print()
        print("Random 1v1 battle test!")
        print(f"On team 1:")
        for b in team1:
            print(f" - {b.name}: {b.stats}")
        print(f"On team 2:")
        for b in team2:
            print(f" - {b.name}: {b.stats}")

        while 1 < len(battle.turn_order):
            turn = battle.next()
            turns.append(turn)
            ev = turn[1][0]
            print(f"Turn {turn[0]}: {ev.battler.name} attacks {ev.target.name} for {ev.before.health - ev.after.health} HP ({ev.before.health} -> {ev.after.health})")
            if ev.after.health <= 0:
                print(f"{ev.target.name} was defeated!")
        
        if len(team1) == 0:
            print("Team 2 wins!")
        else:
            print("Team 1 Wins!")



if __name__ == "__main__":
    unittest.main()