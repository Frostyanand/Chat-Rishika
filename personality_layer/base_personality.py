# personality_layer/base_personality.py
import random
import datetime
from .response_templates.default_responses import DefaultResponses
from .response_templates.mood_responses import MoodResponses
from .utils.phrase_bank import PhraseBank

class BasePersonality:
    def __init__(self, name="Elysia"):
        self.name = name
        self.traits = {
            "empathy": 0.9,            # High empathy
            "supportive": 0.9,         # Very supportive
            "respectful": 1.0,         # Always respectful
            "formality": 0.3,          # Mostly casual, slightly formal
            "warmth": 0.8,             # Very warm in tone
            "patience": 0.9,           # Very patient
            "humor": 0.5,              # Moderate humor when appropriate
            "curiosity": 0.7,          # Curious about the user
            "optimism": 0.6,           # Moderately optimistic (not toxic positivity)
            "adaptability": 0.8        # Adapts well to user moods
        }
        
        # Initialize the phrase dictionaries
        self._init_phrase_dictionaries()
        
        # Initialize phrase bank from utils
        self.__init_phrase_bank()
        
        # Response history to avoid repetition
        self.recent_responses = []
        self.max_recent_responses = 10
        
        # Keywords for mood detection
        self.mood_keywords = {
            "sad": ["sad", "upset", "depressed", "unhappy", "down", "miserable", "heartbroken", "disappointed", "grief", "crying", "tears"],
            "happy": ["happy", "glad", "excited", "pleased", "joy", "delighted", "content", "grateful", "wonderful", "amazing", "fantastic"],
            "angry": ["angry", "frustrated", "annoyed", "mad", "furious", "irritated", "upset", "outraged", "offended", "irked"],
            "anxious": ["anxious", "worried", "nervous", "stressed", "overwhelmed", "scared", "frightened", "panicked", "uneasy", "afraid"],
            "tired": ["tired", "exhausted", "sleepy", "fatigued", "drained", "weary", "spent", "burned out", "worn out"],
            "lonely": ["lonely", "alone", "isolated", "abandoned", "forgotten", "neglected", "rejected"],
            "hopeful": ["hopeful", "optimistic", "looking forward", "positive", "encouraged", "motivated", "inspired"],
            "confused": ["confused", "unsure", "uncertain", "puzzled", "perplexed", "lost", "bewildered"]
        }
        
        # Tracks conversation context
        self.conversation_context = {
            "current_topic": None,
            "emotional_trajectory": [],  # Tracks emotional shifts
            "depth_level": "surface",    # Current depth level of conversation
            "last_response_type": None,  # Type of last response given
            "themes_discussed": set(),   # Major themes discussed in conversation
            "questions_asked": [],       # Questions asked by Elysia
            "follow_up_needed": False,   # Whether a follow-up question is appropriate
            "mental_health_concerns": [],
            "support_level_provided": 0
        }
        
    def _init_phrase_dictionaries(self):
        """Initialize all the phrase dictionaries needed for legacy support"""
        # Define all phrase dictionaries that will be used in legacy_phrases
        self.comfort_phrases = {
            "sadness": [
                "I'm here with you through this sadness.",
                "It's okay to feel sad. Your feelings are valid.",
                "I'm sorry you're feeling sad right now."
            ],
            "anxiety": [
                "Let's take a deep breath together.",
                "Anxiety is tough, but you're not alone in it.",
                "I'm here with you through these anxious feelings."
            ],
            "general": [
                "I'm here with you.",
                "Your feelings are valid.",
                "I'm listening and I care about what you're going through."
            ]
        }
        
        self.appreciation_phrases = [
            "Thank you for sharing that with me.",
            "I appreciate your openness.",
            "Thanks for talking with me today."
        ]
        
        self.greeting_phrases = [
            "Hello there!",
            "Hi! How are you today?",
            "Hey, good to see you!"
        ]
        
        self.empathy_phrases = [
            "I understand that must be difficult.",
            "That sounds challenging.",
            "I can see why you'd feel that way."
        ]
        
        self.encouragement_phrases = [
            "You've got this.",
            "I believe in you.",
            "One step at a time."
        ]
        
        self.presence_phrases = [
            "I'm here with you.",
            "I'm listening.",
            "You're not alone in this."
        ]
        
        self.validation_phrases = [
            "Your feelings are completely valid.",
            "What you're experiencing makes sense.",
            "It's okay to feel how you feel."
        ]
        
        self.gentle_challenge_phrases = [
            "I wonder if there's another perspective we could explore?",
            "What if we looked at this differently?",
            "Have you considered another possibility?"
        ]
        
        self.reframing_phrases = [
            "Maybe we could think about this another way.",
            "Let's try to reframe this situation.",
            "There might be another way to look at this."
        ]
        
        self.connection_deepening_phrases = [
            "I'd love to hear more about that.",
            "Could you tell me more?",
            "What else do you think about this?"
        ]
        
        self.light_conversation_phrases = [
            "That's interesting!",
            "Tell me more about your day.",
            "What do you enjoy most about that?"
        ]
        
        self.closing_phrases = [
            "I'm here whenever you need to talk.",
            "Feel free to reach out anytime.",
            "I'll be thinking of you."
        ]
        
        self.reassurance_phrases = [
            "Things will get better.",
            "This feeling won't last forever.",
            "You've gotten through difficult times before."
        ]
        
        self.personal_disclosure_phrases = [
            "I'm designed to be here for you.",
            "My purpose is to support you.",
            "I'm focused on helping you feel heard."
        ]
        
        self.transition_phrases = [
            "On another note,",
            "By the way,",
            "Shifting gears a bit,"
        ]
        
        self.concise_response_phrases = [
            "I understand.",
            "I see.",
            "That makes sense."
        ]
        
        self.brief_comfort_phrases = [
            "I'm here for you.",
            "That sounds tough.",
            "I'm listening."
        ]
        
        self.relationship_stage_phrases = {
            "new": [
                "I'm glad we're getting to know each other.",
                "I'm looking forward to our conversations.",
                "It's nice to meet you."
            ],
            "familiar": [
                "It's always good to chat with you.",
                "I enjoy our conversations.",
                "It's nice talking with you again."
            ],
            "close": [
                "I value our connection.",
                "I appreciate how open you are with me.",
                "It means a lot that you share with me."
            ]
        }
        
    def __init_phrase_bank(self):
        """Initialize the phrase bank with both new and legacy phrases"""
        # Initialize with core phrases from utils
        self.phrase_bank = PhraseBank()
        
        # Load legacy phrases into phrase bank
        legacy_phrases = {
            "comfort": self.comfort_phrases,
            "appreciation": self.appreciation_phrases,
            "greetings": self.greeting_phrases,
            "empathy": self.empathy_phrases,
            "encouragement": self.encouragement_phrases,
            "presence": self.presence_phrases,
            "validation": self.validation_phrases,
            "gentle_challenge": self.gentle_challenge_phrases,
            "reframing": self.reframing_phrases,
            "connection_deepening": self.connection_deepening_phrases,
            "light_conversation": self.light_conversation_phrases,
            "closing": self.closing_phrases,
            "reassurance": self.reassurance_phrases,
            "personal_disclosure": self.personal_disclosure_phrases,
            "transition": self.transition_phrases,
            "concise_response": self.concise_response_phrases,
            "brief_comfort": self.brief_comfort_phrases,
            "relationship_stage": self.relationship_stage_phrases
        }
        
        # Add legacy phrases to phrase bank
        self.phrase_bank.load_legacy_phrases(legacy_phrases)
        
    def detect_mood(self, message):
        """Detect the user's mood based on keywords in their message"""
        # Ensure lower case for better matching
        message = message.lower()
        mood_scores = {}
        
        # Simple keyword matching
        for mood, keywords in self.mood_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in message:
                    score += 1
            if score > 0:
                mood_scores[mood] = score
        
        # Get the mood with the highest score
        if mood_scores:
            detected_mood = max(mood_scores, key=mood_scores.get)
        else:
            detected_mood = "neutral"
        
        # Store detected mood in conversation context
        try:
            # Try to track mood history if we have personality_factory
            if hasattr(self, 'personality_factory') and self.personality_factory:
                self.personality_factory.add_to_long_term_memory("mood_history", {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "mood": detected_mood,
                    "message": message
                })
        except (AttributeError, Exception) as e:
            # If personality_factory is missing or there's another error, just continue
            pass
            
        return detected_mood
    
    def detect_topics(self, message):
        """Detect potential conversation topics from user message"""
        message = message.lower()
        
        # Basic topic detection - could be enhanced with NLP in a more advanced implementation
        topics = {
            "work": ["work", "job", "career", "office", "boss", "colleague", "project"],
            "relationships": ["relationship", "girlfriend", "boyfriend", "partner", "wife", "husband", "marriage", "dating", "love"],
            "family": ["family", "parents", "mom", "dad", "mother", "father", "sister", "brother", "child", "children", "kids"],
            "health": ["health", "sick", "illness", "doctor", "hospital", "pain", "injury", "diet", "exercise"],
            "mental_health": ["anxiety", "depression", "therapy", "therapist", "stress", "mental health", "medication", "psychiatrist"],
            "hobbies": ["hobby", "hobbies", "game", "gaming", "read", "reading", "music", "movie", "art", "drawing", "painting", "sport"],
            "education": ["school", "college", "university", "class", "course", "degree", "study", "student", "learning", "teacher", "professor"],
            "future": ["future", "plan", "dream", "goal", "ambition", "hope", "aspiration"],
            "past": ["past", "memory", "childhood", "remember", "regret", "nostalgia", "used to"],
            "identity": ["identity", "self", "who I am", "purpose", "meaning", "life", "existence", "philosophical"]
        }
        
        found_topics = []
        for topic, keywords in topics.items():
            if any(keyword in message for keyword in keywords):
                found_topics.append(topic)
                # Add to themes discussed
                self.conversation_context["themes_discussed"].add(topic)
        
        # Update current topic if a new one is found
        if found_topics:
            self.conversation_context["current_topic"] = found_topics[0]
            
            # Update depth level based on topic
            depth_topics = {"mental_health", "identity", "past", "future", "relationships"}
            if any(topic in depth_topics for topic in found_topics):
                self.conversation_context["depth_level"] = "personal"
                
        return found_topics
    
    def detect_follow_up_needs(self, message, previous_response):
        """Determine if a follow-up is needed based on user's response to a question"""
        if not previous_response:
            return False
            
        # Check if previous response ended with a question
        previous_was_question = any(previous_response.strip().endswith(q) for q in ["?", "."]) and \
                               any(q in previous_response for q in ["how", "what", "why", "when", "where", "who", "could you", "can you", "would you"])
        
        # If we asked a question but got a short answer, we should follow up
        if previous_was_question and len(message.split()) < 10:
            return True
            
        # If the user asks "what about you" or similar, we should respond personally
        if any(phrase in message.lower() for phrase in ["what about you", "how about you", "and you", "your thoughts"]):
            return True
            
        return False
    
    def create_layered_response(self, message, user_data=None, previous_response=None):
        """Create a layered response with improved mental health awareness and emotional trend handling"""
        # Detect mood and topics
        mood = self.detect_mood(message)
        topics = self.detect_topics(message)
        
        # Get emotional trend data
        emotional_trend = None
        if user_data and "user_id" in user_data:
            emotional_trend = self.personality_factory.personality_adaptation.detect_emotional_trends(user_data["user_id"])
        
        # Check if follow-up is needed
        is_follow_up = self.detect_follow_up_needs(message, previous_response)
        
        # Check if we're seeing persistent emotions
        persistent_emotion = False
        if emotional_trend and emotional_trend.get("persistent_negative", False):
            persistent_emotion = True
        
        # Check if we've been repeating the same type of response
        repeating = len(self.conversation_context["emotional_trajectory"]) >= 3 and \
                   len(set(self.conversation_context["emotional_trajectory"][-3:])) == 1
        
        # Personalize if user data is available
        user_name = user_data.get("name", "there") if user_data else "there"
        
        # Use the new layered response approach from the phrase bank
        primary_categories = []
        secondary_categories = []
        
        # Determine which phrase categories to use based on mood, trends, and context
        if persistent_emotion and mood in ["sad", "angry", "anxious", "lonely"]:
            # For persistent negative emotions, focus on deeper support
            primary_categories.extend(["deep_empathy", "emotional_support"])
            secondary_categories.extend(["validation", "encouragement", "coping_strategies"])
            
            # Get escalated comfort response if available
            comfort_response = self.personality_factory.personality_adaptation.get_comfort_escalation_response(
                user_data["user_id"], mood
            ) if user_data and "user_id" in user_data else None
            
        elif mood in ["sad", "angry", "anxious", "lonely"]:
            primary_categories.append("empathy")
            if random.random() < 0.7:  # 70% chance
                primary_categories.append("comfort")
            secondary_categories.extend(["validation", "encouragement"])
            
        elif mood in ["happy", "excited"]:
            primary_categories.append("celebration")
            if emotional_trend and emotional_trend.get("trend") == "improving":
                secondary_categories.append("progress_recognition")
            secondary_categories.extend(["light_humor", "curiosity"])
            
        else:
            # For neutral moods, check emotional trend
            if emotional_trend:
                if emotional_trend.get("trend") == "improving":
                    secondary_categories.extend(["subtle_encouragement", "progress_recognition"])
                elif emotional_trend.get("trend") == "declining":
                    secondary_categories.extend(["gentle_support", "casual_check_in"])
            primary_categories.append("curiosity")
            secondary_categories.extend(["transitions", "casual_check_in"])
        
        # For deep conversations, prioritize different kinds of phrases
        if self.conversation_context["depth_level"] in ["personal", "vulnerable"]:
            secondary_categories.append("validation")
        
        # For repeated emotional states, add variety
        if repeating:
            secondary_categories.append("transitions")
            if random.random() < 0.3 and mood not in ["sad", "angry", "anxious"]:  # 30% chance, avoid humor for negative emotions
                secondary_categories.append("light_humor")
        
        # Add content based on the message context and emotional trend
        content = self._generate_content_response(mood, topics, message, user_data)
        
        # Check for mental health concerns with improved trend awareness
        mental_health_concerns = self.personality_factory.personality_adaptation.detect_mental_health_concerns(message)
        
        if mental_health_concerns["type"] and mental_health_concerns["confidence"] > 0.6:
            # Add to conversation context
            self.conversation_context["mental_health_concerns"].append(mental_health_concerns)
            
            # Get appropriate mental health response considering persistence
            mental_health_response = self.personality_factory.personality_adaptation.get_mental_health_response(
                user_data["user_id"], 
                mental_health_concerns["type"]
            ) if user_data and "user_id" in user_data else None
            
            if mental_health_response:
                # Use mental health response as primary response
                content = mental_health_response
                
                # Adjust response categories for empathetic, supportive tone
                primary_categories = ["deep_empathy", "support"]
                secondary_categories = ["validation", "gentle_encouragement"]
                
                # Update support level
                self.conversation_context["support_level_provided"] += 1
        
        # Get opening phrases with awareness of emotional trends
        opening = self.phrase_bank.get_layered_response(
            primary_categories=primary_categories,
            secondary_categories=secondary_categories,
            max_phrases=2
        )
        
        # Add follow-up based on emotional context
        add_follow_up = random.random() < (0.6 if not persistent_emotion else 0.8)  # Higher chance for persistent emotions
        follow_up = ""
        if add_follow_up and not is_follow_up:
            follow_up = self._generate_follow_up(mood, topics, is_follow_up, user_data)
        
        # Build the final response with improved flow
        response_parts = []
        
        if opening:
            response_parts.append(opening)
        
        if content:
            response_parts.append(content)
        
        # Only add follow-up for appropriate situations
        if follow_up and (not mental_health_concerns["type"] or mental_health_concerns["severity"] < 0.7):
            response_parts.append(follow_up)
        
        # Filter out empty parts and join
        response_parts = [p for p in response_parts if p]
        response = " ".join(response_parts)
        
        # Keep track of this response
        self._add_to_response_history(response)
        self.conversation_context["last_response_type"] = (
            "mental_health_support" if mental_health_concerns["type"]
            else "persistent_emotion_support" if persistent_emotion
            else "layered"
        )
        
        return response

    def _generate_emotional_acknowledgment(self, mood, user_name="there", repeating=False):
        """Generate an emotional acknowledgment based on the detected mood"""
        # If we've been repeating the same emotional acknowledgment, use lighter versions
        if repeating:
            # Use brief acknowledgments to avoid repetition
            if mood == "sad":
                return self.phrase_bank.get_phrase("empathy")
            elif mood == "happy":
                return self.phrase_bank.get_phrase("celebration")
            elif mood == "angry":
                return self.phrase_bank.get_phrase("validation")
            elif mood == "anxious":
                return self.phrase_bank.get_phrase("comfort")
            else:
                return ""
        
        # Standard emotional acknowledgments
        if mood == "sad":
            acknowledgments = [
                self.phrase_bank.get_phrase("empathy"),
                self.phrase_bank.get_phrase("comfort")
            ]
            return random.choice(acknowledgments)
        elif mood == "happy":
            return self.phrase_bank.get_phrase("celebration")
        elif mood == "angry":
            acknowledgments = [
                self.phrase_bank.get_phrase("validation"),
                self.phrase_bank.get_phrase("empathy")
            ]
            return random.choice(acknowledgments)
        elif mood == "anxious":
            acknowledgments = [
                self.phrase_bank.get_phrase("comfort"),
                self.phrase_bank.get_phrase("validation")
            ]
            return random.choice(acknowledgments)
        else:
            # For neutral or other moods, more casual acknowledgment
            return ""
    
    def _generate_content_response(self, mood, topics, message, user_data):
        """Generate the main content of the response based on mood and topics"""
        # Simplified content responses - less verbose, more natural
        if mood == "sad":
            responses = [
                "Everyone feels down sometimes.",
                "Taking time for yourself can help when you're feeling low.",
                "It's okay to not be okay.",
                "Would talking about it some more help?"
            ]
            return random.choice(responses)
            
        elif mood == "happy":
            responses = [
                "That's really great to hear!",
                "Awesome! What's been going well?",
                "Nice! Sounds like things are going well.",
                "That's fantastic."
            ]
            return random.choice(responses)
            
        elif mood == "angry":
            responses = [
                "That would frustrate me too.",
                "Sounds like you have good reason to be upset.",
                "Have you been able to address it directly?",
                "Sometimes talking it through helps cool things down."
            ]
            return random.choice(responses)
            
        elif mood == "anxious":
            responses = [
                "It's normal to worry sometimes.",
                "What's got you feeling anxious?",
                "Taking some deep breaths can help in the moment.",
                "Anxiety is tough to deal with."
            ]
            return random.choice(responses)
            
        elif mood == "grateful":
            responses = [
                "It's great when we can appreciate those moments.",
                "Those positive experiences are worth cherishing.",
                "That's really nice.",
                "Sounds like a meaningful experience."
            ]
            return random.choice(responses)
            
        # Topic-based responses - more concise and conversational
        if topics:
            topic = topics[0]
            if topic == "work":
                return "Work can be a lot sometimes. How's it affecting you?"
            elif topic == "relationships":
                return "Relationships definitely have their ups and downs."
            elif topic == "family":
                return "Family stuff can get complicated. How are you handling it?"
            elif topic == "health":
                return "Health concerns can be stressful. Are you taking care of yourself?"
            elif topic == "mental_health":
                return "Mental health is just as important as physical health."
            elif topic == "hobbies":
                return "Having activities you enjoy is so important."
            elif topic == "education":
                return "Learning new things keeps life interesting."
            elif topic == "future":
                return "The future can be both exciting and nerve-wracking."
            elif topic == "past":
                return "Our past experiences definitely shape us."
            elif topic == "identity":
                return "Understanding ourselves is an ongoing journey."
        
        # Default response if no specific mood or topic response is triggered
        general_responses = [
            "Tell me more?",
            "What do you think about that?",
            "How does that affect you?",
            "I'm curious to hear more.",
            "What happened next?"
        ]
        return random.choice(general_responses)
    
    def _add_personalization(self, user_data, mood, topics, is_follow_up):
        """Add personalized elements based on user history and preferences"""
        if not user_data:
            return ""
            
        # Check for shared interests - more natural and brief
        if topics and any(topic == "hobbies" for topic in topics) and user_data.get("interests"):
            interest = random.choice(user_data.get("interests", []))
            return f"Since you enjoy {interest}, that might be a good outlet."
            
        # Reference previous emotional states for growth moments - more natural
        if mood in ["happy", "hopeful"] and any(past_mood in ["sad", "anxious", "angry"] 
                                             for past_mood in self.conversation_context["emotional_trajectory"][:-1]):
            return "It's nice to hear you sounding more positive."
            
        # Only add deeper personalization in appropriate contexts
        if self.conversation_context["depth_level"] not in ["personal", "vulnerable"]:
            return ""
            
        return ""
    
    def _generate_follow_up(self, mood, topics, is_follow_up, user_data):
        """Generate an appropriate follow-up question or prompt"""
        # Stop asking follow-ups if we just did
        if is_follow_up:
            return ""
            
        # Different follow-ups for different moods
        if mood == "sad":
            follow_ups = [
                "What might help you feel better?",
                "Has anything helped in similar situations before?",
                "Do you want to talk more about it?"
            ]
            return random.choice(follow_ups)
            
        elif mood == "happy":
            follow_ups = [
                "What's been the best part?",
                "Anything else exciting happening?",
                "That's great! What's next?"
            ]
            return random.choice(follow_ups)
            
        elif mood == "angry":
            follow_ups = [
                "What do you think would help resolve this?",
                "Have you talked to them about how you feel?",
                "What would make the situation better?"
            ]
            return random.choice(follow_ups)
            
        elif mood == "anxious":
            follow_ups = [
                "What's your biggest concern right now?",
                "Is there anything that might help ease your mind?",
                "What's the first step you could take?"
            ]
            return random.choice(follow_ups)
            
        # More specific follow-ups based on topic
        if topics:
            topic = topics[0]
            if topic == "work":
                follow_ups = [
                    "How's the work-life balance going?",
                    "What's the most challenging part?",
                    "Any projects you're excited about?"
                ]
            elif topic in ["relationships", "family"]:
                follow_ups = [
                    "How have things been between you lately?",
                    "What's working well in the relationship?",
                    "What would make it better?"
                ]
            elif topic in ["health", "mental_health"]:
                follow_ups = [
                    "Have you found anything that helps?",
                    "Are you getting the support you need?",
                    "What's one small thing you could do for yourself today?"
                ]
            elif topic == "hobbies":
                follow_ups = [
                    "What do you enjoy most about it?",
                    "How did you get started with that?",
                    "Any new interests lately?"
                ]
            elif topic in ["future", "past", "identity"]:
                follow_ups = [
                    "Where do you see things going?",
                    "What's been most influential for you?",
                    "What matters most to you?"
                ]
            else:
                # General follow-ups - more casual and brief
                follow_ups = [
                    "What's been on your mind lately?",
                    "How have things been going?",
                    "What else is happening?",
                    "Anything else you want to talk about?"
                ]
                
            return random.choice(follow_ups)
        
        # Default follow-ups if no specific topic
        default_follow_ups = [
            "What else has been going on?",
            "How have you been otherwise?",
            "Anything else on your mind?",
            "What's new with you?"
        ]
        
        return random.choice(default_follow_ups)
    
    def _add_to_response_history(self, response):
        """Add response to history and maintain max length"""
        self.recent_responses.append(response)
        if len(self.recent_responses) > self.max_recent_responses:
            self.recent_responses.pop(0)
    
    def generate_response(self, message, user_data=None):
        """
        Generate a response based on the user's message and personality traits
        This is the main entry point for response generation
        """
        # Get the most recent response as context if available
        previous_response = self.recent_responses[-1] if self.recent_responses else None
        
        # Create a layered response
        response = self.create_layered_response(message, user_data, previous_response)
        
        return response
    
    def adapt_to_user(self, user_preferences):
        """Adapt personality traits based on user preferences and interaction history"""
        if user_preferences:
            # Adjust traits based on user preferences
            for trait, value in user_preferences.items():
                if trait in self.traits:
                    # Gradually adapt towards user preference
                    self.traits[trait] = (self.traits[trait] * 0.8) + (value * 0.2)
