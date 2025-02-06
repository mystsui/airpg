"""
Combat System Adapters

This package contains adapter classes that bridge existing implementations
with the new interface-based architecture.
"""

from combat.adapters.combatant_adapter import CombatantAdapter
from combat.adapters.action_resolver_adapter import ActionResolverAdapter
from combat.adapters.state_manager_adapter import StateManagerAdapter
from combat.adapters.event_dispatcher_adapter import EventDispatcherAdapter
from combat.adapters.awareness_system_adapter import AwarenessSystemAdapter

__all__ = [
    'CombatantAdapter',
    'ActionResolverAdapter',
    'StateManagerAdapter',
    'EventDispatcherAdapter',
    'AwarenessSystemAdapter'
]
