from enum import Enum, auto
from typing import Dict, Final

# Combat Constants
MAX_COMBAT_ROUNDS: Final[int] = 100
MAX_COMBATANTS: Final[int] = 8
MIN_COMBAT_DISTANCE: Final[float] = 0.0
MAX_COMBAT_DISTANCE: Final[float] = 100.0

# Character Constants
MAX_LEVEL: Final[int] = 100
BASE_EXP_NEEDED: Final[int] = 1000
MAX_PARTY_SIZE: Final[int] = 4
MAX_INVENTORY_SIZE: Final[int] = 50

# Stat Constants
MIN_STAT_VALUE: Final[int] = 1
MAX_STAT_VALUE: Final[int] = 100
BASE_STAT_VALUE: Final[int] = 10

class DamageType(Enum):
    """Types of damage that can be dealt."""
    PHYSICAL = auto()
    MAGICAL = auto()
    FIRE = auto()
    ICE = auto()
    LIGHTNING = auto()
    POISON = auto()
    TRUE = auto()  # Ignores defenses

class StatusEffectType(Enum):
    """Types of status effects."""
    BUFF = auto()
    DEBUFF = auto()
    DOT = auto()  # Damage over time
    HOT = auto()  # Healing over time
    CC = auto()   # Crowd control

# Combat Timing Constants (in milliseconds)
COMBAT_TIMINGS: Final[Dict[str, int]] = {
    "ACTION_DELAY": 1000,
    "ROUND_START_DELAY": 2000,
    "ROUND_END_DELAY": 2000,
    "EFFECT_ANIMATION": 500,
    "MOVEMENT_SPEED": 100,  # Per unit of distance
}

# Resource Constants
STAMINA_REGEN_RATE: Final[float] = 0.1  # Per second
HEALTH_REGEN_RATE: Final[float] = 0.05   # Per second
MAX_RESOURCE_VALUE: Final[int] = 10000

# Combat Modifiers
COMBAT_MODIFIERS: Final[Dict[str, float]] = {
    "CRITICAL_MULTIPLIER": 1.5,
    "BLOCK_REDUCTION": 0.5,
    "DODGE_CHANCE_CAP": 0.75,
    "MINIMUM_DAMAGE": 1.0,
}

# Experience and Level Constants
LEVEL_MODIFIERS: Final[Dict[str, float]] = {
    "EXP_SCALE": 1.5,        # Experience scaling per level
    "STAT_SCALE": 1.1,       # Stat increase per level
    "SKILL_COST_SCALE": 1.2, # Skill cost increase per level
}

# File Paths
DEFAULT_PATHS: Final[Dict[str, str]] = {
    "SAVE_DIR": "saves/",
    "CONFIG_DIR": "config/",
    "LOG_DIR": "logs/",
    "ASSET_DIR": "assets/",
}

# Event Types
class GameEventType(Enum):
    """Types of game events."""
    COMBAT_START = "combat.start"
    COMBAT_END = "combat.end"
    ACTION_EXECUTED = "action.executed"
    DAMAGE_DEALT = "damage.dealt"
    STATUS_APPLIED = "status.applied"
    RESOURCE_CHANGED = "resource.changed"
    CHARACTER_LEVELUP = "character.levelup"
    SKILL_LEARNED = "skill.learned"
    ITEM_USED = "item.used"