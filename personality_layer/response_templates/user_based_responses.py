# personality_layer/response_templates/user_based_responses.py
import random

class UserBasedResponses:
    def __init__(self, user_data):
        self.user_name = user_data.get("name", "there")
        self.user_interests = user_data.get("interests", [])
        self.user_preferences = user_data.get("preferences", {})
        self.important_dates = user_data.get("important_dates", {})
        self.conversation_style = user_data.get("conversation_style", "supportive")
        self.mental_health_history = user_data.get("mental_health_history", {})

    def personalized_greeting(self):
        greetings = [
            f"Hey {self.user_name}, how's your day been? 😊",
            f"Hi {self.user_name}! It's so good to see you again.",
            f"Hello {self.user_name}! I've been looking forward to our chat.",
            f"{self.user_name}! I'm happy you're here. How are you feeling?",
            f"Welcome back, {self.user_name}! How have things been since we last talked?"
        ]
        return random.choice(greetings)

    def personalized_comfort(self):
        responses = [
            f"{self.user_name}, it's perfectly okay to take things slow. You've got this.",
            f"I know it's tough right now, {self.user_name}. Remember that this feeling will pass.",
            f"You've overcome difficult situations before, {self.user_name}. I believe in you.",
            f"{self.user_name}, I'm here with you through this. You don't have to face it alone.",
            f"Take all the time you need, {self.user_name}. Healing isn't linear."
        ]
        return random.choice(responses)
        
    def interest_based_question(self):
        """Generate a question based on user's known interests"""
        if not self.user_interests:
            return f"I'd love to learn more about what interests you, {self.user_name}. What do you enjoy doing?"
            
        interest = random.choice(self.user_interests)
        questions = [
            f"How's your interest in {interest} going lately?",
            f"Have you had any time for {interest} recently?",
            f"I remember you enjoy {interest}. Anything new happening with that?",
            f"Last time we talked about {interest}. Have you made any progress with it?",
            f"I'd love to hear more about your passion for {interest} today."
        ]
        return random.choice(questions)
        
    def check_important_date(self, current_date):
        """Check if today is an important date for the user"""
        for event, date in self.important_dates.items():
            if date == current_date:
                return f"By the way, {self.user_name}, I remembered that today is {event}! {self.celebrate_occasion(event)}"
        return None
        
    def celebrate_occasion(self, occasion):
        """Generate a celebratory message for a special occasion"""
        birthday_messages = [
            "Happy birthday! 🎂 I hope your day is filled with joy!",
            "Wishing you the happiest of birthdays today!",
            "Another trip around the sun! Hope it's a wonderful celebration."
        ]
        
        anniversary_messages = [
            "Happy anniversary! 🎉 That's a wonderful milestone!",
            "Congratulations on your anniversary! That's something to celebrate.",
            "Happy anniversary! I hope it's a beautiful day of reflection and joy."
        ]
        
        generic_messages = [
            "I hope it's a wonderful day for you!",
            "That's definitely worth celebrating!",
            "I hope you enjoy this special day!"
        ]
        
        if "birthday" in occasion.lower():
            return random.choice(birthday_messages)
        elif "anniversary" in occasion.lower():
            return random.choice(anniversary_messages)
        else:
            return random.choice(generic_messages)
            
    def adapt_to_conversation_style(self, message):
        """Adapt response style based on user's preferred conversation style"""
        style = self.conversation_style.lower()
        
        if style == "supportive":
            return f"I'm here to support you, {self.user_name}. {message}"
        elif style == "analytical":
            return f"Let's think about this analytically, {self.user_name}. {message}"
        elif style == "casual":
            return f"Hey {self.user_name}! {message}"
        elif style == "formal":
            return f"Good day, {self.user_name}. {message}"
        else:
            return message

    def mental_health_support(self, concern_type, severity):
        """Generate mental health support responses with appropriate escalation"""
        if concern_type == "depression":
            initial_responses = [
                "I hear you. Depression can be really overwhelming.",
                "It takes courage to talk about these feelings.",
                "Those feelings of hopelessness are valid, and you're not alone."
            ]
            
            if severity > 0.7:
                responses = [
                    "Have you considered talking to a mental health professional? They can provide the support you need.",
                    "I care about your wellbeing. Would you be open to reaching out to a counselor?",
                    "Depression is serious, and you deserve professional support. Can I suggest some resources?"
                ]
            else:
                responses = [
                    "Would you like to talk more about what you're experiencing?",
                    "Is there someone you trust that you can talk to about this?",
                    "Sometimes small steps can help. What might make today a bit easier?"
                ]
                
        elif concern_type == "anxiety":
            initial_responses = [
                "Anxiety can be really challenging to deal with.",
                "It's understandable to feel overwhelmed.",
                "Living with anxiety is difficult, and your feelings are valid."
            ]
            
            if severity > 0.7:
                responses = [
                    "Have you talked to a healthcare provider about your anxiety?",
                    "There are professionals who specialize in anxiety treatment. Would you like to learn more?",
                    "This level of anxiety deserves proper support. Have you considered counseling?"
                ]
            else:
                responses = [
                    "What helps you feel grounded when anxiety hits?",
                    "Would you like to explore some coping strategies together?",
                    "Sometimes sharing these feelings can help lighten the load."
                ]
        else:
            initial_responses = [
                "Thank you for sharing this with me.",
                "I'm here to listen and support you.",
                "It's important to take care of your mental health."
            ]
            responses = [
                "How long have you been feeling this way?",
                "Is there anything specific triggering these feelings?",
                "What kind of support would be most helpful right now?"
            ]
            
        # Combine initial response with follow-up
        return f"{random.choice(initial_responses)} {random.choice(responses)}"
        
    def resource_suggestion(self, concern_type):
        """Provide appropriate mental health resource suggestions"""
        general_resources = [
            "Many people find talking to a counselor or therapist helpful.",
            "Mental health professionals are trained to help with exactly these kinds of challenges.",
            "There are confidential crisis helplines available 24/7 if you need someone to talk to."
        ]
        
        specific_resources = {
            "depression": [
                "Depression is treatable, and a mental health professional can help guide you through treatment options.",
                "There are different approaches to managing depression, from therapy to medication, that a professional can discuss with you.",
                "Many people find that a combination of counseling and lifestyle changes helps with depression."
            ],
            "anxiety": [
                "Anxiety specialists can teach you effective coping strategies and techniques.",
                "There are many evidence-based treatments for anxiety that a professional can guide you through.",
                "A mental health professional can help you develop a personalized plan to manage anxiety."
            ]
        }
        
        if concern_type in specific_resources:
            return f"{random.choice(general_resources)} {random.choice(specific_resources[concern_type])}"
        return random.choice(general_resources)
