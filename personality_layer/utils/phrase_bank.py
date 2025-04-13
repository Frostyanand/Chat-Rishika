# personality_layer/utils/phrase_bank.py
import random
import json
import os

class PhraseBank:
    """A class to manage and retrieve phrases for various conversation scenarios"""
    
    def __init__(self, phrases_file=None):
        """Initialize the phrase bank"""
        # Initialize base categories
        self.categories = {
            "greetings": [
                "Hey! How's it going?",
                "Hi there!",
                "Hey, good to see you!",
                "Hi! How are you?", 
                "Hello! How's your day been?"
            ],
            "comfort": {
                "sadness": [
                    "I'm here with you through this sadness. Sometimes just having someone to listen can help.",
                    "It's okay to feel sad. Your feelings are valid.",
                    "Sadness is a natural part of being human. I'm here with you.",
                    "Sometimes the world feels heavy. You don't have to carry that weight alone.",
                    "I'm here with you through this difficult time."
                ],
                "anxiety": [
                    "Let's take a deep breath together.",
                    "Anxiety can feel overwhelming, but you've gotten through difficult moments before.",
                    "Focus on what you can control right now.",
                    "You're doing the best you can with what you have right now.",
                    "I'm right here with you through this anxious moment."
                ],
                "anger": [
                    "Your anger is valid. It's a natural response.",
                    "I hear how frustrated you are.",
                    "Your feelings make sense given what happened.",
                    "It's okay to feel angry about that.",
                    "That would make anyone feel angry."
                ],
                "fear": [
                    "It takes courage to face fear. I'm here with you.",
                    "Fear is trying to protect you, even if it feels overwhelming.",
                    "One small step at a time.",
                    "You're braver than you know.",
                    "I believe in your ability to handle this."
                ],
                "grief": [
                    "I'm so sorry for your loss.",
                    "Grief has no timeline. Take the time you need.",
                    "Your feelings are valid, whatever they are.",
                    "There's no right way to grieve.",
                    "I'm here to listen whenever you need to talk."
                ],
                "general": [
                    "That sounds tough. I'm here to listen.",
                    "I hear you, and what you're feeling matters.",
                    "You don't have to go through this alone.",
                    "Your feelings are valid.",
                    "I'm here to support you through this."
                ]
            },
            "celebration": [
                "That's wonderful!",
                "I'm so happy for you!",
                "That's really great news!",
                "How exciting!",
                "That's definitely worth celebrating!"
            ],
            "empathy": [
                "I understand that must be difficult.",
                "That sounds challenging.",
                "I can see why you'd feel that way.",
                "I hear you.",
                "That makes a lot of sense, given what you're going through."
            ],
            "follow_up": [
                "How do you feel about that?",
                "What do you think about that?",
                "What's your perspective on this?",
                "How has that been affecting you?",
                "Would you like to talk more about this?"
            ]
        }
        
        # Track recently used phrases to avoid repetition
        self.max_recent_phrases = 20
        self.recent_phrases = []
        self.max_phrases_per_response = 2
        
        # Load additional phrases if provided
        if phrases_file and os.path.exists(phrases_file):
            self.load_phrases(phrases_file)
    
    def get_comfort_phrase(self, emotion="general"):
        """Get a comforting phrase appropriate for the given emotion"""
        emotion = emotion.lower()
        if emotion in self.categories["comfort"]:
            phrases = self.categories["comfort"][emotion]
        else:
            phrases = self.categories["comfort"]["general"]
            
        # Filter out recently used phrases if possible
        available_phrases = [p for p in phrases if p not in self.recent_phrases]
        if not available_phrases:
            available_phrases = phrases
        
        phrase = random.choice(available_phrases)
        
        # Add to recent phrases and trim if needed
        self.recent_phrases.append(phrase)
        if len(self.recent_phrases) > self.max_recent_phrases:
            self.recent_phrases.pop(0)
            
        return phrase
    
    def get_phrase(self, category, fallback=None):
        """Get a random phrase from a category, avoiding recent repetition"""
        if isinstance(category, list):
            phrases = category
        elif category in self.categories:
            phrases = self.categories[category]
        else:
            return fallback if fallback else "I'm here with you"
            
        # Filter out recently used phrases if possible
        available_phrases = [p for p in phrases if p not in self.recent_phrases]
        
        # If all phrases have been recently used, reset and use any
        if not available_phrases:
            available_phrases = phrases
        
        phrase = random.choice(available_phrases)
        
        # Add to recent phrases and trim if needed
        self.recent_phrases.append(phrase)
        if len(self.recent_phrases) > self.max_recent_phrases:
            self.recent_phrases.pop(0)
            
        return phrase
        
    def load_phrases(self, phrases_file):
        """Load phrases from a JSON file"""
        try:
            with open(phrases_file, 'r') as f:
                additional_phrases = json.load(f)
                
            # Merge with existing categories
            for category, phrases in additional_phrases.items():
                if category in self.categories:
                    if isinstance(self.categories[category], dict):
                        # For nested categories like comfort
                        for subcat, subphrases in phrases.items():
                            if subcat in self.categories[category]:
                                self.categories[category][subcat].extend(subphrases)
                            else:
                                self.categories[category][subcat] = subphrases
                    else:
                        # For flat categories
                        self.categories[category].extend(phrases)
                else:
                    self.categories[category] = phrases
                    
        except Exception as e:
            print(f"Error loading phrases file: {e}")
    
    def save_phrases(self, phrases_file):
        """Save phrases to a JSON file"""
        try:
            with open(phrases_file, 'w') as f:
                json.dump(self.categories, f, indent=2)
                
        except Exception as e:
            print(f"Error saving phrases file: {e}")
    
    def add_phrase(self, category, phrase):
        """Add a new phrase to a category"""
        if category not in self.categories:
            self.categories[category] = []
            
        if phrase not in self.categories[category]:
            self.categories[category].append(phrase)
    
    def get_all_categories(self):
        """Get a list of all available categories"""
        return list(self.categories.keys())
    
    def get_all_phrases(self, category):
        """Get all phrases in a category"""
        return self.categories.get(category, [])
    
    def get_layered_response(self, primary_categories, secondary_categories=None, max_phrases=None):
        """
        Creates a more natural-sounding response by combining phrases from different categories.
        Limits the number of phrases to avoid overly verbose responses.
        
        Args:
            primary_categories (list): List of main category names to include
            secondary_categories (list, optional): List of optional categories to maybe include
            max_phrases (int, optional): Maximum number of phrases to include
            
        Returns:
            str: Combined natural response
        """
        if max_phrases is None:
            max_phrases = self.max_phrases_per_response
            
        # Ensure we don't try to use more categories than our max phrases
        if len(primary_categories) > max_phrases:
            primary_categories = random.sample(primary_categories, max_phrases)
        
        # Start with primary categories
        response_parts = []
        for category in primary_categories:
            phrase = self.get_phrase(category)
            if phrase:
                response_parts.append(phrase)
        
        # Add secondary categories if we have room and with a 50% chance each
        if secondary_categories and len(response_parts) < max_phrases:
            remaining_slots = max_phrases - len(response_parts)
            # Shuffle and limit secondary categories
            random.shuffle(secondary_categories)
            for category in secondary_categories[:remaining_slots]:
                if random.random() < 0.5:  # 50% chance to include
                    phrase = self.get_phrase(category)
                    if phrase:
                        response_parts.append(phrase)
        
        # Combine phrases into a natural response
        response = " ".join(response_parts)
        
        return response

    def load_legacy_phrases(self, phrases):
        """Load phrases from the legacy format into the new structure"""
        try:
            # Handle comfort phrases first since they have a special nested structure
            if "comfort_phrases" in phrases and phrases["comfort_phrases"]:
                if "comfort" not in self.categories:
                    self.categories["comfort"] = {}
                    
                for emotion, phrase_list in phrases["comfort_phrases"].items():
                    if phrase_list:  # Only process if list is not empty
                        if emotion not in self.categories["comfort"]:
                            self.categories["comfort"][emotion] = []
                        self.categories["comfort"][emotion].extend(phrase_list)
                    
            # Map old category names to new ones
            category_mapping = {
                "appreciation_phrases": "appreciation",
                "greeting_phrases": "greetings",
                "empathy_phrases": "empathy",
                "encouragement_phrases": "encouragement",
                "presence_phrases": "presence",
                "validation_phrases": "validation",
                "gentle_challenge_phrases": "gentle_challenge",
                "reframing_phrases": "reframing",
                "connection_deepening_phrases": "connection_deepening",
                "light_conversation_phrases": "light_conversation",
                "closing_phrases": "closing",
                "reassurance_phrases": "reassurance",
                "personal_disclosure_phrases": "personal_disclosure",
                "gentle_humor_phrases": "humor",
                "transition_phrases": "transitions",
                "concise_response_phrases": "concise_responses",
                "brief_comfort_phrases": "brief_comfort",
                "general_phrases": "general"
            }
            
            # Load each category if it exists
            for old_name, new_name in category_mapping.items():
                if old_name in phrases and phrases[old_name]:  # Check if exists and not empty
                    if new_name not in self.categories:
                        self.categories[new_name] = []
                    self.categories[new_name].extend(phrases[old_name])

            # Handle relationship stage phrases separately since they're nested
            if "relationship_stage_phrases" in phrases and phrases["relationship_stage_phrases"]:
                if "relationship_stages" not in self.categories:
                    self.categories["relationship_stages"] = {}
                self.categories["relationship_stages"].update(phrases["relationship_stage_phrases"])
        except Exception as e:
            print(f"Error loading legacy phrases: {e}")
            # Continue with default phrases even if there's an error