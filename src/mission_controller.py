from dataclasses import dataclass
from typing import Tuple, Optional
import numpy as np
import time
import ast

from src.grid_manager import GridManager
from src.navigator import Navigator


@dataclass
class MissionConfig:
    max_steps: int = 30
    retry_delay: int = 5
    max_attempts: int = 20
    position_bounds: Tuple[float, float] = (-0.5, 0.5)


class MissionController:
    def __init__(self, grid_manager: GridManager, navigator: Navigator, config: MissionConfig):
        self.grid_manager = grid_manager
        self.navigator = navigator
        self.config = config
        self.current_position = None
        self.waypoints = []
        self.position_history = []

    def initialize_position(self) -> np.ndarray:
        """Initialize random starting position."""
        return np.round(np.random.uniform(self.config.position_bounds[0], self.config.position_bounds[1], size=(2)), 1)

    def execute_mission(self, model) -> str:
        """Execute complete navigation mission."""
        for attempt in range(self.config.max_attempts):
            self.current_position = self.initialize_position() if attempt != 0 else self.current_position
            self.position_history = []

            prompt = f"Start. you are at ({self.current_position[0]}, {self.current_position[1]})"
            response = model.send_message([prompt])
            self.waypoints = ast.literal_eval(response.candidates[0].content.parts[0].text)

            result = self._execute_single_attempt()
            if result == "Success":
                return result

            time.sleep(self.config.retry_delay)
        return "Failed: Max attempts reached"

    def _execute_single_attempt(self) -> str:
        """Execute a single mission attempt."""
        target_wp_idx = 0

        for _ in range(self.config.max_steps):
            target_wp = self.waypoints[target_wp_idx]
            self.current_position = self.navigator.move_one_cell(self.current_position, target_wp)
            self.position_history.append(self.current_position)

            if not self.grid_manager.is_valid_position(self.current_position):
                return self._format_failure_message()

            if np.array_equal(self.current_position, self.waypoints[target_wp_idx]):
                target_wp_idx += 1

            if target_wp_idx == len(self.waypoints) and np.array_equal(self.current_position, self.waypoints[-1]):
                return "Success"

        return "Failed: Max steps reached"

    def _format_failure_message(self) -> str:
        """Format failure message with position history."""
        x, y = self.current_position.astype(int)
        return f"Failed: Stopped at ({x}, {y}), traversed cells: {[tuple(np.round(x_, 1)) for x_ in self.position_history]}"
