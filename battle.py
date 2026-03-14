from collections import deque
import enum
from typing import Any, Callable, Tuple
from emitter import Emitter

# Empty type declarations so that the names can be used in type hints
class StatBlock: pass
class Action: pass
class BasicAttack: pass
class Battler: pass
class BattleEventType: pass
class BattleEvent: pass
class Battle: pass

class BattleDoneException(Exception): pass
class BattleWonException(Exception): pass
class BattleDrawException(Exception): pass

class StatBlock(dict):
    def __init__(self, health:int=0, damage:int=0) -> None:
        self.health = health
        self.damage = damage
    
    def __add__(self, other) -> StatBlock:
        copy = self.clone()
        copy.health += other.health
        copy.damage += other.damage
        return copy
    
    def __sub__(self, other) -> StatBlock:
        copy = self.clone()
        copy.health -= other.health
        copy.damage -= other.damage
        return copy
    
    def __eq__(self, other) -> bool:
        return self.health == other.health and self.damage == other.damage

    def clone(self):
        return StatBlock(self.health, self.damage)

# Base class for actions used by battlers.
class Action:
    def __init__(self, name:str) -> None:
        self.name = name

    # Base method used to execute this action, simply returns a copy of the
    # target StatBlock that should be manipulated by implemented child classes.
    def perform(self, user:StatBlock, target:StatBlock) -> StatBlock:
        return target.clone()

# Basic attack action, just reduces the target's health by the user's damage.
class BasicAttack(Action):
    def __init__(self) -> None:
        super().__init__("basic attack")
    
    def perform(self, user:StatBlock, target:StatBlock) -> StatBlock:
        new_target = super().perform(user, target)
        new_target.health -= user.damage
        return new_target

BASIC_ATTACK = BasicAttack()

class Battler(Emitter):
    def __init__(self, name:str, health:int, damage:int) -> None:
        super().__init__()
        
        self.events["act_start"] = []
        self.events["act_end"] = []

        self.name   = name
        self.stats  = StatBlock(health, damage)
    
    def act(self, allies:list, enemies:list) -> list[BattleEvent]:
        self.emit("act_start")
        target = enemies[0]
        before = target.stats.clone()
        target.stats = BASIC_ATTACK.perform(self.stats, target.stats)
        after = target.stats.clone()
        self.emit("act_end")
        return [BattleEvent(BattleEventType.ATTACK, BASIC_ATTACK, self, target, before, after)]
        

    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"Battler('{self.name}', {self.stats.health}, {self.stats.damage})"
        
class BattleEventType(enum.IntEnum):
    ATTACK = 0

class BattleEvent:
    def __init__(self, action_type:BattleEventType, action:Action, battler:Battler, target:Battler, before:StatBlock, after:StatBlock) -> None:
        self.type = action_type
        self.action = action
        self.battler = battler
        self.target = target
        self.before = before
        self.after  = after


    
class Battle(Emitter):
    """
    Represents a battle. Tracks current turn number, organizes turn order and facilitates combat turns.
    """
    def __init__(self, team1:list, team2:list) -> None:
        super().__init__()
        
        self.events["turn_start"] = []
        self.events["turn_end"] = []
        
        self.teams = [
            team1,
            team2
        ]
        self.turn_order = deque()
        for team_num in range(0, len(self.teams)):
            team = self.teams[team_num]
            for battler in team:
                self.turn_order.append((team_num, battler))
        self.current_turn = 0

    
    def next(self) -> Tuple[int, list[BattleEvent]]:
        """
        Attempts to execute the next turn, even if there are no teams or only one remains.

        Raises BattleDoneException if:
            - the battle is over (.is_done returns True).
        """

        if self.is_done():
            raise BattleDoneException()

        self.current_turn += 1

        battler_record = self.turn_order.popleft()
        
        print(f"{battler_record[1].name} is going ({battler_record[1].stats.health}hp)")

        team = battler_record[0]
        battler = battler_record[1]
        allies  = self.teams[team]
        enemies = self.teams[(team + 1) % len(self.teams)]
        
        self.emit("turn_start", battler)

        battle_events = battler.act(allies=allies, enemies=enemies)

        if 0 < battler.stats.health:
            self.turn_order.append(battler_record)
        
        for battle_event in battle_events:
            if battle_event.target.stats.health <= 0:
                t = battle_event.target
                enemies.remove(t)
                self.turn_order = deque(filter(lambda r: r[1] != t, self.turn_order))
    
        
        self.emit("turn_end", battler)

        return self.current_turn, battle_events
    
    def is_done(self):
        """
        Check if the battle is over, i.e. if at least one teams is empty.
        """
        return len(self.teams[0]) == 0 or len(self.teams[1]) == 0

    def __iter__(self) -> Battle:
        """
        Returns the Battle object, implemented to satisfy Iterable behavior.
        """
        return self

    def __next__(self) -> Tuple[int, list[BattleEvent]]:
        """
        Performs next turn and returns the turn number and resulting BattleEvent(s), or raises StopIteration if the battle is over.
        """
        if self.is_done(): raise StopIteration
        
        return self.next()
    
    def resolve(self) -> list[Tuple[int, list[BattleEvent]]]:
        """
        Resolves the Battle by iterating through the turns until one team is defated.
        """
        turns = []
        for r in self: turns.append(r)
        return turns

        