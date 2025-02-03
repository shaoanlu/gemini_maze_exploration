import unittest
from unittest.mock import patch
import numpy as np
from src.grid_manager import GridConfig, GridManager  # Assuming the original code is in grid_manager.py


class TestGridConfig(unittest.TestCase):
    def test_default_values(self):
        """Test that GridConfig initializes with correct default values."""
        config = GridConfig()
        self.assertEqual(config.grid_size, (5, 5))
        self.assertEqual(config.image_size, 50)
        self.assertEqual(config.threshold, 255)

    def test_custom_values(self):
        """Test that GridConfig accepts custom values."""
        config = GridConfig(grid_size=(10, 10), image_size=100, threshold=128)
        self.assertEqual(config.grid_size, (10, 10))
        self.assertEqual(config.image_size, 100)
        self.assertEqual(config.threshold, 128)


class TestGridManager(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.config = GridConfig()
        self.grid_manager = GridManager(self.config)

    def test_initialization(self):
        """Test proper initialization of GridManager."""
        self.assertEqual(self.grid_manager.config, self.config)
        self.assertEqual(self.grid_manager.img2grid_scale, 10)  # 50 / 5 = 10
        self.assertTrue(isinstance(self.grid_manager.grid, np.ndarray))
        self.assertEqual(self.grid_manager.grid.shape, (5, 5))

    @patch('matplotlib.pyplot.imread')
    def test_load_from_image(self, mock_imread):
        """Test loading and processing grid from image."""
        # Create a mock 50x50 image with known values
        mock_image = np.zeros((50, 50, 3))
        # Set some pixels to white (255) to create a pattern
        mock_image[45:, 5:10] = 255  # This should result in grid[0,0] = 1
        mock_imread.return_value = mock_image

        # Test loading the image
        grid = self.grid_manager.load_from_image("dummy_path.jpg")
        
        # Verify imread was called
        mock_imread.assert_called_once_with("dummy_path.jpg", format="jpeg")
        
        # Check grid dimensions
        self.assertEqual(grid.shape, (5, 5))
        
        # Verify specific grid values based on our mock image
        self.assertEqual(grid[0, 0], 1)  # Should be 1 where we set white pixels
        self.assertEqual(grid[1, 1], 0)  # Should be 0 in black areas

    def test_is_valid_position(self):
        """Test position validation in the grid."""
        # Set up a simple test grid
        self.grid_manager.grid = np.array([
            [1, 0, 1],
            [0, 1, 0],
            [1, 0, 1]
        ])
        self.grid_manager.config = GridConfig(grid_size=(3, 3))

        # Test valid positions
        self.assertTrue(self.grid_manager.is_valid_position(np.array([0, 0])))
        self.assertTrue(self.grid_manager.is_valid_position(np.array([1, 1])))
        
        # Test invalid positions
        self.assertFalse(self.grid_manager.is_valid_position(np.array([0, 1])))
        self.assertFalse(self.grid_manager.is_valid_position(np.array([3, 3])))  # Out of bounds
        self.assertFalse(self.grid_manager.is_valid_position(np.array([-1, 0])))  # Negative index

    def test_is_valid_position_edge_cases(self):
        """Test edge cases for position validation."""
        self.grid_manager.grid = np.ones((5, 5))  # All positions valid
        
        # Test float inputs (should be converted to int)
        self.assertTrue(self.grid_manager.is_valid_position(np.array([0.9, 0.1])))
        
        # Test positions exactly at boundaries
        self.assertTrue(self.grid_manager.is_valid_position(np.array([0, 0])))  # Bottom-left corner
        self.assertTrue(self.grid_manager.is_valid_position(np.array([4, 4])))  # Top-right corner
        
        # Test out-of-bounds positions
        self.assertFalse(self.grid_manager.is_valid_position(np.array([5, 0])))
        self.assertFalse(self.grid_manager.is_valid_position(np.array([0, 5])))


if __name__ == '__main__':
    unittest.main()