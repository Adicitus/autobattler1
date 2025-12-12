class Battler:
    def __init__(self, name:str, health:int, damage:int) -> None:
        self.name   = name
        self.health = health
        self.damage = damage
    
    def attack(self, allies:list, enemies:list):
        target = enemies[0]
        target.health -= self.damage
        return target


    
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
        target = battler.attack(allies=allies, enemies=enemies)

        if target.health <= 0:
            self.turn_order.remove(((team + 1) % len(self.teams), target))
            enemies.remove(target)
    
        return self.current_turn, battler, target

        