from typing import Any, Callable, Dict, List, Optional, Type, Union
from ..errors import ValidationError

class Validator:
    """Base validator class."""
    
    def __init__(self, field_name: str):
        self.field_name = field_name

    def validate(self, value: Any) -> None:
        """Validate a value."""
        raise NotImplementedError

class TypeValidator(Validator):
    """Validates value type."""
    
    def __init__(self, field_name: str, expected_type: Union[Type, tuple[Type, ...]]):
        super().__init__(field_name)
        self.expected_type = expected_type

    def validate(self, value: Any) -> None:
        if not isinstance(value, self.expected_type):
            raise ValidationError(
                self.field_name,
                value,
                f"Expected type {self.expected_type.__name__}, got {type(value).__name__}"
            )

class RangeValidator(Validator):
    """Validates numeric range."""
    
    def __init__(self, field_name: str, min_value: Optional[float] = None, max_value: Optional[float] = None):
        super().__init__(field_name)
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value: Union[int, float]) -> None:
        if self.min_value is not None and value < self.min_value:
            raise ValidationError(
                self.field_name,
                value,
                f"Value must be greater than or equal to {self.min_value}"
            )
        if self.max_value is not None and value > self.max_value:
            raise ValidationError(
                self.field_name,
                value,
                f"Value must be less than or equal to {self.max_value}"
            )

class LengthValidator(Validator):
    """Validates string or collection length."""
    
    def __init__(self, field_name: str, min_length: Optional[int] = None, max_length: Optional[int] = None):
        super().__init__(field_name)
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value: Union[str, List, Dict]) -> None:
        length = len(value)
        if self.min_length is not None and length < self.min_length:
            raise ValidationError(
                self.field_name,
                value,
                f"Length must be at least {self.min_length}"
            )
        if self.max_length is not None and length > self.max_length:
            raise ValidationError(
                self.field_name,
                value,
                f"Length must be at most {self.max_length}"
            )

class PatternValidator(Validator):
    """Validates string pattern."""
    
    def __init__(self, field_name: str, pattern: str):
        super().__init__(field_name)
        import re
        self.pattern = re.compile(pattern)

    def validate(self, value: str) -> None:
        if not self.pattern.match(value):
            raise ValidationError(
                self.field_name,
                value,
                f"Value must match pattern {self.pattern.pattern}"
            )

class CustomValidator(Validator):
    """Custom validation using a callback function."""
    
    def __init__(self, field_name: str, validation_func: Callable[[Any], bool], error_message: str):
        super().__init__(field_name)
        self.validation_func = validation_func
        self.error_message = error_message

    def validate(self, value: Any) -> None:
        if not self.validation_func(value):
            raise ValidationError(
                self.field_name,
                value,
                self.error_message
            )

class ValidationChain:
    """Chain multiple validators together."""
    
    def __init__(self):
        self.validators: List[Validator] = []

    def add_validator(self, validator: Validator) -> 'ValidationChain':
        """Add a validator to the chain."""
        self.validators.append(validator)
        return self

    def validate(self, value: Any) -> None:
        """Run all validators in the chain."""
        for validator in self.validators:
            validator.validate(value)

# Common validation functions
def validate_name(name: str) -> None:
    """Validate character/item name."""
    chain = ValidationChain()
    chain.add_validator(TypeValidator("name", str))
    chain.add_validator(LengthValidator("name", 2, 32))
    chain.add_validator(PatternValidator("name", r'^[a-zA-Z0-9 _-]+$'))
    chain.validate(name)

def validate_stats(stats: Dict[str, int]) -> None:
    """Validate character stats."""
    chain = ValidationChain()
    chain.add_validator(TypeValidator("stats", dict))
    chain.add_validator(CustomValidator(
        "stats",
        lambda s: all(isinstance(v, int) for v in s.values()),
        "All stat values must be integers"
    ))
    chain.add_validator(CustomValidator(
        "stats",
        lambda s: all(1 <= v <= 100 for v in s.values()),
        "Stat values must be between 1 and 100"
    ))
    chain.validate(stats)

def validate_combat_distance(distance: float) -> None:
    """Validate combat distance."""
    chain = ValidationChain()
    chain.add_validator(TypeValidator("distance", (int, float)))
    chain.add_validator(RangeValidator("distance", 0.0, 100.0))
    chain.validate(distance)