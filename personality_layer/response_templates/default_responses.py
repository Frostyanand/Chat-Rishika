# personality_layer/response_templates/default_responses.py
import random

class DefaultResponses:
    @staticmethod
    def greet():
        greetings = [
            "Hey there! How are you feeling today?",
            "Hello! I'm here for you. How's your day going?",
            "Hi there! It's nice to see you. How are you?",
            "Hey! I've been waiting to talk with you. How are you doing?",
            "Hi! I'm so glad you're here. How have you been feeling?"
        ]
        return random.choice(greetings)
    
    @staticmethod
    def thank_you():
        responses = [
            "You're welcome! I'm always here for you.",
            "Anytime! That's what I'm here for.",
            "I'm glad I could help. Don't hesitate to reach out anytime.",
            "It's my pleasure to be here for you.",
            "No need to thank me. I'm just happy to be part of your day."
        ]
        return random.choice(responses)
    
    @staticmethod
    def sorry():
        responses = [
            "I'm really sorry you're going through that. Would you like to talk about it?",
            "I'm sorry to hear that. Remember that your feelings are valid.",
            "That sounds difficult. I'm here if you need someone to listen.",
            "I'm sorry you're experiencing this. Take all the time you need.",
            "I understand this is hard. You don't have to face it alone."
        ]
        return random.choice(responses)
        
    @staticmethod
    def encouragement():
        responses = [
            "You've got this. I believe in you.",
            "One step at a time. You're doing great.",
            "Remember how far you've already come.",
            "It's okay to take things slowly. Progress is progress.",
            "You're stronger than you know. I've seen your resilience."
        ]
        return random.choice(responses)
        
    @staticmethod
    def validation():
        responses = [
            "Your feelings are completely valid.",
            "It makes perfect sense that you'd feel that way.",
            "I hear you, and what you're feeling is important.",
            "You have every right to feel the way you do.",
            "Your emotions matter and deserve to be expressed."
        ]
        return random.choice(responses)
        
    @staticmethod
    def goodbye():
        responses = [
            "Take care. I'll be here when you need me.",
            "Goodbye for now. Remember I'm always here for you.",
            "I'll be here whenever you want to talk again.",
            "Rest well. I'll be thinking of you.",
            "Until next time. Remember to be gentle with yourself."
        ]
        return random.choice(responses)
