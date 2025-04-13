"""Emotion analysis utilities for Elysia"""
import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)

class EmotionAnalyzer:
    """Analyzes emotional content in messages"""
    
    def __init__(self):
        """Initialize the emotion analyzer"""
        # Basic emotions dictionary
        self.emotions = {
            "joy": ["happy", "glad", "excited", "wonderful", "joy", "fantastic", "great", "lovely", "pleased"],
            "sadness": ["sad", "unhappy", "depressed", "miserable", "down", "blue", "upset", "heartbroken"],
            "anger": ["angry", "mad", "furious", "annoyed", "irritated", "frustrated", "outraged"],
            "fear": ["afraid", "scared", "terrified", "fearful", "worried", "anxious", "nervous"],
            "surprise": ["surprised", "amazed", "astonished", "shocked", "stunned"],
            "neutral": []
        }

        # More detailed emotion patterns
        self.emotion_patterns = {
            "joy": {
                "explicit": ["happy", "joyful", "excited", "delighted"],
                "implicit": ["looking forward to", "can't wait", "blessed", "grateful"],
                "behavioral": ["smiling", "laughing", "celebrating"]
            },
            "sadness": {
                "explicit": ["sad", "unhappy", "depressed", "miserable"],
                "implicit": ["miss", "lonely", "empty", "numb"],
                "behavioral": ["crying", "tears", "not sleeping"]
            },
            "anger": {
                "explicit": ["angry", "mad", "furious", "annoyed"],
                "implicit": ["unfair", "frustrated", "tired of", "fed up"],
                "behavioral": ["yelling", "screaming", "breaking"]
            },
            "anxiety": {
                "explicit": ["anxious", "nervous", "worried", "scared"],
                "implicit": ["what if", "stressed", "overwhelmed", "uneasy"],
                "behavioral": ["can't sleep", "racing thoughts", "panic"]
            }
        }
        
        # Intensity modifiers
        self.intensity_modifiers = {
            "very": 1.5,
            "really": 1.3,
            "extremely": 1.8,
            "so": 1.4,
            "totally": 1.3,
            "completely": 1.6,
            "absolutely": 1.7
        }
        
        # Emotion mixers for complex emotional states
        self.emotion_mixers = {
            ("joy", "anxiety"): "excitement",
            ("sadness", "anger"): "frustration",
            ("joy", "sadness"): "nostalgia",
            ("anxiety", "anger"): "stress"
        }
        
        # Load any stored emotion data
        self.emotion_data = {}
        self.data_dir = "./user_data"
        self._load_emotion_data()

        self.emotion_weights = {
            'joy': 1.0,
            'sadness': -0.5,
            'anger': -0.8,
            'fear': -0.6,
            'surprise': 0.2,
            'neutral': 0.0,
            'trust': 0.7,
            'anticipation': 0.4
        }
        self.emotional_history = []
    
    def _get_data_path(self) -> str:
        """Get path to emotion data file"""
        os.makedirs(self.data_dir, exist_ok=True)
        return os.path.join(self.data_dir, "emotion_data.json")
    
    def _load_emotion_data(self) -> None:
        """Load stored emotion data"""
        try:
            file_path = self._get_data_path()
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    self.emotion_data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading emotion data: {e}")
            self.emotion_data = {}
    
    def _save_emotion_data(self) -> None:
        """Save emotion data to storage"""
        try:
            file_path = self._get_data_path()
            with open(file_path, 'w') as f:
                json.dump(self.emotion_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving emotion data: {e}")
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze text for emotional content"""
        if not text or not isinstance(text, str):
            return {
                "emotion": "neutral",
                "intensity": 0.0,
                "depth": 0.0,
                "details": {
                    "word_count": 0,
                    "emotion_words": 0,
                    "error": "Invalid input"
                }
            }

        try:
            text = text.lower()
            max_emotion = "neutral"
            max_count = 0
            word_count = len(text.split())
            
            # Count emotion words
            for emotion, words in self.emotions.items():
                count = sum(1 for word in words if word in text)
                if count > max_count:
                    max_count = count
                    max_emotion = emotion
            
            # Calculate intensity based on emotion word density
            intensity = min(1.0, max_count / max(1, word_count / 2))
            
            # Adjust intensity based on punctuation
            if "!" in text:
                intensity = min(1.0, intensity + 0.2)
            if "!!" in text:
                intensity = min(1.0, intensity + 0.3)
            if "?" in text:
                intensity = max(0.3, intensity)  # Questions indicate engagement
            
            # Calculate depth score (based on message complexity)
            depth = min(1.0, word_count / 20)  # Longer messages may indicate deeper engagement
            if "because" in text or "since" in text or "therefore" in text:
                depth = min(1.0, depth + 0.2)  # Reasoning indicates depth
            if "feel" in text or "think" in text or "believe" in text:
                depth = min(1.0, depth + 0.2)  # Personal expression indicates depth
            
            return {
                "emotion": max_emotion,
                "intensity": intensity,
                "depth": depth,
                "details": {
                    "word_count": word_count,
                    "emotion_words": max_count
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing emotions: {e}")
            return {
                "emotion": "neutral",
                "intensity": 0.0,
                "depth": 0.0,
                "details": {
                    "word_count": 0,
                    "emotion_words": 0,
                    "error": str(e)
                }
            }
    
    def get_emotional_profile(self, text):
        """Get a detailed emotional profile from text with improved accuracy"""
        if not text or not isinstance(text, str):
            return {}
            
        try:
            text = text.lower()
            emotions = {}
            
            # Check each emotion category
            for emotion, patterns in self.emotion_patterns.items():
                score = 0
                intensity = 1.0
                
                # Check explicit mentions
                for word in patterns["explicit"]:
                    if word in text:
                        score += 1.0
                        # Check for intensity modifiers before the word
                        for modifier, mult in self.intensity_modifiers.items():
                            if f"{modifier} {word}" in text:
                                intensity *= mult
                                
                # Check implicit indicators
                for phrase in patterns["implicit"]:
                    if phrase in text:
                        score += 0.7
                        
                # Check behavioral indicators
                for behavior in patterns["behavioral"]:
                    if behavior in text:
                        score += 0.8
                        
                # Only include emotions with significant scores
                if score > 0:
                    emotions[emotion] = {
                        "score": min(score * intensity, 5.0),  # Cap at 5.0
                        "confidence": min((score * intensity) / 5.0, 1.0)  # Normalize to 0-1
                    }
            
            # Check for mixed emotions
            if len(emotions) >= 2:
                emotion_pairs = list(emotions.keys())
                for i in range(len(emotion_pairs)):
                    for j in range(i + 1, len(emotion_pairs)):
                        pair = (emotion_pairs[i], emotion_pairs[j])
                        if pair in self.emotion_mixers:
                            mixed_emotion = self.emotion_mixers[pair]
                            # Average the scores of the component emotions
                            score = (emotions[pair[0]]["score"] + emotions[pair[1]]["score"]) / 2
                            emotions[mixed_emotion] = {
                                "score": score,
                                "confidence": min(
                                    (emotions[pair[0]]["confidence"] + emotions[pair[1]]["confidence"]) / 2,
                                    1.0
                                )
                            }
            
            # Add overall emotional intensity
            max_score = max([e["score"] for e in emotions.values()]) if emotions else 0
            
            return {
                "emotions": emotions,
                "intensity": max_score / 5.0,  # Normalize to 0-1
                "complexity": len(emotions),
                "dominant_emotion": max(emotions.items(), key=lambda x: x[1]["score"])[0] if emotions else "neutral"
            }
        except Exception as e:
            logger.error(f"Error getting emotional profile: {e}")
            return {}
        
    def analyze_emotional_stability(self, emotional_history):
        """Analyze emotional stability over time"""
        if not emotional_history:
            return {
                "stability": 1.0,
                "variability": 0.0,
                "trend": "stable"
            }
            
        # Calculate emotional variability
        intensity_values = [entry.get("intensity", 0) for entry in emotional_history]
        avg_intensity = sum(intensity_values) / len(intensity_values)
        variability = sum(abs(x - avg_intensity) for x in intensity_values) / len(intensity_values)
        
        # Detect emotional trends
        if len(intensity_values) >= 3:
            recent_trend = intensity_values[-3:]
            if all(recent_trend[i] > recent_trend[i-1] for i in range(1, len(recent_trend))):
                trend = "increasing"
            elif all(recent_trend[i] < recent_trend[i-1] for i in range(1, len(recent_trend))):
                trend = "decreasing"
            else:
                trend = "fluctuating"
        else:
            trend = "stable"
            
        return {
            "stability": max(0, 1 - variability),  # Higher variability = lower stability
            "variability": variability,
            "trend": trend
        }
    
    def update_user_emotional_state(self, user_id: str, emotion: str, intensity: float) -> None:
        """Update stored emotional state for a user"""
        if user_id not in self.emotion_data:
            self.emotion_data[user_id] = {
                "current_emotion": emotion,
                "current_intensity": intensity,
                "emotion_history": []
            }
        
        user_data = self.emotion_data[user_id]
        user_data["emotion_history"].append({
            "emotion": emotion,
            "intensity": intensity
        })
        
        # Keep only last 10 emotions in history
        if len(user_data["emotion_history"]) > 10:
            user_data["emotion_history"] = user_data["emotion_history"][-10:]
        
        user_data["current_emotion"] = emotion
        user_data["current_intensity"] = intensity
        
        self._save_emotion_data()
    
    def get_user_emotional_state(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get current emotional state for a user"""
        return self.emotion_data.get(user_id)

    def analyze_emotion(self, text: str, context: Dict = None) -> Dict:
        """Analyze emotional content of text with context awareness"""
        # Calculate base emotion scores
        emotion_scores = self._calculate_base_emotions(text)
        
        # Consider conversation context if provided
        if context and 'previous_emotions' in context:
            emotion_scores = self._adjust_with_context(
                emotion_scores, 
                context['previous_emotions']
            )

        # Get dominant emotion and intensity
        dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
        intensity = emotion_scores[dominant_emotion]

        # Update emotional history
        self.emotional_history.append({
            'timestamp': datetime.now().isoformat(),
            'emotion': dominant_emotion,
            'intensity': intensity,
            'context': context
        })

        return {
            'dominant_emotion': dominant_emotion,
            'intensity': intensity,
            'emotion_scores': emotion_scores,
            'emotional_valence': self._calculate_emotional_valence(emotion_scores)
        }

    def _calculate_base_emotions(self, text: str) -> Dict[str, float]:
        """Calculate base emotion scores from text"""
        # Placeholder for more sophisticated emotion detection
        # In a production system, this would use NLP models
        scores = {emotion: 0.0 for emotion in self.emotion_weights.keys()}
        
        # Simple keyword-based scoring for demonstration
        joy_keywords = ['happy', 'great', 'wonderful', 'excellent']
        sadness_keywords = ['sad', 'sorry', 'unfortunate', 'disappointing']
        
        text_lower = text.lower()
        
        for word in joy_keywords:
            if word in text_lower:
                scores['joy'] += 0.3
                
        for word in sadness_keywords:
            if word in text_lower:
                scores['sadness'] += 0.3

        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: v/total for k, v in scores.items()}

        return scores

    def _adjust_with_context(self, current_scores: Dict[str, float], 
                           previous_emotions: List[Dict]) -> Dict[str, float]:
        """Adjust emotion scores based on conversation context"""
        if not previous_emotions:
            return current_scores

        # Get recent emotional trend
        recent_emotions = previous_emotions[-3:]
        trend_weight = 0.2

        # Calculate emotional momentum
        for prev_emotion in recent_emotions:
            emotion = prev_emotion['emotion']
            if emotion in current_scores:
                current_scores[emotion] += trend_weight * prev_emotion['intensity']

        # Normalize scores again
        total = sum(current_scores.values())
        if total > 0:
            current_scores = {k: v/total for k, v in current_scores.items()}

        return current_scores

    def _calculate_emotional_valence(self, emotion_scores: Dict[str, float]) -> float:
        """Calculate overall emotional valence"""
        valence = 0.0
        for emotion, score in emotion_scores.items():
            valence += score * self.emotion_weights.get(emotion, 0.0)
        
        # Normalize to [-1, 1] range
        return np.tanh(valence)

    def get_emotional_trend(self, window_size: int = 5) -> Dict:
        """Analyze emotional trends over recent interactions"""
        if not self.emotional_history:
            return {'trend': 'neutral', 'stability': 1.0}

        recent_history = self.emotional_history[-window_size:]
        
        # Calculate emotional stability
        emotions = [h['emotion'] for h in recent_history]
        unique_emotions = len(set(emotions))
        stability = 1.0 - (unique_emotions / len(emotions))

        # Calculate average valence
        valences = [
            self.emotion_weights.get(h['emotion'], 0.0) * h['intensity']
            for h in recent_history
        ]
        avg_valence = sum(valences) / len(valences)

        return {
            'trend': 'positive' if avg_valence > 0.2 
                    else 'negative' if avg_valence < -0.2 
                    else 'neutral',
            'stability': stability,
            'average_valence': avg_valence
        }