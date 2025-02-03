import unittest
from unittest.mock import MagicMock, patch
import numpy as np

from src.mission_controller import MissionConfig, MissionController


class TestMissionConfig(unittest.TestCase):
    def test_default_values(self):
        """Test MissionConfig initializes with correct default values."""
        config = MissionConfig()
        self.assertEqual(config.goal, (4, 4))
        self.assertEqual(config.max_steps, 30)
        self.assertEqual(config.retry_delay_sec, 5)
        self.assertEqual(config.max_attempts, 20)
        self.assertEqual(config.position_bounds, (-0.5, 0.5))

    def test_custom_values(self):
        """Test MissionConfig accepts custom values."""
        config = MissionConfig(
            goal=(2, 2),
            max_steps=10,
            retry_delay_sec=1,
            max_attempts=5,
            position_bounds=(-1.0, 1.0)
        )
        self.assertEqual(config.goal, (2, 2))
        self.assertEqual(config.max_steps, 10)
        self.assertEqual(config.retry_delay_sec, 1)
        self.assertEqual(config.max_attempts, 5)
        self.assertEqual(config.position_bounds, (-1.0, 1.0))


class TestMissionController(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock classes with required methods
        self.grid_manager = MagicMock()
        self.grid_manager.is_valid_position = MagicMock(return_value=True)
        
        self.navigator = MagicMock()
        self.navigator.move_one_cell = MagicMock(return_value=np.array([0.0, 0.0]))
        
        self.config = MissionConfig()
        
        self.model = MagicMock()
        self.model.get_waypoints = MagicMock(return_value=[np.array([0.0, 0.0])])
        
        self.controller = MissionController(
            grid_manager=self.grid_manager,
            navigator=self.navigator,
            config=self.config
        )

    def test_initialization(self):
        """Test proper initialization of MissionController."""
        self.assertEqual(self.controller.config, self.config)
        self.assertIsNone(self.controller.current_position)
        self.assertEqual(self.controller.waypoints, [])
        self.assertEqual(self.controller.position_history, [])

    @patch('numpy.random.uniform')
    def test_initialize_position(self, mock_uniform):
        """Test random position initialization."""
        mock_uniform.return_value = np.array([0.3, -0.2])
        position = self.controller.initialize_position()

        mock_uniform.assert_called_once_with(-0.5, 0.5, size=(2))
        np.testing.assert_array_almost_equal(position, np.array([0.3, -0.2]))

    def test_format_failure_message(self):
        """Test failure message formatting."""
        self.controller.current_position = np.array([1.1, 2.2])
        self.controller.position_history = [
            np.array([0.0, 0.0]),
            np.array([1.1, 2.2])
        ]

        message = self.controller._format_failure_message("Stop")
        expected = "Failed: Stop at (1, 2), traversed cells: [(np.float64(0.0), np.float64(0.0)), (np.float64(1.1), np.float64(2.2))]"
        self.assertEqual(message, expected)

    @patch('time.sleep')
    def test_execute_mission_success(self, mock_sleep):
        """Test successful mission execution."""
        # Mock initial position
        self.controller.initialize_position = MagicMock(return_value=np.array([0.0, 0.0]))
        
        # Mock model response
        self.model.get_waypoints.return_value = [
            np.array([0.0, 0.0]),
            np.array([4.0, 4.0])
        ]
        
        # Mock navigation behavior
        self.navigator.move_one_cell.return_value = np.array([4.0, 4.0])
        self.grid_manager.is_valid_position.return_value = True

        # Execute mission
        result, history = self.controller.execute_mission(self.model)

        # Verify results
        self.assertEqual(result, "Success")
        self.assertEqual(len(history), 1)
        np.testing.assert_array_equal(history[0], np.array([4.0, 4.0]))
        mock_sleep.assert_not_called()

    @patch('time.sleep')
    def test_execute_mission_max_attempts(self, mock_sleep):
        """Test mission failure after maximum attempts."""
        # Configure test for failure
        self.controller.config.max_attempts = 2
        self.controller.initialize_position = MagicMock(return_value=np.array([0.0, 0.0]))
        self.model.get_waypoints.return_value = [np.array([1.0, 1.0])]
        self.navigator.move_one_cell.return_value = np.array([1.0, 1.0])
        self.grid_manager.is_valid_position.return_value = False

        # Execute mission
        result, history = self.controller.execute_mission(self.model)

        # Verify results
        self.assertEqual(result, "Failed: Max attempts reached")
        mock_sleep.assert_called_with(self.config.retry_delay_sec)
        self.assertEqual(mock_sleep.call_count, 2)

    def test_execute_single_attempt_timeout(self):
        """Test single attempt failure due to timeout."""
        # Set up a mission that will timeout
        self.controller.config.max_steps = 2
        self.controller.current_position = np.array([0.0, 0.0])
        self.controller.waypoints = [np.array([4.0, 4.0])]
        self.grid_manager.is_valid_position.return_value = True
        self.navigator.move_one_cell.return_value = np.array([1.0, 1.0])

        # Execute single attempt
        result = self.controller._execute_single_attempt()

        # Verify timeout
        self.assertTrue(result.startswith("Failed: Timeout"))
        self.assertEqual(len(self.controller.position_history), 2)

    def test_execute_single_attempt_debug_mode(self):
        """Test single attempt execution in debug mode."""
        self.controller.current_position = np.array([0.0, 0.0])
        self.controller.waypoints = [np.array([1.0, 1.0])]
        self.grid_manager.is_valid_position.return_value = True
        self.navigator.move_one_cell.return_value = np.array([1.0, 1.0])

        with patch('builtins.print') as mock_print:
            self.controller._execute_single_attempt(debug=True)
            mock_print.assert_called()  # Verify debug information was printed


if __name__ == '__main__':
    unittest.main()