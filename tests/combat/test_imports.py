import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

print("Current working directory:", os.getcwd())
print("Project root:", project_root)
print("Python path:", sys.path)

try:
    print("\nTrying to import combat.lib.actions_library...")
    from combat.lib.actions_library import ACTIONS
    print("Successfully imported ACTIONS:", list(ACTIONS.keys()))
except Exception as e:
    print("Failed to import actions_library:", str(e))
    import traceback
    traceback.print_exc()

try:
    print("\nTrying to import combat.combat_system...")
    from combat.combat_system import CombatSystem
    print("Successfully imported CombatSystem")
except Exception as e:
    print("Failed to import combat_system:", str(e))
    import traceback
    traceback.print_exc()

try:
    print("\nTrying to import combat.combatant...")
    from combat.combatant import TestCombatant
    print("Successfully imported TestCombatant")
except Exception as e:
    print("Failed to import combatant:", str(e))
    import traceback
    traceback.print_exc()

print("\nAll imports attempted")
