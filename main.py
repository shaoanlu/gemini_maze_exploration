# main.py
import google.generativeai as genai
import os

from grid_manager import GridManager, GridConfig
from navigator import Navigator
from mission_controller import MissionController, MissionConfig


API_KEY = os.environ["GOOGLE_API_KEY"]


def load_prompt_file(file_path="prompt.txt", encoding="utf-8"):
    try:
        with open(file_path, "r", encoding=encoding) as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find prompt file: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading prompt file: {str(e)}")


def main():
    # Initialize components
    grid_config = GridConfig()
    grid_manager = GridManager(grid_config)
    grid_manager.load_from_image("floor1.jpg")

    navigator = Navigator()

    mission_config = MissionConfig()
    mission_controller = MissionController(grid_manager, navigator, mission_config)

    # Initialize model
    genai.configure(api_key=API_KEY)
    instruction = load_prompt_file(file_path="prompt.txt", encoding="utf-8")
    model = genai.GenerativeModel("models/gemini-2.0-flash-exp", system_instruction=instruction)
    chat = model.start_chat()

    # Execute mission
    result = mission_controller.execute_mission(chat)
    print(f"\nFinal result: {result}")


if __name__ == "__main__":
    main()
