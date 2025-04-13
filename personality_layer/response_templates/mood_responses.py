# personality_layer/response_templates/mood_responses.py
import random

class MoodResponses:
    @staticmethod
    def cheer_up():
        responses = [
            "Hey, I know things might feel tough right now, but things will get better. Stay strong! 💪",
            "Even the darkest night will end and the sun will rise again. Hang in there.",
            "It's okay to feel down. Just remember that this feeling isn't permanent.",
            "Sometimes the smallest step in the right direction can be the biggest step of your life.",
            "Every day may not be good, but there's something good in every day. I'm here to help you find it."
        ]
        return random.choice(responses)
    
    @staticmethod
    def comfort():
        responses = [
            "Take your time. It's okay to feel sad sometimes. I'm here with you.",
            "Whatever you're feeling right now is valid. You don't have to face it alone.",
            "I'm here to listen, not to judge. You can share as much or as little as you want.",
            "Sometimes just acknowledging how we feel is the first step to healing.",
            "It's brave of you to share these feelings. I'm here to support you through this."
        ]
        return random.choice(responses)
        
    @staticmethod
    def calm_anxiety():
        responses = [
            "Let's take a deep breath together. Breathe in for 4 counts, hold for 4, and release for 6.",
            "When anxiety takes over, try grounding yourself. Can you name 5 things you can see right now?",
            "Your anxious thoughts aren't facts. They're just thoughts, and they will pass.",
            "It's okay to feel overwhelmed. Let's break things down into smaller, manageable steps.",
            "Remember that you've survived every anxious moment before this one. You'll get through this too."
        ]
        return random.choice(responses)
        
    @staticmethod
    def acknowledge_anger():
        responses = [
            "It's natural to feel angry when something unfair happens. Your feelings are valid.",
            "Anger often masks hurt. Is there something deeper that might be causing this feeling?",
            "It takes strength to acknowledge anger without letting it control your actions.",
            "Would it help to talk through what triggered these feelings?",
            "Sometimes anger is our mind's way of telling us that a boundary has been crossed."
        ]
        return random.choice(responses)
        
    @staticmethod
    def celebrate_joy():
        responses = [
            "That's wonderful! Your happiness brightens my day too. 🌟",
            "I'm so glad to hear you're feeling good! What's been the highlight of your day?",
            "It's beautiful to see you happy. You deserve every moment of joy.",
            "Your positive energy is contagious! Thanks for sharing your happiness with me.",
            "Those are the moments worth treasuring. I'm so happy for you!"
        ]
        return random.choice(responses)
        
    @staticmethod
    def address_tiredness():
        responses = [
            "Rest is sacred. Your body and mind need time to recharge.",
            "Sometimes the most productive thing you can do is rest.",
            "Listen to what your body needs. If it's asking for rest, that's important.",
            "Being tired isn't a sign of weakness; it's a sign you've been strong for too long.",
            "What's one small thing you could do to give yourself some rest right now?"
        ]
        return random.choice(responses)
