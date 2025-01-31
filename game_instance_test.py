import unittest
from combat.combat_system import CombatSystem
from combat.combatant import Combatant
from combat.lib.actions_library import ACTIONS

class TestCombatant(Combatant):
    """Test-specific combatant that allows direct action control"""
    def force_action(self, action_type, timer, target=None):
        """Override normal decision making to force a specific action"""
        self.action = self.create_action(action_type, timer, target)
        self.deduct_stamina(action_type)
        return self.action

class TestGameMechanics(unittest.TestCase):
    def setUp(self):
        """Setup basic battle scenario for each test"""
        self.battle = CombatSystem(duration=10000, distance=100)
        self.combatant_a = TestCombatant(
            name="A",
            health=100,
            stamina=100,
            attack_power=10,
            accuracy=100,
            blocking_power=5,
            evading_ability=10,
            mobility=50,
            range_a=0,
            range_b=150,
            position="left",
            facing="right",
            perception=0,
            stealth=0,
            stamina_recovery=10
        )
        self.combatant_b = TestCombatant(
            name="B", 
            health=100,
            stamina=100,
            attack_power=10,
            accuracy=100, 
            blocking_power=5,
            evading_ability=10,
            mobility=50,
            range_a=0,
            range_b=150,
            position="right",
            facing="left",
            perception=0,
            stealth=0,
            stamina_recovery=10
        )
        self.battle.add_combatant(self.combatant_a)
        self.battle.add_combatant(self.combatant_b)
        self.battle.get_opponent_data(self.combatant_a, self.combatant_b)
        self.battle.get_opponent_data(self.combatant_b, self.combatant_a)

    def test_basic_movement(self):
        """Test basic movement mechanics"""
        initial_distance = self.battle.distance
        
        # Force move forward action
        self.combatant_a.force_action("move_forward", 0)
        self.battle.determine_next_event()
        self.battle.update()
        
        # Check distance reduced by mobility
        self.assertEqual(self.battle.distance, initial_distance - self.combatant_a.mobility)

    # def test_attack_sequence(self):
    #     """Test basic attack sequence"""
    #     initial_health = self.combatant_b.health
        
    #     # Position within range
    #     self.battle.distance = 50
        
    #     # Force attack sequence
    #     self.combatant_a.force_action("try_attack", 0, self.combatant_b)
    #     self.battle.determine_next_event()
    #     self.battle.update()
        
    #     self.combatant_a.force_action("release_attack", self.battle.timer, self.combatant_b)
    #     self.battle.determine_next_event()
    #     self.battle.update()
        
    #     # Check damage dealt
    #     self.assertLess(self.combatant_b.health, initial_health)

    # def test_blocking_mechanics(self):
    #     """Test blocking mechanics"""
    #     initial_health = self.combatant_b.health
    #     self.battle.distance = 50

    #     # Start blocking
    #     self.combatant_b.force_action("try_block", 0)
    #     self.battle.determine_next_event()
    #     self.battle.update()
        
    #     # Attack while opponent is blocking
    #     self.combatant_a.force_action("try_attack", self.battle.timer, self.combatant_b)
    #     self.battle.determine_next_event()
    #     self.battle.update()
        
    #     self.combatant_a.force_action("release_attack", self.battle.timer, self.combatant_b)
    #     self.battle.determine_next_event()
    #     self.battle.update()
        
    #     # Health should be unchanged due to blocking
    #     self.assertEqual(self.combatant_b.health, initial_health)

    # def test_stamina_consumption(self):
    #     """Test stamina mechanics"""
    #     initial_stamina = self.combatant_a.stamina
    #     action_type = "try_attack"
    #     stamina_cost = ACTIONS[action_type]["stamina_cost"]
        
    #     self.combatant_a.force_action(action_type, 0)
    #     self.battle.determine_next_event()
    #     self.battle.update()
        
    #     self.assertEqual(self.combatant_a.stamina, initial_stamina - stamina_cost)

    # def test_battle_duration(self):
    #     """Test battle duration limit"""
    #     self.battle.duration = 100
        
    #     while not self.battle.is_battle_over():
    #         self.combatant_a.force_action("idle", self.battle.timer)
    #         self.combatant_b.force_action("idle", self.battle.timer)
    #         self.battle.determine_next_event()
    #         self.battle.update()
            
    #     self.assertGreaterEqual(self.battle.timer, self.battle.duration)

    # def test_defeat_condition(self):
    #     """Test battle ends when combatant is defeated"""
    #     self.combatant_b.health = 1
    #     self.battle.distance = 50
        
    #     # Force fatal attack
    #     self.combatant_a.force_action("try_attack", 0, self.combatant_b)
    #     self.battle.determine_next_event()
    #     self.battle.update()
        
    #     self.combatant_a.force_action("release_attack", self.battle.timer, self.combatant_b)
    #     self.battle.determine_next_event()
    #     self.battle.update()
        
    #     self.assertTrue(self.battle.is_battle_over())
    #     self.assertTrue(self.combatant_b.is_defeated())

if __name__ == '__main__':
    unittest.main()