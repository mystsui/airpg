from typing import Any, Optional

class GameError(Exception):
    """Base class for all game-related errors."""
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class CombatError(GameError):
    """Base class for combat-related errors."""
    pass

class StateManagementError(CombatError):
    """Raised when there's an error managing game states."""
    pass

class CombatProcessingError(CombatError):
    """Raised when there's an error processing combat actions."""
    pass

class InvalidActionError(CombatError):
    """Raised when an invalid action is attempted."""
    def __init__(self, message: str, action_id: Optional[str] = None):
        super().__init__(message, {"action_id": action_id})

class CharacterError(GameError):
    """Base class for character-related errors."""
    pass

class InvalidStatError(CharacterError):
    """Raised when attempting to modify invalid stats."""
    def __init__(self, stat_name: str):
        super().__init__(f"Invalid stat: {stat_name}", {"stat_name": stat_name})

class SkillRequirementError(CharacterError):
    """Raised when skill requirements are not met."""
    def __init__(self, skill_name: str, missing_requirements: dict[str, int]):
        super().__init__(
            f"Requirements not met for skill: {skill_name}",
            {
                "skill_name": skill_name,
                "missing_requirements": missing_requirements
            }
        )

class ResourceError(GameError):
    """Raised when there are insufficient resources."""
    def __init__(self, resource_type: str, required: int, available: int):
        super().__init__(
            f"Insufficient {resource_type}: need {required}, have {available}",
            {
                "resource_type": resource_type,
                "required": required,
                "available": available
            }
        )

class ValidationError(GameError):
    """Raised when validation fails."""
    def __init__(self, field: str, value: Any, reason: str):
        super().__init__(
            f"Validation failed for {field}: {reason}",
            {
                "field": field,
                "value": value,
                "reason": reason
            }
        )

class ConfigurationError(GameError):
    """Raised when there's an error in configuration."""
    def __init__(self, config_key: str, reason: str):
        super().__init__(
            f"Configuration error for {config_key}: {reason}",
            {
                "config_key": config_key,
                "reason": reason
            }
        )