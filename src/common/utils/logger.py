import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from logging.handlers import RotatingFileHandler

class GameLogger:
    """Custom logger for the game with both file and console output."""
    
    def __init__(
        self,
        name: str = "game",
        log_dir: Optional[Path] = None,
        level: int = logging.INFO
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Create log directory if it doesn't exist
        self.log_dir = log_dir or Path("logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Add handlers
        self._add_console_handler()
        self._add_file_handler()
        
        self.logger.info("Logger initialized")

    def _add_console_handler(self) -> None:
        """Add console output handler with colored formatting."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Create colored formatter
        console_format = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)

    def _add_file_handler(self) -> None:
        """Add rotating file handler."""
        log_file = self.log_dir / f"game_{datetime.now():%Y%m%d}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10_000_000,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Create detailed formatter for file
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(message, extra=kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self.logger.error(message, exc_info=True, extra=kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self.logger.critical(message, exc_info=True, extra=kwargs)

class CombatLogger(GameLogger):
    """Specialized logger for combat events."""
    
    def __init__(self):
        super().__init__(name="combat", level=logging.DEBUG)
        self.combat_id: Optional[str] = None

    def set_combat_id(self, combat_id: str) -> None:
        """Set the current combat ID for context."""
        self.combat_id = combat_id
        self.info(f"Started logging for combat {combat_id}")

    def log_action(self, action_id: str, actor_id: str, target_id: Optional[str], result: dict) -> None:
        """Log a combat action."""
        self.debug(
            f"Action executed: {action_id}",
            combat_id=self.combat_id,
            actor_id=actor_id,
            target_id=target_id,
            result=result
        )

    def log_damage(self, source_id: str, target_id: str, amount: int, damage_type: str) -> None:
        """Log damage dealt."""
        self.info(
            f"{source_id} dealt {amount} {damage_type} damage to {target_id}",
            combat_id=self.combat_id
        )

    def log_status_effect(self, target_id: str, effect_name: str, duration: int) -> None:
        """Log status effect application."""
        self.info(
            f"{target_id} affected by {effect_name} for {duration} rounds",
            combat_id=self.combat_id
        )

# Create global logger instance
game_logger = GameLogger()
combat_logger = CombatLogger()

def get_logger(name: str = "game") -> GameLogger:
    """Get or create a logger instance."""
    if name == "combat":
        return combat_logger
    return game_logger