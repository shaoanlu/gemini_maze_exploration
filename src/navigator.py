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
        """Calculate next cell position based on target."""
        if np.array_equal(cur_cell, tar_cell):
            return cur_cell

        movements = [
            (Direction.RIGHT.value, cur_cell + Direction.RIGHT.value),
            (Direction.UP.value, cur_cell + Direction.UP.value),
            (Direction.LEFT.value, cur_cell + Direction.LEFT.value),
            (Direction.DOWN.value, cur_cell + Direction.DOWN.value),
        ]

        distances = [np.linalg.norm(tar_cell - pos) for _, pos in movements]
        _, next_pos = movements[np.argmin(distances)]
        return next_pos.astype(np.int32)
