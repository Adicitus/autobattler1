# Base class for actions used by battlers.
from combat.stats import BattleStats

class Action:
    def __init__(self, name:str) -> None:
        self.name = name

    # Base method used to execute this action, simply returns a copy of the
    # target StatBlock that should be manipulated by implemented child classes.
    def perform(self, user:BattleStats, target:BattleStats) -> BattleStats:
        return target.clone()

# Basic attack action, just reduces the target's health by the user's damage.
class BasicAttack(Action):
    def __init__(self) -> None:
        super().__init__("basic attack")
    
    def perform(self, user:BattleStats, target:BattleStats) -> BattleStats:
        new_target = super().perform(user, target)
        new_target.health -= user.damage
        return new_target

BASIC_ATTACK = BasicAttack()