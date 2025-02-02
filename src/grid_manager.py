import numpy as np
from matplotlib import pyplot as plt
from dataclasses import dataclass
from typing import Tuple, List


@dataclass
class GridConfig:
    grid_size: Tuple[int, int] = (5, 5)
    image_size: int = 50  # 50x50 RGB image representing traversibility of a 5x5 maze
    threshold: int = 255  # White color


class GridManager:
    def __init__(self, config: GridConfig):
        self.config = config
        self.grid = np.empty(config.grid_size)
        self.img2grid_scale = self.config.image_size // self.config.grid_size[0]

    def load_from_image(self, image_path: str) -> np.ndarray:
        """Load and process grid from image.

        Thr output is a binary 2D grid where 1 represents a valid position and 0 an invalid one.
        This method also involes a transformation of coordinates from image to grid space.
        As image coordinates are (0, 0) at the top-left corner and grid coordinates are (0, 0) at the bottom-left corner,
        we need to invert the y-axis and scale the coordinates accordingly.
        """
        im = plt.imread(image_path, format="jpeg")
        self.image = im
        for x in range(self.config.grid_size[0]):
            for y in range(self.config.grid_size[1]):
                color = im[
                    self.config.image_size - self.img2grid_scale * x - self.img2grid_scale // 2,
                    self.img2grid_scale * y + self.img2grid_scale // 2,
                ][0]
                self.grid[y, x] = 1 if color == self.config.threshold else 0
        return self.grid

    def is_valid_position(self, position: np.ndarray) -> bool:
        """Check if position is valid in the grid."""
        x, y = position.astype(int)
        if 0 <= x < self.config.grid_size[0] and 0 <= y < self.config.grid_size[1]:
            return self.grid[x, y] == 1
        return False
