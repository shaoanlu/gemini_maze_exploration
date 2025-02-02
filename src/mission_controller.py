from dataclasses import dataclass
from typing import Tuple, List
import numpy as np
import time

from src.grid_manager import GridManager
from src.navigator import Navigator
from src.gemini_chat import GeminiChatInterface


@dataclass
class MissionConfig:
    goal: tuple = (4, 4)
    max_steps: int = 30
    retry_delay_sec: int = 5
    max_attempts: int = 20
    position_bounds: Tuple[float, float] = (-0.5, 0.5)


class MissionController:
    def __init__(self, grid_manager: GridManager, navigator: Navigator, config: MissionConfig):
        self.grid_manager = grid_manager
        self.navigator = navigator
        self.config = config
        self.current_position: np.ndarray | None = None
        self.waypoints: List[Tuple] = []
        self.position_history = []

    def initialize_position(self) -> np.ndarray:
        """Initialize random starting position."""
        return np.round(np.random.uniform(self.config.position_bounds[0], self.config.position_bounds[1], size=(2)), 1)

    def execute_mission(self, model: GeminiChatInterface, debug: bool = False) -> Tuple[str, List[np.ndarray]]:
        """
        Execute complete navigation mission.

        Returns:
            str: Mission status
            List[np.ndarray]: List of traversed XY positions
        """
        # Run the mission for a number of attempts, each time with a different init position and prompt
        for attempt in range(self.config.max_attempts):
            self.current_position = self.initialize_position()
            self.position_history = []

            # Prompt the LLM to get waypoints suggestion
            if attempt == 0:
                prompt = f"Start. you are at ({self.current_position[0]}, {self.current_position[1]})"
            self.waypoints = model.get_waypoints(prompt)

            # run the mission (simulation)
            result = self._execute_single_attempt()

            # print debug information
            if debug:
                print(f"[Trial {attempt + 1}]\n{prompt=}\n{self.waypoints=}\n{result=}\n")
            prompt = result

            if result == "Success":
                return (result, self.position_history)

            # add a delay before retrying to avoid API rate limiting
            time.sleep(self.config.retry_delay_sec)
        return ("Failed: Max attempts reached", self.position_history)

    def _execute_single_attempt(self, debug: bool = False) -> str:
        """
        Execute a single mission attempt.
        """
        target_waypoint_idx = 0  # index of the current target waypoint

        # Traverse waypoints until reaching the goal or max steps or invalid position
        for _ in range(self.config.max_steps):
            target_position = self.waypoints[target_waypoint_idx]
            self.current_position = self.navigator.move_one_cell(self.current_position, target_position)
            self.position_history.append(self.current_position)

            # Check if the current position is valid (is traversable)
            if not self.grid_manager.is_valid_position(self.current_position):
                return self._format_failure_message("Stop")

            # Move to the next waypoint if the current one is reached
            if np.array_equal(self.current_position, self.waypoints[target_waypoint_idx]):
                target_waypoint_idx += 1

            # Check if the mission is completed
            is_at_last_waypoint = np.array_equal(self.current_position, self.waypoints[-1])
            is_at_goal = np.array_equal(self.current_position, np.array(self.config.goal))
            if is_at_last_waypoint and is_at_goal:
                return "Success"

            # print debug information
            if debug:
                print(f"{self.current_position=}, {target_position=}, {is_at_last_waypoint=}, {is_at_goal=}")

        return self._format_failure_message("Timeout")

    def _format_failure_message(self, failure_type: str) -> str:
        """Format failure message with position history."""
        x, y = self.current_position.astype(int)
        return (
            f"Failed: {failure_type} at ({x}, {y}), traversed cells: {[tuple(np.round(x_, 1)) for x_ in self.position_history]}"
        )
