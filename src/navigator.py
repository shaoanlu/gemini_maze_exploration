from enum import Enum
import numpy as np


class Direction(Enum):
    RIGHT = (1, 0)
    UP = (0, 1)
    LEFT = (-1, 0)
    DOWN = (0, -1)

    def as_array(self) -> np.ndarray:
        return np.array(self.value)


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
            cur_cell + Direction.RIGHT.as_array(),
            cur_cell + Direction.UP.as_array(),
            cur_cell + Direction.LEFT.as_array(),
            cur_cell + Direction.DOWN.as_array(),
        ]

        # move in a direciton that minimizes the distance to the target waypoint
        distances = [np.linalg.norm(tar_cell - pos) for pos in movements]
        next_pos = movements[np.argmin(distances)]
        return next_pos.astype(np.int32)
