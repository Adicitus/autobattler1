# Empty type declarations so that the names can be used in type hints
class StatBlock: pass

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