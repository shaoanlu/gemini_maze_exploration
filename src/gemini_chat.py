from google import generativeai, genai  # old and new API
from typing import List, Tuple


class GeminiChat:
    def __init__(self, model: generativeai.GenerativeModel):
        self.model = model
        self.chat = self.model.start_chat()

    def get_waypoints(self, prompt) -> List[Tuple]:
        response = self.chat.send_message([prompt])
        waypoints = eval(response.candidates[0].content.parts[0].text)  # Convert string to list
        return waypoints
    
    @staticmethod
    def clean_instruction(instr: str) -> str:
        char_to_be_deleted = ['\n', '\t', "'", "`", '{', "}"]
        for c in char_to_be_deleted:
            instr = instr.replace(c, "")
        return instr


class GeminiThinkChat(GeminiChat):
    def __init__(self, model: genai.Client, model_name: str='gemini-2.0-flash-thinking-exp'):
        self.model = model
        self.chat = self.model.chats.create(model=model_name)

    def get_waypoints(self, prompt) -> List[Tuple]:
        response = self.chat.send_message([prompt])
        waypoints = eval(self.clean_instruction(response.text))  # Convert string to list
        return waypoints
