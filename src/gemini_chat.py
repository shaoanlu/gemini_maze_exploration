from google import generativeai, genai  # old and new API
from typing import List, Tuple
import numpy as np


class GeminiChatInterface:
    def __init__(self):
        pass

    def get_waypoints(self, prompt: str) -> List[Tuple]:
        raise NotImplementedError

    def reset_chat(self):
        raise NotImplementedError

    @staticmethod
    def clean_instruction(instr: str) -> str:
        char_to_be_deleted = ["\n", "\t", "'", "`", "{", "}"]
        for c in char_to_be_deleted:
            instr = instr.replace(c, "")
        return instr

    @staticmethod
    def convert_to_list_of_numpy_array(waypoints: List[Tuple]) -> List[np.ndarray]:
        return [np.array(wp) for wp in waypoints]


class GeminiChat(GeminiChatInterface):
    def __init__(self, model: generativeai.GenerativeModel):
        self.model = model
        self.chat = self.model.start_chat()

    def get_waypoints(self, prompt) -> List[Tuple]:
        response = self.chat.send_message([prompt])
        waypoints = eval(response.candidates[0].content.parts[0].text)  # Convert string to list
        return self.convert_to_list_of_numpy_array(waypoints)

    def reset_chat(self):
        self.chat = self.model.start_chat()


class GeminiThinkChat(GeminiChatInterface):
    def __init__(self, model: genai.Client, model_name: str = "gemini-2.0-flash-thinking-exp", instruction: str = ""):
        self.model = model
        self.chat = self.model.chats.create(model=model_name)
        self.system_instruction = instruction
        self.is_first_msg = True  # need to append instruciton in the first message

    def get_waypoints(self, prompt: str, debug: bool = False) -> List[Tuple]:
        if self.is_first_msg:
            prompt = self.system_instruction + "\n" + prompt
            self.is_first_msg = False
        response = self.chat.send_message([prompt])
        waypoints = eval(self.clean_instruction(response.text))  # Convert string to list
        if debug:
            print(f"{response.text=}\n{waypoints=}\n")
        return self.convert_to_list_of_numpy_array(waypoints)

    def reset_chat(self):
        self.chat = self.model.chats.create(model=self.model_name)
        self.is_first_msg = True
