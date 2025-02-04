"""
Combat System Adapters

This package contains adapter classes that bridge existing implementations
with the new interface-based architecture.
"""

from combat.adapters.combatant_adapter import CombatantAdapter
from combat.adapters.action_resolver_adapter import ActionResolverAdapter
from combat.adapters.state_manager_adapter import StateManagerAdapter

__all__ = [
    'CombatantAdapter',
    'ActionResolverAdapter',
    'StateManagerAdapter'
]
