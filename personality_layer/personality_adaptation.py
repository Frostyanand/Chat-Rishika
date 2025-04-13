# personality_layer/personality_adaptation.py
import datetime
import re
from collections import Counter
import math
from .utils.emotion_analysis import EmotionAnalyzer

class PersonalityAdaptation:
    def __init__(self, personality_factory):
        self.personality_factory = personality_factory
        self.emotion_analyzer = EmotionAnalyzer()
        
        # Define patterns for detecting user preferences
        self.formality_patterns = {
            "formal": [r"speak\s+formal", r"more\s+formal", r"professional", r"less\s+casual"],
            "casual": [r"speak\s+casual", r"more\s+casual", r"relaxed", r"less\s+formal", r"friendly"]
        }
        
        self.humor_patterns = {
            "increase": [r"more\s+humor", r"more\s+jokes", r"funnier", r"lighten\s+up", r"make\s+me\s+laugh"],
            "decrease": [r"less\s+humor", r"fewer\s+jokes", r"more\s+serious", r"not\s+funny"]
        }
        
        self.empathy_patterns = {
            "increase": [r"more\s+understanding", r"more\s+empathy", r"be\s+kinder", r"compassionate"],
            "decrease": [r"less\s+empathy", r"don't\s+sympathize", r"more\s+neutral", r"less\s+emotional"]
        }
        
        self.response_length_patterns = {
            "increase": [r"longer\s+responses", r"more\s+detail", r"elaborate", r"tell\s+me\s+more"],
            "decrease": [r"shorter\s+responses", r"be\s+brief", r"concise", r"less\s+wordy", r"too\s+long"]
        }
        
        # Patterns for detecting emotions - now using EmotionAnalyzer for more nuanced analysis
        self.emotion_patterns = {
            "happiness": [r"happy", r"joy", r"delighted", r"excited", r"pleased", r"grateful"],
            "sadness": [r"sad", r"upset", r"depressed", r"miserable", r"heartbroken", r"devastated"],
            "anger": [r"angry", r"mad", r"furious", r"annoyed", r"frustrated", r"irritated"],
            "fear": [r"afraid", r"scared", r"terrified", r"anxious", r"worried", r"nervous"],
            "surprise": [r"surprised", r"shocked", r"amazed", r"astonished", r"stunned"],
            "trust": [r"trust", r"believe", r"faith", r"confident", r"assured"],
            "disgust": [r"disgust", r"revolted", r"grossed out", r"nauseated", r"repelled"],
            "anticipation": [r"looking forward", r"excited for", r"anticipate", r"can't wait", r"eager"]
        }
        
        # Patterns for detecting interests with improved accuracy
        self.interest_patterns = [
            (r"I\s+(?:love|enjoy|like|adore)\s+([\w\s]+)", 1),
            (r"I'm\s+(?:passionate|enthusiastic)\s+about\s+([\w\s]+)", 1),
            (r"I'm\s+(?:really|very|quite)\s+into\s+([\w\s]+)", 1),
            (r"My\s+hobby\s+(?:is|involves)\s+([\w\s]+)", 1),
            (r"I\s+(?:spend|dedicate)\s+(?:my|a lot of|most)\s+(?:time|energy)\s+(?:to|on)\s+([\w\s]+)", 1),
            (r"I'm\s+interested\s+in\s+([\w\s]+)", 1),
            (r"I\s+work\s+(?:as|in)\s+([\w\s]+)", 1),
            (r"I've\s+been\s+(?:doing|learning|studying|practicing)\s+([\w\s]+)", 1)
        ]
        
        # Patterns for detecting important dates with improved accuracy
        self.date_patterns = [
            (r"(?:my|our)\s+(?:birthday|anniversary|special day)\s+is\s+(?:on\s+)?([\w\s\-\.]+)", 1),
            (r"([\w\s\-\.]+)\s+is\s+(?:my|our)\s+(?:birthday|anniversary|special day)", 1),
            (r"remember\s+(?:that\s+)?([\w\s\-\.]+)\s+is\s+([\w\s\-\.]+)", 2, 1),
            (r"(?:mark|save|note|circle)\s+(?:the\s+date|down)[\w\s]*?([\w\s\-\.]+)", 1),
            (r"I\s+(?:get|become|turn|am|will be)\s+(\d+)(?:\s+years\s+old)?\s+on\s+([\w\s\-\.]+)", 2)
        ]
        
        # Personal disclosure patterns for depth detection
        self.personal_disclosure_patterns = [
            # High disclosure patterns (vulnerable topics)
            (r"I've\s+never\s+told\s+anyone", 0.9),
            (r"can\s+I\s+tell\s+you\s+something\s+personal", 0.9),
            (r"I\s+feel\s+(?:embarrassed|ashamed|scared)\s+to\s+say", 0.9),
            (r"I\s+struggle\s+with", 0.8),
            (r"(?:my|I've\s+had\s+a)\s+trauma", 0.9),
            (r"I'm\s+(?:afraid|scared|terrified)\s+of", 0.7),
            (r"I\s+don't\s+know\s+if\s+I\s+can", 0.6),
            (r"I\s+(?:wish|hope|dream)\s+(?:I|to)", 0.6),
            
            # Medium disclosure patterns (personal but less vulnerable)
            (r"I\s+feel\s+(?:like|that)", 0.5),
            (r"I\s+think\s+(?:about|that)", 0.4),
            (r"to\s+be\s+honest", 0.5),
            (r"honestly", 0.4),
            (r"between\s+you\s+and\s+me", 0.6),
            (r"just\s+between\s+us", 0.6),
            (r"I've\s+been\s+thinking", 0.4),
            
            # Low disclosure patterns (everyday sharing)
            (r"I\s+(?:like|enjoy|love)\s+to", 0.3),
            (r"my\s+(?:day|morning|evening)\s+was", 0.2),
            (r"I\s+(?:went|visited|saw)", 0.2)
        ]
        
        # Emotional support detection patterns
        self.emotional_support_patterns = [
            r"thank\s+you\s+for\s+(?:listening|understanding|being\s+there|your\s+support)",
            r"you\s+(?:really|always)\s+help",
            r"I\s+feel\s+(?:better|calmer|more\s+relaxed|understood)\s+(?:now|after\s+talking)",
            r"talking\s+(?:to|with)\s+you\s+(?:helps|makes\s+me\s+feel\s+better)",
            r"I\s+appreciate\s+your",
            r"you're\s+(?:really|so)\s+(?:helpful|supportive|understanding)",
            r"that\s+(?:helps|made\s+me\s+feel\s+better)",
            r"you\s+(?:understand|get)\s+me"
        ]
        
        # Enhanced comfort response levels based on emotional state persistence
        self.comfort_escalation_levels = {
            # For sadness
            "sadness": [
                "I notice you're feeling down. It's okay to feel sad sometimes.",
                "I can see this sadness has been with you for a while. Remember that all emotions are temporary, even when they feel permanent.",
                "You've been experiencing sadness consistently. While I'm here to listen, please consider reaching out to a trusted friend or professional if it becomes overwhelming.",
                "I'm concerned about how persistent your sadness has been. Please consider speaking with a mental health professional who can offer proper support.",
                "Your well-being matters deeply. Please consider reaching out to a crisis helpline if you're feeling overwhelmed: Mental Health Helpline: 988 or text HOME to 741741."
            ],
            
            # For anxiety
            "anxiety": [
                "I notice you seem anxious. Taking deep breaths can sometimes help in the moment.",
                "Your anxiety seems to be recurring. Remember that grounding techniques like naming 5 things you can see might help.",
                "I've noticed consistent anxiety in our conversations. While I'm here to listen, professional support might offer more effective strategies.",
                "Your anxiety seems quite persistent. A mental health professional could provide tools specifically tailored to your experience.",
                "I'm concerned about your ongoing anxiety. Please consider reaching out to a crisis helpline if it becomes overwhelming: Mental Health Helpline: 988 or text HOME to 741741."
            ],
            
            # For anger
            "anger": [
                "I can understand why you'd feel frustrated by this situation.",
                "I notice anger has been coming up frequently. Sometimes it can be helpful to step back briefly from what's triggering it.",
                "Your anger seems to be a recurring theme. While I'm here to listen, addressing the root causes might require additional support.",
                "I notice your anger has been persistent. A professional might help provide strategies for managing these intense feelings.",
                "I'm concerned about how these feelings are affecting you. Please consider speaking with someone who specializes in helping people process anger."
            ]
        }

        # Enhanced mental health keywords
        self.mental_health_indicators = {
            "depression": {
                "explicit": ["depressed", "depression", "depressing"],
                "implicit": ["worthless", "hopeless", "numb", "empty", "tired all the time"],
                "behavioral": ["cant sleep", "no energy", "no motivation", "not eating"]
            }
        }

        # Mental health response escalation
        self.mental_health_responses = {
            "depression": [
                # Level 1 - Initial acknowledgment
                "I hear you. Depression is really difficult to deal with. Would you like to talk more about what you're experiencing?",
                
                # Level 2 - Gentle support 
                "I understand this is hard. Have you been able to talk to anyone else about how you're feeling?",
                
                # Level 3 - Resource suggestion
                "Your feelings are valid. Have you considered talking to a mental health professional? They're trained to help with depression.",
                
                # Level 4 - Direct support encouragement
                "I care about your wellbeing. Depression is serious, and you deserve support. Would you be open to reaching out to a counselor or crisis helpline?"
            ]
        }

        self.adaptation_weights = {
            'emotional_resonance': 0.4,
            'conversation_depth': 0.3,
            'user_engagement': 0.3
        }
        self.emotion_patterns = {}

    def analyze_message(self, message):
        """Analyze a user message for emotional content, disclosure level, interests, etc."""
        # Basic implementation - in a real system this would use more sophisticated NLP
        analysis = {
            "emotion": "neutral",
            "emotion_intensity": 0.3,  # Default medium-low intensity
            "disclosure_level": 0.2,   # Default low disclosure
            "detected_interests": [],
            "detected_dates": [],
            "personal_info": {}
        }
        
        # Very basic emotion detection
        emotion_keywords = {
            "joy": ["happy", "glad", "excited", "wonderful", "joy", "fantastic", "great", "lovely", "pleased"],
            "sadness": ["sad", "unhappy", "depressed", "miserable", "down", "blue", "upset", "heartbroken"],
            "anger": ["angry", "mad", "furious", "annoyed", "irritated", "frustrated", "outraged"],
            "fear": ["afraid", "scared", "terrified", "fearful", "worried", "anxious", "nervous"],
            "anxiety": ["anxious", "stressed", "overwhelmed", "panicked", "tense", "restless", "worried"],
            "grief": ["grief", "loss", "mourning", "sorrow", "bereavement", "devastated"],
            "overwhelm": ["overwhelmed", "swamped", "buried", "overloaded", "exhausted", "too much"],
            "loneliness": ["lonely", "alone", "isolated", "abandoned", "solitary", "disconnected"],
            "disappointment": ["disappointed", "letdown", "disillusioned", "disheartened", "failed"],
            "confusion": ["confused", "puzzled", "perplexed", "unsure", "uncertain", "disoriented"]
        }
        
        # Check for emotion keywords
        message_lower = message.lower()
        detected_emotions = {}
        
        for emotion, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    # Check if it's part of a word or a complete word
                    word_boundary_pattern = f"\\b{keyword}\\b"
                    import re
                    if re.search(word_boundary_pattern, message_lower):
                        detected_emotions[emotion] = detected_emotions.get(emotion, 0) + 1
        
        # Determine dominant emotion
        if detected_emotions:
            dominant_emotion = max(detected_emotions.items(), key=lambda x: x[1])
            analysis["emotion"] = dominant_emotion[0]
            
            # Calculate intensity based on count and message length
            word_count = len(message.split())
            intensity = min(0.9, (dominant_emotion[1] / max(1, word_count / 10)) * 0.5 + 0.4)
            analysis["emotion_intensity"] = intensity
            
        # Estimate disclosure level based on message characteristics
        # - Length (longer messages often have more disclosure)
        # - Personal pronouns (I, me, my)
        # - Emotional content
        # - Sharing of personal details
        
        word_count = len(message.split())
        personal_pronouns = ["i", "me", "my", "mine", "myself"]
        pronoun_count = sum(1 for word in message_lower.split() if word in personal_pronouns)
        
        # Calculate disclosure based on message length and pronoun density
        length_factor = min(0.5, word_count / 100)  # Max 0.5 for length
        pronoun_factor = min(0.4, pronoun_count / max(1, word_count) * 2)  # Max 0.4 for pronouns
        emotion_factor = analysis["emotion_intensity"] * 0.3  # Max 0.3 for emotion
        
        analysis["disclosure_level"] = length_factor + pronoun_factor + emotion_factor
        
        # Very basic interest detection (in a real system, this would use entity recognition)
        common_interests = [
            "music", "books", "movies", "travel", "sports", "cooking", "reading",
            "writing", "photography", "art", "gaming", "dancing", "programming"
        ]
        
        for interest in common_interests:
            if interest in message_lower:
                analysis["detected_interests"].append(interest)
                
        # Very basic date detection (in a real system, this would use date entity extraction)
        # Look for mentions of dates or events
        date_patterns = [
            (r"birthday.*?(\w+ \d+|\d+ \w+)", "birthday"),
            (r"anniversary.*?(\w+ \d+|\d+ \w+)", "anniversary"),
            (r"vacation.*?(\w+ \d+|\d+ \w+)", "vacation")
        ]
        
        import re
        for pattern, description in date_patterns:
            matches = re.findall(pattern, message_lower)
            for match in matches:
                analysis["detected_dates"].append({
                    "date": match,
                    "description": description
                })
                
        # Very basic personal info detection
        name_match = re.search(r"my name is (\w+)", message_lower)
        if name_match:
            analysis["personal_info"]["name"] = name_match.group(1)
            
        location_match = re.search(r"i live in (\w+)", message_lower)
        if location_match:
            analysis["personal_info"]["location"] = location_match.group(1)
            
        job_match = re.search(r"i work as an? (\w+)", message_lower)
        if job_match:
            analysis["personal_info"]["occupation"] = job_match.group(1)
        
        return analysis
        
    def update_emotional_trend(self, user_id, emotion, intensity):
        """Update the emotional trend tracking for a user"""
        user_data = self.personality_factory._load_user_data(user_id)
        
        if "emotional_history" not in user_data:
            user_data["emotional_history"] = {
                "recent_emotions": [],
                "persistent_emotions": {}
            }
            
        if emotion not in user_data["emotional_history"].get("persistent_emotions", {}):
            user_data["emotional_history"]["persistent_emotions"][emotion] = {
                "count": 0,
                "first_seen": datetime.datetime.now().isoformat(),
                "last_seen": datetime.datetime.now().isoformat(),
                "duration_days": 0,
                "intensity_sum": 0.0
            }
        
        # Update emotion history
        user_data["emotional_history"]["recent_emotions"].append({
            "emotion": emotion,
            "intensity": intensity,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        # Keep only last 10 emotions
        if len(user_data["emotional_history"]["recent_emotions"]) > 10:
            user_data["emotional_history"]["recent_emotions"] = user_data["emotional_history"]["recent_emotions"][-10:]
        
        # Update persistent emotions
        persistent = user_data["emotional_history"]["persistent_emotions"][emotion]
        persistent["count"] += 1
        persistent["last_seen"] = datetime.datetime.now().isoformat()
        persistent["intensity_sum"] = persistent.get("intensity_sum", 0.0) + intensity
        persistent["duration_days"] = (
            datetime.datetime.fromisoformat(persistent["last_seen"]) - 
            datetime.datetime.fromisoformat(persistent["first_seen"])
        ).days
        
        # Save updated user data
        self.personality_factory._save_user_data(user_id, user_data)
    
    def get_emotional_trend(self, user_id):
        """Get the emotional trend for a user"""
        user_data = self.personality_factory._load_user_data(user_id)
        
        if "emotional_history" not in user_data:
            return {"trend": "neutral", "persistent_negative": False}
            
        recent_emotions = user_data["emotional_history"].get("recent_emotions", [])
        persistent_emotions = user_data["emotional_history"].get("persistent_emotions", {})
        
        if not recent_emotions:
            return {"trend": "neutral", "persistent_negative": False}
            
        # Check for persistent negative emotions (3+ instances within recent emotions)
        negative_emotions = ["sadness", "anger", "fear", "anxiety", "grief", "overwhelm", "loneliness"]
        recent_negative_count = sum(1 for e in recent_emotions if e["emotion"] in negative_emotions)
        persistent_negative = recent_negative_count >= 3
        
        # Determine overall trend (improving, stable, declining)
        trend = "stable"
        if len(recent_emotions) >= 5:
            # Split into first and second half to detect trend
            first_half = recent_emotions[:len(recent_emotions)//2]
            second_half = recent_emotions[len(recent_emotions)//2:]
            
            # Count positive emotions in each half
            positive_emotions = ["joy", "contentment", "surprise"]
            positive_first = sum(1 for e in first_half if e["emotion"] in positive_emotions)
            positive_second = sum(1 for e in second_half if e["emotion"] in positive_emotions)
            
            # Count negative emotions in each half
            negative_first = sum(1 for e in first_half if e["emotion"] in negative_emotions)
            negative_second = sum(1 for e in second_half if e["emotion"] in negative_emotions)
            
            # Determine trend based on emotional shift
            if positive_second > positive_first and negative_second < negative_first:
                trend = "improving"
            elif positive_second < positive_first and negative_second > negative_first:
                trend = "declining"
                
        return {
            "trend": trend,
            "persistent_negative": persistent_negative,
            "dominant_emotion": recent_emotions[-1]["emotion"] if recent_emotions else "neutral"
        }
    
    def get_emotional_history(self, user_id):
        """Get the emotional history for a user"""
        user_data = self.personality_factory._load_user_data(user_id)
        return user_data.get("emotional_history", {})
    
    def analyze_conversation_history(self, user_id):
        """Analyze recent conversation history to extract insights with improved analysis"""
        user_data = self.personality_factory._load_user_data(user_id)
        
        # Get last 50 messages
        short_term = user_data.get("memory", {}).get("short_term", [])
        
        if not short_term:
            return
        
        # Filter user messages only
        user_messages = [item["content"] for item in short_term if item.get("is_user", False)]
        
        # Calculate average message length
        avg_length = sum(len(msg.split()) for msg in user_messages) / len(user_messages) if user_messages else 0
        
        # Concatenate all messages for analysis
        all_text = " ".join(user_messages)
        
        # Complete emotional profile of conversation
        emotional_profile = self.emotion_analyzer.get_emotional_profile(all_text)
        
        # Conversation data for update
        conversation_data = {
            "message_count": len(user_messages),
            "avg_message_length": avg_length,
            "emotional_intensity": emotional_profile["intensity"],
            "personal_disclosure_level": self._calculate_disclosure_level(all_text),
            "question_depth": self._calculate_question_depth(all_text)
        }
        
        # Analyze as one batch
        self.analyze_message(all_text)
        
        # Return conversation data for evolution tracking
        return conversation_data
    
    def _calculate_question_depth(self, text):
        """Calculate the depth of questions in conversation (0-10 scale)"""
        # Simple patterns to match different levels of question depth
        surface_patterns = [
            r"how are you",
            r"what's up",
            r"how's it going",
            r"what is that",
            r"where is"
        ]
        
        medium_patterns = [
            r"how do you feel about",
            r"what do you think of",
            r"why did you",
            r"how does that",
            r"tell me about"
        ]
        
        deep_patterns = [
            r"what's your perspective on",
            r"how has that affected",
            r"what meaning",
            r"why do you believe",
            r"how have you grown",
            r"what does that say about",
            r"how would you describe your",
            r"what have you learned from"
        ]
        
        philosophical_patterns = [
            r"what is the meaning",
            r"purpose of life",
            r"what makes us human",
            r"nature of consciousness",
            r"why do we exist",
            r"what is truth",
            r"moral implications",
            r"ethical question"
        ]
        
        # Count matches for each level
        surface_count = sum(1 for pattern in surface_patterns if re.search(pattern, text.lower()))
        medium_count = sum(1 for pattern in medium_patterns if re.search(pattern, text.lower()))
        deep_count = sum(1 for pattern in deep_patterns if re.search(pattern, text.lower()))
        philosophical_count = sum(1 for pattern in philosophical_patterns if re.search(pattern, text.lower()))
        
        # Calculate weighted score (0-10)
        depth_score = (
            surface_count * 1 +
            medium_count * 3 +
            deep_count * 6 +
            philosophical_count * 10
        ) / max(1, surface_count + medium_count + deep_count + philosophical_count)
        
        return min(10, depth_score * 1.5)  # Scale up slightly but cap at 10
    
    def _get_dominant_emotion(self, user_id):
        """Get the dominant emotion from the user's emotional history with improved analysis"""
        user_data = self.personality_factory._load_user_data(user_id)
        
        if "emotional_history" not in user_data or "summary" not in user_data["emotional_history"]:
            return None
            
        summary = user_data["emotional_history"]["summary"]
        if not summary:
            return None
        
        # Get recent emotions (last 24 hours with higher weight)
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        recent_emotions = user_data["emotional_history"].get("daily_counts", {}).get(today, {})
        
        # Combine with weighted scoring (recent emotions count 3x more)
        weighted_scores = Counter()
        for emotion, count in summary.items():
            weighted_scores[emotion] = count
            
        for emotion, count in recent_emotions.items():
            weighted_scores[emotion] += count * 3
            
        # Get most common emotion
        return weighted_scores.most_common(1)[0][0] if weighted_scores else None
    
    def detect_emotional_trends(self, user_id):
        """Detect emotional trends and transitions over time"""
        user_data = self.personality_factory._load_user_data(user_id)
        
        if "emotional_history" not in user_data or "emotional_patterns" not in user_data["emotional_history"]:
            return None
            
        patterns = user_data["emotional_history"]["emotional_patterns"]
        if len(patterns) < 3:
            return None
            
        # Enhanced emotional valence with weighted impact
        emotional_valence = {
            "happiness": 1.0,
            "hopeful": 0.8,
            "trust": 0.7,
            "anticipation": 0.5,
            "surprise": 0.2,
            "neutral": 0,
            "tired": -0.3,
            "confused": -0.3,
            "sadness": -0.8,
            "fear": -0.7,
            "anger": -0.8,
            "disgust": -0.6,
            "anxiety": -0.7,
            "lonely": -0.8,
            "overwhelm": -0.9,
            "grief": -0.9,
            "depression": -1.0
        }
        
        # Calculate weighted emotional scores over time
        current_time = datetime.datetime.now()
        weighted_scores = []
        
        for pattern in patterns:
            pattern_time = datetime.datetime.fromisoformat(pattern["timestamp"])
            days_ago = (current_time - pattern_time).days
            
            # More recent emotions have higher weight
            time_weight = 1.0 / (1.0 + days_ago * 0.1)  # Decay factor
            emotion = pattern["emotion"]
            intensity = pattern["intensity"]
            
            valence = emotional_valence.get(emotion, 0) * intensity * time_weight
            weighted_scores.append(valence)
        
        # Detect trends using moving average
        window_size = min(5, len(weighted_scores))
        if window_size < 3:
            return None
            
        moving_averages = []
        for i in range(len(weighted_scores) - window_size + 1):
            window = weighted_scores[i:i+window_size]
            moving_averages.append(sum(window) / window_size)
        
        # Analyze trend characteristics
        if len(moving_averages) < 2:
            return None
            
        first_avg = moving_averages[0]
        last_avg = moving_averages[-1]
        change_threshold = 0.3  # Reduced threshold for more sensitive detection
        
        # Get emotions from relevant timeframes
        recent_patterns = patterns[-window_size:]
        older_patterns = patterns[:window_size]
        
        trend_data = {
            "magnitude": abs(last_avg - first_avg),
            "from_emotions": [p["emotion"] for p in older_patterns],
            "to_emotions": [p["emotion"] for p in recent_patterns],
            "current_valence": last_avg,
            "persistent_negative": last_avg < -0.5 and len([s for s in moving_averages if s < -0.3]) > len(moving_averages) * 0.7
        }
        
        # Determine trend direction with more nuanced categories
        if last_avg - first_avg > change_threshold:
            trend_data["trend"] = "improving"
        elif first_avg - last_avg > change_threshold:
            trend_data["trend"] = "declining"
        elif last_avg < -0.3:
            trend_data["trend"] = "persistently_negative"
        elif last_avg > 0.3:
            trend_data["trend"] = "persistently_positive"
        else:
            trend_data["trend"] = "stable"
        
        return trend_data
    
    def get_comfort_escalation_response(self, user_id, emotion):
        """Get an appropriate comfort response based on emotion persistence"""
        if emotion not in ["sadness", "anxiety", "anger", "fear"]:
            return None
            
        # Map emotions to comfort categories
        comfort_category = {
            "sadness": "sadness",
            "fear": "anxiety",
            "anxiety": "anxiety",
            "anger": "anger"
        }.get(emotion, "sadness")
        
        user_data = self.personality_factory._load_user_data(user_id)
        
        # If no persistence data, return first level response
        if "emotion_persistence" not in user_data or emotion not in user_data["emotion_persistence"]:
            return self.comfort_escalation_levels[comfort_category][0]
            
        # Get the current escalation level
        escalation_level = user_data["emotion_persistence"][emotion].get("current_escalation_level", 0)
        
        # Return appropriate response
        if escalation_level >= len(self.comfort_escalation_levels[comfort_category]):
            escalation_level = len(self.comfort_escalation_levels[comfort_category]) - 1
            
        return self.comfort_escalation_levels[comfort_category][escalation_level]
    
    def _calculate_disclosure_level(self, message):
        """Calculate the personal disclosure level in a message"""
        disclosure_level = 0.0
        matches = 0
        
        for pattern, level in self.personal_disclosure_patterns:
            if re.search(pattern, message.lower()):
                disclosure_level += level
                matches += 1
        
        if matches > 0:
            return min(1.0, disclosure_level / matches + 0.1 * matches)  # Adding bonus for multiple disclosures
        
        return 0.0
    
    def _detect_emotional_support_acknowledgment(self, message):
        """Detect if the user is acknowledging emotional support"""
        return any(re.search(pattern, message.lower()) for pattern in self.emotional_support_patterns)

    def detect_mental_health_concerns(self, message):
        """Enhanced detection of mental health concerns with severity assessment"""
        message_lower = message.lower()
        concerns = {"type": None, "severity": 0, "confidence": 0}
        
        for condition, indicators in self.mental_health_indicators.items():
            # Check explicit mentions
            explicit_count = sum(1 for word in indicators["explicit"] if word in message_lower)
            
            # Check implicit indicators
            implicit_count = sum(1 for phrase in indicators["implicit"] if phrase in message_lower)
            
            # Check behavioral indicators
            behavioral_count = sum(1 for phrase in indicators["behavioral"] if phrase in message_lower)
            
            # Calculate severity score (0-1)
            severity = min(1.0, (explicit_count * 0.5 + implicit_count * 0.3 + behavioral_count * 0.2))
            
            if severity > concerns["severity"]:
                concerns = {
                    "type": condition,
                    "severity": severity,
                    "confidence": min(1.0, explicit_count * 0.6 + implicit_count * 0.25 + behavioral_count * 0.15)
                }
        
        return concerns

    def get_mental_health_response(self, user_id, concern_type):
        """Get appropriate mental health response based on interaction history"""
        if concern_type not in self.mental_health_responses:
            return None
            
        user_data = self.personality_factory._load_user_data(user_id)
        mention_count = user_data.get("mental_health_mentions", {}).get(concern_type, 0)
        
        # Choose response level based on mention frequency
        level = min(len(self.mental_health_responses[concern_type]) - 1, mention_count)
        return self.mental_health_responses[concern_type][level]

    def update_adaptation_model(self, user_id: str, conversation_metrics: dict) -> dict:
        """Update the adaptation model based on conversation metrics and emotional patterns"""
        if 'emotional_states' not in conversation_metrics:
            return {}

        # Track emotional patterns
        emotional_states = conversation_metrics['emotional_states']
        if not emotional_states:
            return {}

        # Calculate emotional resonance
        emotional_resonance = self._calculate_emotional_resonance(emotional_states)
        
        # Update emotion patterns
        if user_id not in self.emotion_patterns:
            self.emotion_patterns[user_id] = []
        
        self.emotion_patterns[user_id].append({
            'timestamp': datetime.datetime.now().isoformat(),
            'resonance': emotional_resonance,
            'dominant_emotion': self._get_dominant_emotion(emotional_states)
        })

        # Keep only recent patterns
        self.emotion_patterns[user_id] = self.emotion_patterns[user_id][-10:]

        # Calculate adaptation scores
        adaptation_scores = {
            'emotional_resonance': emotional_resonance,
            'conversation_depth': conversation_metrics.get('emotional_depth', 0.5),
            'user_engagement': conversation_metrics.get('engagement_level', 0.5)
        }

        # Calculate weighted adaptation score
        weighted_score = sum(
            score * self.adaptation_weights[metric]
            for metric, score in adaptation_scores.items()
        )

        return {
            'adaptation_score': weighted_score,
            'emotional_pattern': self.emotion_patterns[user_id][-1],
            'recommended_adjustments': self._get_adaptation_recommendations(
                weighted_score,
                self.emotion_patterns[user_id]
            )
        }

    def _calculate_emotional_resonance(self, emotional_states: list) -> float:
        """Calculate emotional resonance from recent emotional states"""
        if not emotional_states:
            return 0.5

        # Get recent emotions and their intensities
        recent_emotions = [
            (state['emotion'], state['intensity']) 
            for state in emotional_states[-5:]
        ]

        # Calculate consistency and intensity
        unique_emotions = len(set(emotion for emotion, _ in recent_emotions))
        avg_intensity = sum(intensity for _, intensity in recent_emotions) / len(recent_emotions)

        # Higher resonance for consistent emotions with moderate-high intensity
        emotional_consistency = 1.0 - (unique_emotions / len(recent_emotions))
        resonance = (emotional_consistency * 0.6) + (avg_intensity * 0.4)

        return min(1.0, max(0.0, resonance))

    def _get_dominant_emotion(self, emotional_states: list) -> str:
        """Get the dominant emotion from recent states"""
        if not emotional_states:
            return 'neutral'

        # Count emotion occurrences
        emotion_counts = {}
        for state in emotional_states[-5:]:
            emotion = state['emotion']
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        # Return most frequent emotion
        return max(emotion_counts.items(), key=lambda x: x[1])[0]

    def _get_adaptation_recommendations(self, score: float, patterns: list) -> dict:
        """Generate personality adaptation recommendations"""
        if not patterns:
            return {'adjust_emotional_depth': 0.0, 'adjust_conversation_style': 0.0}

        recent_pattern = patterns[-1]
        dominant_emotion = recent_pattern['dominant_emotion']
        resonance = recent_pattern['resonance']

        recommendations = {
            'adjust_emotional_depth': 0.0,
            'adjust_conversation_style': 0.0
        }

        # Adjust emotional depth based on resonance
        if (resonance < 0.3):
            recommendations['adjust_emotional_depth'] = 0.2  # Increase emotional depth
        elif (resonance > 0.7):
            recommendations['adjust_emotional_depth'] = -0.1  # Slightly decrease emotional depth

        # Adjust conversation style based on dominant emotion
        if (dominant_emotion in ['sadness', 'anxiety']):
            recommendations['adjust_conversation_style'] = 0.3  # More supportive style
        elif (dominant_emotion in ['joy', 'excitement']):
            recommendations['adjust_conversation_style'] = -0.2  # More celebratory style

        return recommendations