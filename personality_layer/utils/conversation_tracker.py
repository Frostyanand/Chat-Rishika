from datetime import datetime
import json
import os
import re

class EmotionAnalyzer:
    def analyze(self, message):
        # Dummy implementation for the sake of example
        return {
            "emotion": "neutral",
            "intensity": 0.5,
            "depth": 0.5
        }

class MemoryStore:
    def store_data(self, key, data):
        # Dummy implementation for the sake of example
        pass

class ConversationTracker:
    """Tracks and manages conversation metrics and history"""
    
    def __init__(self, storage_path="./user_data", memory_store=None):
        """Initialize the conversation tracker with a storage path"""
        self.storage_path = storage_path
        self.memory_store = memory_store or MemoryStore()
        self.emotion_analyzer = EmotionAnalyzer()
        self.metrics = {}  # In-memory cache of user metrics
        self.emotional_pattern_window = 10  # Track last 10 interactions
        self.concern_threshold = 0.75  # Threshold for flagging concerns
        
        # Ensure storage directory exists
        os.makedirs(storage_path, exist_ok=True)
    
    def add_message(self, user_id, message_content):
        """Add a message to the user's conversation history"""
        # Initialize user metrics if they don't exist
        if user_id not in self.metrics:
            self._load_user_metrics(user_id)
            
        # Initialize if still not found (new user)
        if user_id not in self.metrics:
            self.metrics[user_id] = {
                "first_interaction": datetime.now().isoformat(),
                "last_interaction": datetime.now().isoformat(),
                "message_count": 0,
                "conversation_history": []
            }
        
        # Update metrics
        message_data = {
            "content": message_content,
            "timestamp": datetime.now().isoformat(),
            "word_count": len(message_content.split())
        }
        
        # Update user metrics
        self.metrics[user_id]["message_count"] += 1
        self.metrics[user_id]["last_interaction"] = datetime.now().isoformat()
        
        # Add to conversation history, limiting size to prevent memory issues
        self.metrics[user_id]["conversation_history"].append(message_data)
        if len(self.metrics[user_id]["conversation_history"]) > 100:
            self.metrics[user_id]["conversation_history"] = self.metrics[user_id]["conversation_history"][-100:]
        
        # Save updated metrics
        self._save_user_metrics(user_id)
    
    def get_user_metrics(self, user_id):
        """Get metrics for a specific user"""
        if user_id not in self.metrics:
            self._load_user_metrics(user_id)
        
        return self.metrics.get(user_id, {})
    
    def _get_user_metrics_file(self, user_id):
        """Get the file path for user metrics"""
        return os.path.join(self.storage_path, f"{user_id}_conversation_metrics.json")
    
    def _load_user_metrics(self, user_id):
        """Load user metrics from storage"""
        metrics_file = self._get_user_metrics_file(user_id)
        if os.path.exists(metrics_file):
            try:
                with open(metrics_file, 'r') as f:
                    self.metrics[user_id] = json.load(f)
            except Exception as e:
                print(f"Error loading metrics for {user_id}: {e}")
                self.metrics[user_id] = {
                    "first_interaction": datetime.now().isoformat(),
                    "last_interaction": datetime.now().isoformat(),
                    "message_count": 0,
                    "conversation_history": []
                }
    
    def _save_user_metrics(self, user_id):
        """Save user metrics to storage"""
        metrics_file = self._get_user_metrics_file(user_id)
        try:
            with open(metrics_file, 'w') as f:
                json.dump(self.metrics[user_id], f, indent=2)
        except Exception as e:
            print(f"Error saving metrics for {user_id}: {e}")
    
    def get_conversation_summary(self, user_id):
        """Get a summary of the conversation with this user"""
        metrics = self.get_user_metrics(user_id)
        
        # Basic summary
        summary = {
            "message_count": metrics.get("message_count", 0),
            "first_interaction": metrics.get("first_interaction", None),
            "last_interaction": metrics.get("last_interaction", None)
        }
        
        # Calculate total words
        total_words = 0
        for message in metrics.get("conversation_history", []):
            total_words += message.get("word_count", 0)
        
        summary["total_words"] = total_words
        summary["avg_message_length"] = total_words / max(1, summary["message_count"])
        
        # Calculate days of interaction
        if summary["first_interaction"] and summary["last_interaction"]:
            first_date = datetime.fromisoformat(summary["first_interaction"]).date()
            last_date = datetime.fromisoformat(summary["last_interaction"]).date()
            days_diff = (last_date - first_date).days
            summary["interaction_span_days"] = max(1, days_diff)
        
        return summary

    def track_conversation(self, user_id, message_data, emotional_profile):
        """Track conversation with emotional pattern analysis"""
        conversation_data = {
            "timestamp": datetime.now().isoformat(),
            "content_metrics": self.analyze_content(message_data),
            "emotional_metrics": self.analyze_emotional_patterns(emotional_profile),
            "interaction_depth": self.calculate_interaction_depth(message_data)
        }
        
        # Check for concerning patterns
        concerns = self.check_concerning_patterns(conversation_data)
        if concerns:
            conversation_data["concerns"] = concerns
            
        return conversation_data
        
    def analyze_content(self, message_data):
        """Analyze message content for meaningful patterns"""
        content = message_data.get("content", "")
        return {
            "length": len(content),
            "question_count": content.count("?"),
            "exclamation_count": content.count("!"),
            "word_count": len(content.split()),
            "avg_word_length": sum(len(word) for word in content.split()) / max(1, len(content.split())),
            "has_urls": bool(re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content))
        }
        
    def analyze_emotional_patterns(self, emotional_profile):
        """Analyze emotional patterns in conversation"""
        return {
            "primary_emotion": emotional_profile.get("dominant_emotion", "neutral"),
            "emotional_intensity": emotional_profile.get("intensity", 0),
            "emotional_complexity": emotional_profile.get("complexity", 0),
            "emotions_detected": list(emotional_profile.get("emotions", {}).keys())
        }
        
    def calculate_interaction_depth(self, message_data):
        """Calculate the depth of interaction"""
        depth_indicators = {
            "personal_disclosure": r"\b(i feel|i think|i believe|i'm feeling|i am feeling)\b",
            "seeking_support": r"\b(help|advice|support|suggestion)\b",
            "emotional_expression": r"\b(happy|sad|angry|scared|worried|anxious|depressed)\b",
            "reflection": r"\b(because|since|therefore|however|although)\b"
        }
        
        content = message_data.get("content", "").lower()
        depth_score = 0
        
        for indicator_type, pattern in depth_indicators.items():
            matches = len(re.findall(pattern, content))
            if matches > 0:
                depth_score += min(matches * 0.2, 0.5)  # Cap each indicator's contribution
                
        return min(depth_score, 1.0)  # Normalize to 0-1
        
    def check_concerning_patterns(self, conversation_data):
        """Check for patterns that might indicate concerns"""
        concerns = []
        
        # Check emotional intensity
        if conversation_data["emotional_metrics"]["emotional_intensity"] > self.concern_threshold:
            concerns.append({
                "type": "high_emotional_intensity",
                "level": conversation_data["emotional_metrics"]["emotional_intensity"],
                "primary_emotion": conversation_data["emotional_metrics"]["primary_emotion"]
            })
            
        # Check for distress indicators
        distress_emotions = ["sadness", "anxiety", "anger", "depression"]
        detected_emotions = conversation_data["emotional_metrics"]["emotions_detected"]
        
        if any(emotion in detected_emotions for emotion in distress_emotions):
            concerns.append({
                "type": "emotional_distress",
                "emotions": [e for e in detected_emotions if e in distress_emotions]
            })
            
        # Check interaction depth for support needs
        if conversation_data["interaction_depth"] > self.concern_threshold:
            concerns.append({
                "type": "deep_emotional_engagement",
                "depth_level": conversation_data["interaction_depth"]
            })
            
        return concerns if concerns else None
        
    def analyze_long_term_patterns(self, conversation_history):
        """Analyze long-term conversation patterns"""
        if len(conversation_history) < 2:
            return {"stability": 1.0, "trend": "stable", "patterns": []}
            
        # Analyze emotional trajectory
        emotional_intensities = [
            conv["emotional_metrics"]["emotional_intensity"]
            for conv in conversation_history
        ]
        
        # Calculate trend
        trend = "stable"
        if len(emotional_intensities) >= 3:
            recent_trend = emotional_intensities[-3:]
            if all(recent_trend[i] > recent_trend[i-1] for i in range(1, len(recent_trend))):
                trend = "intensifying"
            elif all(recent_trend[i] < recent_trend[i-1] for i in range(1, len(recent_trend))):
                trend = "diminishing"
                
        # Calculate stability
        avg_intensity = sum(emotional_intensities) / len(emotional_intensities)
        variability = sum(abs(i - avg_intensity) for i in emotional_intensities) / len(emotional_intensities)
        stability = max(0, 1 - variability)
        
        # Identify recurring patterns
        patterns = self.identify_recurring_patterns(conversation_history)
        
        return {
            "stability": stability,
            "trend": trend,
            "patterns": patterns,
            "avg_intensity": avg_intensity,
            "variability": variability
        }
        
    def identify_recurring_patterns(self, conversation_history):
        """Identify recurring patterns in conversation history"""
        patterns = []
        
        # Group conversations by emotion
        emotion_groups = {}
        for conv in conversation_history:
            emotion = conv["emotional_metrics"]["primary_emotion"]
            if emotion not in emotion_groups:
                emotion_groups[emotion] = []
            emotion_groups[emotion].append(conv)
            
        # Analyze patterns for each emotion
        for emotion, convs in emotion_groups.items():
            if len(convs) >= 3:  # Minimum occurrences to consider a pattern
                avg_intensity = sum(c["emotional_metrics"]["emotional_intensity"] for c in convs) / len(convs)
                patterns.append({
                    "type": "recurring_emotion",
                    "emotion": emotion,
                    "frequency": len(convs) / len(conversation_history),
                    "avg_intensity": avg_intensity
                })
                
        return patterns

    def update_conversation_state(self, user_id: str, message: str, response: str) -> dict:
        """Update conversation state with improved emotional tracking"""
        if not user_id in self.metrics:
            self.metrics[user_id] = {
                "message_count": 0,
                "emotional_depth": 0.0,
                "topic_consistency": 0.0,
                "engagement_level": 0.0,
                "emotional_states": []
            }

        # Analyze message emotions
        emotion_data = self.emotion_analyzer.analyze(message)
        
        # Update metrics
        self.metrics[user_id]["message_count"] += 1
        self.metrics[user_id]["emotional_depth"] = (
            self.metrics[user_id]["emotional_depth"] * 0.8 + 
            emotion_data["depth"] * 0.2
        )
        
        # Track emotional states with timestamps
        self.metrics[user_id]["emotional_states"].append({
            "timestamp": datetime.now().isoformat(),
            "emotion": emotion_data["emotion"],
            "intensity": emotion_data["intensity"]
        })
        
        # Keep only last 10 emotional states
        self.metrics[user_id]["emotional_states"] = (
            self.metrics[user_id]["emotional_states"][-10:]
        )
        
        # Store updated metrics
        self._persist_metrics(user_id)
        
        return {
            "current_metrics": self.metrics[user_id],
            "current_emotion": emotion_data
        }

    def _persist_metrics(self, user_id: str):
        """Persist conversation metrics to storage"""
        try:
            metrics_key = f"user_{user_id}_conversation_metrics"
            self.memory_store.store_data(
                metrics_key,
                self.metrics[user_id]
            )
        except Exception as e:
            logger.error(f"Failed to persist metrics for user {user_id}: {e}")

    def get_conversation_trends(self, user_id: str) -> dict:
        """Get conversation trends and patterns"""
        if user_id not in self.metrics:
            return {}
            
        metrics = self.metrics[user_id]
        emotional_states = metrics.get("emotional_states", [])
        
        # Analyze emotional patterns
        if emotional_states:
            recent_emotions = [state["emotion"] for state in emotional_states[-5:]]
            dominant_emotion = max(set(recent_emotions), key=recent_emotions.count)
            emotion_variety = len(set(recent_emotions))
        else:
            dominant_emotion = "neutral"
            emotion_variety = 0
            
        return {
            "message_count": metrics["message_count"],
            "emotional_depth": metrics["emotional_depth"],
            "dominant_emotion": dominant_emotion,
            "emotion_variety": emotion_variety,
            "engagement_level": metrics["engagement_level"]
        }