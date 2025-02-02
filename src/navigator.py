from enum import Enum
import numpy as np
from typing import List, Optional


class Direction(Enum):
    RIGHT = np.array([1, 0])
    UP = np.array([0, 1])
    LEFT = np.array([-1, 0])
    DOWN = np.array([0, -1])


class Navigator:
    @staticmethod
    def move_one_cell(cur_cell: np.ndarray, tar_cell: np.ndarray) -> np.ndarray:
        """
        Calculate next cell position based on target.

        Args:
            cur_cell: Current cell position of format (x, y).
            tar_cell: Target cell position of format (x, y).
        """
        if np.array_equal(cur_cell, tar_cell):
            return cur_cell

        movements = [
            cur_cell + Direction.RIGHT.value,
            cur_cell + Direction.UP.value,
            cur_cell + Direction.LEFT.value,
            cur_cell + Direction.DOWN.value,
        ]

        # move in a direciton that minimizes the distance to the target waypoint
        distances = [np.linalg.norm(tar_cell - pos) for pos in movements]
        next_pos = movements[np.argmin(distances)]
        return next_pos.astype(np.int32)
