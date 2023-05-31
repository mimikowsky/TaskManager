from datetime import datetime

class Task:
    def __init__(self, description) -> None:
        self.time = datetime.now()
        self.description = description

    def __repr__(self) -> str:
        return f"Task: {self.time} - {self.description}"
    
    def __str__(self) -> str:
        return f"Task: {self.time} - {self.description}"