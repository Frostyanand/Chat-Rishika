"""Personality evolution system for tracking and evolving relationship stages"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class PersonalityEvolution:
    """Handles the evolution of Elysia's relationship with users"""
    
    def __init__(self):
        """Initialize the personality evolution system"""
        self.stages = [
            "new",
            "acquaintance",
            "familiar",
            "close",
            "trusted",
            "intimate"
        ]
        
        self.stage_thresholds = {
            "acquaintance": 10,  # 10 meaningful interactions
            "familiar": 25,      # 25 meaningful interactions
            "close": 50,         # 50 meaningful interactions
            "trusted": 100,      # 100 meaningful interactions
            "intimate": 200      # 200 meaningful interactions
        }
        
        self.evolution_data = {}
        self.data_dir = "./user_data"
        
        self.adaptation_thresholds = {
            "emotional_support": 0.7,  # Threshold for increasing emotional support
            "professional_referral": 0.85,  # Threshold for suggesting professional help
            "conversation_depth": 0.6  # Threshold for deeper conversations
        }
        
        self.support_levels = {
            "minimal": {
                "max_depth": 0.3,
                "response_style": "light",
                "follow_up_frequency": 0.2
            },
            "moderate": {
                "max_depth": 0.6,
                "response_style": "balanced",
                "follow_up_frequency": 0.5
            },
            "intensive": {
                "max_depth": 1.0,
                "response_style": "supportive",
                "follow_up_frequency": 0.8
            }
        }
    
    def _get_user_data_path(self, user_id: str) -> str:
        """Get path to user's evolution data file"""
        base_path = os.path.join(self.data_dir, f"user_{user_id}")
        os.makedirs(base_path, exist_ok=True)
        return os.path.join(base_path, "evolution_data.json")
    
    def _load_evolution_data(self, user_id: str) -> Dict[str, Any]:
        """Load evolution data for a user"""
        try:
            file_path = self._get_user_data_path(user_id)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            return {
                "stage": "new",
                "interaction_count": 0,
                "meaningful_interactions": 0,
                "last_interaction": None,
                "first_interaction": datetime.now().isoformat(),
                "evolution_stats": {}
            }
        except Exception as e:
            logger.error(f"Error loading evolution data: {e}")
            return {
                "stage": "new",
                "interaction_count": 0,
                "meaningful_interactions": 0,
                "last_interaction": None,
                "first_interaction": datetime.now().isoformat(),
                "evolution_stats": {}
            }
    
    def _save_evolution_data(self, user_id: str, data: Dict[str, Any]) -> bool:
        """Save evolution data for a user"""
        try:
            file_path = self._get_user_data_path(user_id)
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving evolution data: {e}")
            return False
    
    def get_relationship_data(self, user_id: str) -> Dict[str, Any]:
        """Get current relationship data for a user"""
        if user_id not in self.evolution_data:
            self.evolution_data[user_id] = self._load_evolution_data(user_id)
        return self.evolution_data[user_id]
    
    def update_evolution_stats(self, user_id: str, interaction_data: Dict[str, Any]) -> None:
        """Update evolution statistics based on new interaction"""
        data = self.get_relationship_data(user_id)
        
        # Update basic stats
        data["interaction_count"] = data.get("interaction_count", 0) + 1
        data["last_interaction"] = datetime.now().isoformat()
        
        # Calculate interaction depth
        depth_score = 0.0
        if "depth_level" in interaction_data:
            depth_score = float(interaction_data["depth_level"])
        elif "emotion_intensity" in interaction_data:
            depth_score = float(interaction_data["emotion_intensity"]) * 0.7
        
        # Update meaningful interactions count
        if depth_score > 0.5:
            data["meaningful_interactions"] = data.get("meaningful_interactions", 0) + 1
        
        # Check for stage progression
        current_stage = data.get("stage", "new")
        meaningful_interactions = data.get("meaningful_interactions", 0)
        
        for stage, threshold in self.stage_thresholds.items():
            if current_stage != stage and meaningful_interactions >= threshold:
                if self.stages.index(stage) > self.stages.index(current_stage):
                    data["stage"] = stage
                    data["stage_reached_at"] = datetime.now().isoformat()
                    logger.info(f"User {user_id} progressed to stage: {stage}")
        
        # Store interaction details
        if "evolution_stats" not in data:
            data["evolution_stats"] = {}
        
        stats = data["evolution_stats"]
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        if current_date not in stats:
            stats[current_date] = {
                "interaction_count": 0,
                "meaningful_interactions": 0,
                "total_depth": 0.0,
                "emotions": {}
            }
        
        daily_stats = stats[current_date]
        daily_stats["interaction_count"] += 1
        daily_stats["total_depth"] += depth_score
        
        if depth_score > 0.5:
            daily_stats["meaningful_interactions"] += 1
        
        # Track emotions
        if "emotion" in interaction_data:
            emotion = interaction_data["emotion"]
            if emotion not in daily_stats["emotions"]:
                daily_stats["emotions"][emotion] = 0
            daily_stats["emotions"][emotion] += 1
        
        # Save updated data
        self._save_evolution_data(user_id, data)
        self.evolution_data[user_id] = data
    
    def update_metrics(self, message_data: Dict[str, Any]) -> Optional[str]:
        """Update metrics and check for milestones"""
        milestone_message = None
        
        # Add milestone checking logic here in the future
        # For now, just acknowledging that milestones will be tracked
        
        return milestone_message
        
    def analyze_interaction_patterns(self, user_history):
        """Analyze user interaction patterns to guide personality evolution"""
        if not user_history:
            return self.get_default_personality_settings()
            
        # Calculate engagement metrics
        avg_msg_length = sum(len(msg["content"]) for msg in user_history) / len(user_history)
        emotional_content = sum(1 for msg in user_history if msg.get("emotional_intensity", 0) > 0.5)
        support_seeking = sum(1 for msg in user_history if msg.get("support_seeking", False))
        
        # Analyze emotional stability
        emotional_stability = self.calculate_emotional_stability(user_history)
        
        # Determine optimal personality settings
        settings = {
            "empathy_level": min(1.0, emotional_content / len(user_history) + 0.3),
            "response_depth": min(1.0, avg_msg_length / 100),  # Normalize to 0-1
            "support_level": min(1.0, support_seeking / len(user_history) + 0.2),
            "conversation_style": self.determine_conversation_style(emotional_stability)
        }
        
        return settings
        
    def calculate_emotional_stability(self, user_history):
        """Calculate emotional stability score from user history"""
        if len(user_history) < 2:
            return 1.0  # Assume stable if not enough history
            
        # Get emotional intensities
        intensities = [msg.get("emotional_intensity", 0) for msg in user_history]
        
        # Calculate variability
        avg_intensity = sum(intensities) / len(intensities)
        variability = sum(abs(i - avg_intensity) for i in intensities) / len(intensities)
        
        # Calculate stability (inverse of variability)
        stability = max(0, 1 - variability)
        
        return stability
        
    def determine_conversation_style(self, emotional_stability):
        """Determine appropriate conversation style based on emotional stability"""
        if emotional_stability < 0.3:
            return {
                "style": "supportive",
                "depth": "shallow",
                "pace": "slow",
                "focus": "emotional"
            }
        elif emotional_stability < 0.7:
            return {
                "style": "balanced",
                "depth": "moderate",
                "pace": "medium",
                "focus": "mixed"
            }
        else:
            return {
                "style": "engaging",
                "depth": "deep",
                "pace": "natural",
                "focus": "comprehensive"
            }
            
    def adjust_support_level(self, current_level, emotional_state):
        """Adjust support level based on emotional state"""
        if emotional_state.get("intensity", 0) > self.adaptation_thresholds["professional_referral"]:
            return "intensive"
        elif emotional_state.get("intensity", 0) > self.adaptation_thresholds["emotional_support"]:
            return "moderate"
        else:
            return "minimal"
            
    def get_support_settings(self, level):
        """Get support settings for a given level"""
        return self.support_levels.get(level, self.support_levels["minimal"])
        
    def evolve_personality(self, user_data, interaction_history):
        """Evolve personality based on user interactions and emotional patterns"""
        # Analyze patterns
        interaction_patterns = self.analyze_interaction_patterns(interaction_history)
        
        # Get current emotional state
        current_emotional_state = user_data.get("emotional_state", {})
        
        # Determine appropriate support level
        support_level = self.adjust_support_level(
            user_data.get("current_support_level", "minimal"),
            current_emotional_state
        )
        
        # Get support settings
        support_settings = self.get_support_settings(support_level)
        
        # Combine settings for final personality configuration
        personality_config = {
            "base_settings": interaction_patterns,
            "support_settings": support_settings,
            "conversation_style": self.determine_conversation_style(
                current_emotional_state.get("stability", 1.0)
            )
        }
        
        return personality_config