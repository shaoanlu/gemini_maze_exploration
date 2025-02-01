import google.generativeai as genai


class GeminiChat:
    def __init__(self, model: genai.GenerativeModel):
        self.model = model
        self.chat = self.model.start_chat()

    def get_waypoints(self, prompt):
        response = self.chat.send_message([prompt])
        waypoints = eval(response.candidates[0].content.parts[0].text)  # Convert string to list
        return waypoints
