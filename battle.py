import enum

class StatBlock(dict):
    def __init__(self, health:int=0, damage:int=0) -> None:
        self.health = health
        self.damage = damage
    
    def __add__(self, other):
        copy = self.clone()
        copy.health += other.health
        copy.damage += other.damage
        return copy
    
    def __sub__(self, other):
        copy = self.clone()
        copy.health -= other.health
        copy.damage -= other.damage
        return copy
    
    def __eq__(self, other):
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

class Battler:
    def __init__(self, name:str, health:int, damage:int) -> None:
        self.name   = name
        self.stats  = StatBlock(health, damage)
    
    def attack(self, allies:list, enemies:list):
        target = enemies[0]
        before = target.stats.clone()
        target.stats = BASIC_ATTACK.perform(self.stats, target.stats)
        after = target.stats.clone()
        return BattleEvent(BattleEventType.ATTACK, BASIC_ATTACK, self, target, before, after)
        
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


    
class Battle:
    def __init__(self, team1:list, team2:list) -> None:
        self.teams = [
            team1,
            team2
        ]
        self.turn_order = []
        for team_num in range(0, len(self.teams)):
            team = self.teams[team_num]
            for battler in team:
                self.turn_order.append((team_num, battler))
        self.current_turn = 0

    
    def next(self):
        turn_num = self.current_turn
        self.current_turn = turn_num + 1

        battler_record = self.turn_order[turn_num % len(self.turn_order)]
        team = battler_record[0]
        battler = battler_record[1]
        allies  = self.teams[team]
        enemies = self.teams[(team + 1) % len(self.teams)]
        action = battler.attack(allies=allies, enemies=enemies)

        if action.target.stats.health <= 0:
            self.turn_order.remove(((team + 1) % len(self.teams), action.target))
            enemies.remove(action.target)
    
        return self.current_turn, action

        