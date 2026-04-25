from collections import deque
import enum
from typing import Any, Callable, Tuple, Iterable

from emitter import Emitter
from combat.stats import BattleStats
from combat.actions import BASIC_ATTACK, Action

# Empty type declarations so that the names can be used in type hints
class Battle: pass
class Battler: pass

class BattleDoneException(Exception): pass
class BattleWonException(Exception): pass
class BattleDrawException(Exception): pass

class BattleEventType(enum.IntEnum):
    ATTACK = 0

class BattleEvent:
    def __init__(self, action_type:BattleEventType, action:Action, battler:Battler, target:Battler, before:BattleStats, after:BattleStats) -> None:
        self.type = action_type
        self.action = action
        self.battler = battler
        self.target = target
        self.before = before
        self.after  = after

class Battler(Emitter):
    def __init__(self, name:str, health:int, damage:int) -> None:
        super().__init__()
        
        self.events["act_start"] = []
        self.events["act_end"] = []

        self.name   = name
        self.stats  = BattleStats(health, damage)
    
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

class Battler(Emitter):
    def __init__(self, name:str, health:int=1, damage:int=1, reflex:int=1) -> None:
        super().__init__()
        
        self.events["act_start"] = []
        self.events["act_end"] = []

        self.name   = name
        self.stats  = BattleStats(health, damage, reflex)
    
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
        return f"Battler('{self.name}', {self.stats})"


# Used to track Battlers place in the turn order and the cost of their next turn
class Turn:
    battler:Battler
    cost_exponent:int=0

    def __init__(self, battler:Battler) -> None:
        self.battler = battler
    
    def __str__(self) -> str:
        return self.battler.__str__()

    def __repr__(self) -> str:
        return f"Turn({self.battler.__repr__()}, {self.cost_exponent})"

# Implements turn order logic.
#
# Turn order is based on the battler's reflex (stats.reflex_curent) stat:
# 1. Higher reflex_current go before lower
# 2. Each time a character is selected to act, reflex_current is reduces by 1
# 3. If the difference between the current batller b1's and the next battler b2's reflex is greater than 2,
#   b1 can take additional turns with each turn costing twice as much as the previous.
# 4. If the battler still has at least 1 reflex left, it will be returned to the back of the turn order.
#
# 
# When all battlers have 0 Reflex left, the round is over.
class TurnManager(Emitter):
    def __init__(self, battlers:Iterable[Battler]):
        super().__init__()
        self.turn   = 0
        self.round  = 0
        self.battlers   = list(map(lambda b: Turn(b), battlers))
        self.turn_queue = deque()
    
    # Ends the current round and sets up the next round:
    # - Emits "round_end" event on each battlers
    # - Resets reflex_current to reflex_base
    # - Emits "round_start" event on all battlers
    def new_round(self) -> None:

        if self.round > 0:
            self.emit("round_end", self.round)
            for b in self.battlers:
                b.battler.emit("round_end", self.round)

        self.round += 1
        for b in self.battlers:
            b.cost_exponent = 0
            b.battler.stats.reflex_current = b.battler.stats.reflex_base

        self.emit("round_start", self.round)
        for b in self.battlers:
            b.battler.emit("round_start", self.round)
        
        q = self.battlers.copy()
        q.sort(key=lambda b: b.battler.stats.reflex_current, reverse=True)
        self.turn_queue = deque(q)
        

    # Returns the next battler in the turn order, or None if all battlers are done.
    def next_battler(self) -> Battler | None:
        if len(self.turn_queue) == 0:
            if len(self.battlers) > 0:
                self.new_round()
            else:
                return None
            
        self.turn += 1
        
        # Grab the next battler:
        b1 = self.turn_queue.popleft()
        cost = pow(2, b1.cost_exponent)
        b1.battler.stats.reflex_current -= cost

        if b1.battler.stats.reflex_current > 0:
            if len(self.turn_queue) > 0:
                b2 = self.turn_queue.popleft()
                self.turn_queue.appendleft(b2)

                budget = b1.battler.stats.reflex_current - b2.battler.stats.reflex_current

                if budget > cost * 2:
                    b1.cost_exponent += 1
                    self.turn_queue.appendleft(b1)
                else:
                    b1.cost_exponent = 0
                    self.turn_queue.append(b1)
            else:
                # b1 is the last battler, so will only do consecutive turns
                b1.cost_exponent += 1
                self.turn_queue.append(b1)

        return b1.battler

    # Remove a given battler form the manager
    def remove_battler(self, b:Battler) -> None:
        t:Turn = None
        i = 0
        while i < len(self.battlers):
            if self.battlers[i].battler == b:
                t = self.battlers[i]
                break
            i += 1
        
        if t == None:
            return

        self.battlers.remove(t)
        
        # There should be at most 1 turn referencing the battler in the queue
        if t in self.turn_queue:
            self.turn_queue.remove(t)

    def __len__(self):
        return len(self.battlers)
    
    def __str__(self):
        return str(self.turn_queue)

class Battle(Emitter):
    """
    Represents a battle. Tracks current turn number, organizes turn order and facilitates combat turns.
    """
    def __init__(self, team1:list, team2:list) -> None:
        super().__init__()
        
        self.events["turn_start"] = []
        self.events["turn_end"] = []
        
        self.team1 = team1
        self.team2 = team2

        self.turn_order = TurnManager(team1 + team2)

    
    def next(self) -> Tuple[int, list[BattleEvent]]:
        """
        Attempts to execute the next turn, even if there are no teams or only one remains.

        Raises BattleDoneException if:
            - the battle is over (.is_done returns True).
        """

        if self.is_done():
            raise BattleDoneException()

        battler = self.turn_order.next_battler();

        if battler == None:
            # Turn manager is empty, battle is over
            raise BattleDoneException()
        
        print(f"{battler.name} is going {battler.stats}")

        allies  = self.team1
        enemies = self.team2
        if battler not in allies:
            allies  = self.team2
            enemies = self.team1
        
        self.emit("turn_start", battler)

        battle_events = battler.act(allies=allies, enemies=enemies)
        
        for battle_event in battle_events:
            if battle_event.target.stats.health <= 0:
                self.emit("battler_killed", battle_event)
                t = battle_event.target
                if t in self.team1:
                    self.team1.remove(t)
                else:
                    self.team2.remove(t)
                self.turn_order.remove_battler(t)
    
        
        self.emit("turn_end", battler)

        return self.turn_order.turn, battle_events
    
    def is_done(self):
        """
        Check if the battle is over, i.e. if at least one teams is empty.
        """
        return len(self.team1) == 0 or len(self.team2) == 0

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

        