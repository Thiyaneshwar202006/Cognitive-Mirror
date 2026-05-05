# scenarios.py
import random

DATA = [
    {
        "id": "logic_1",
        "type": "Logic Puzzle",
        "text": """
        **The Two Doors**
        You are in a room with two doors. One leads to freedom, the other to a bottomless pit.
        There are two guards. One always tells the truth, the other always lies. You don't know which is which.
        You can ask **one** question to **one** guard to find the door to freedom.
        
        What do you ask?
        """
    },
    {
        "id": "lateral_1",
        "type": "Lateral Thinking",
        "text": """
        **The Heavy Rock**
        A man is pushing his car. He stops when he reaches a hotel. When he gets there, he knows he is bankrupt. 
        
        Why?
        """
    },
    {
        "id": "real_1",
        "type": "Management Scenario",
        "text": """
        **The Overwhelmed Junior**
        You are a manager. A junior employee is missing deadlines. You know they are trying hard, but they are too proud to ask for help. 
        If they miss the next deadline, the client will fire your firm.
        
        How do you intervene without crushing their confidence?
        """
    },
    {
        "id": "code_1",
        "type": "Technical Logic",
        "text": """
        **The Infinite Loop**
        You are reviewing a colleague's code. You notice a 'while' loop that depends on a variable fetched from an external API. 
        If the internet cuts out, the variable never updates.
        
        What is the specific risk here and how do you fix it in one sentence?
        """
    }
]

def get_random_scenario():
    return random.choice(DATA)