from networking.service import Service
from robot.aluxe3.context import Aluxe3Context

class ContextProvider(Service):
    def __init__(self, context:Aluxe3Context):
        super().__init__("context")
        self.context = context
    def process(self, data):
        return {
            "header": "context",
            "status": "success", 
            "content": {
                "enviroment": {
                    "distances": {
                        "sl": self.context.env.us_left_dist,
                        "sr": self.context.env.us_right_dist,
                        "sb": self.context.env.us_back_dist
                    }
                },
            }
        }
    