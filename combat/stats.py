# Empty type declarations so that the names can be used in type hints
class BattleStats: pass

class BattleStats(dict):
    def __init__(self, health:int=0, damage:int=0, reflex:int=1) -> None:
        self.max_health = health
        self.health = health
        self.damage = damage

        self.reflex_base  = reflex
        self.reflex_current = reflex
    
    def __add__(self, other) -> BattleStats:
        copy = self.clone()
        copy.health += other.health
        copy.damage += other.damage
        return copy
    
    def __sub__(self, other) -> BattleStats:
        copy = self.clone()
        copy.health -= other.health
        copy.damage -= other.damage
        return copy
    
    def __eq__(self, other) -> bool:
        return self.health == other.health and self.damage == other.damage

    def __str__(self):
        return f"HP: {self.health}/{self.max_health}, DMG: {self.damage}, Reflex: {self.reflex_current}/{self.reflex_base}"

    def clone(self):
        s = BattleStats(self.health, self.damage, self.reflex_base)
        s.reflex_current = self.reflex_current
        return s