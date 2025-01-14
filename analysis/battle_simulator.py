from dataclasses import dataclass
from typing import List, Dict
import json
from combat.combat_system import CombatSystem
from combat.combatant import Combatant

@dataclass
class BattleResult:
    winner: str
    duration: int
    damage_dealt_a: int
    damage_dealt_b: int
    actions_a: List[Dict]
    actions_b: List[Dict]
    final_distance: int

class BattleSimulator:
    def __init__(self, num_iterations=100):
        self.results: List[BattleResult] = []
        self.num_iterations = num_iterations

    def run_simulation(self):
        for _ in range(self.num_iterations):
            battle = CombatSystem(duration=10000)
            result = self._run_single_battle(battle)
            self.results.append(result)

    def _run_single_battle(self, battle) -> BattleResult:
        # Create combatants with same parameters as game_instance.py
        combatant_a = Combatant(name="A", health=100, stamina=60, attack_power=9,
                               accuracy=70, blocking_ability=2, evading_ability=1,
                               mobility=50, range=50, stamina_recovery=15)
        
        combatant_b = Combatant(name="B", health=81, stamina=80, attack_power=6,
                               accuracy=85, blocking_ability=1, evading_ability=2,
                               mobility=60, range=110, stamina_recovery=20)

        battle.add_combatant(combatant_a)
        battle.add_combatant(combatant_b)

        # Initial actions
        combatant_a.decide_action(timer=0, distance=200, opponent=combatant_b)
        combatant_b.decide_action(timer=0, distance=200, opponent=combatant_a)
        battle.determine_next_event()

        # Run battle
        while not battle.is_battle_over():
            battle.update()

        return BattleResult(
            winner="A" if combatant_a.health > combatant_b.health else "B",
            duration=battle.timer,
            damage_dealt_a=81 - combatant_b.health,
            damage_dealt_b=100 - combatant_a.health,
            actions_a=battle.events.get_actions("A"),
            actions_b=battle.events.get_actions("B"),
            final_distance=battle.distance
        )

    def analyze_results(self) -> Dict:
        wins_a = sum(1 for r in self.results if r.winner == "A")
        avg_duration = sum(r.duration for r in self.results) / len(self.results)
        
        return {
            "win_rate_a": wins_a / self.num_iterations,
            "avg_duration": avg_duration,
            "avg_damage_a": sum(r.damage_dealt_a for r in self.results) / len(self.results),
            "avg_damage_b": sum(r.damage_dealt_b for r in self.results) / len(self.results),
        }