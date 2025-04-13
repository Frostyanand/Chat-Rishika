"""Main personality system implementation"""
import os
import logging
import random
from datetime import datetime
from typing import Dict, Any, Optional

from .personality_adaptation import PersonalityAdaptation
from .personality_evolution import PersonalityEvolution
from .personality_factory import PersonalityResponseFactory
from .utils.conversation_tracker import ConversationTracker
from .utils.emotion_analysis import EmotionAnalyzer
from .utils.phrase_bank import PhraseBank  # Updated import path

logger = logging.getLogger(__name__)

class ElysiaPersonalitySystem:
    """Main personality system that coordinates all personality components"""
    
    def __init__(self, storage_path: str = "./user_data"):
        """Initialize the personality system"""
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        # Initialize components
        self.factory = PersonalityResponseFactory()
        self.adaptation = PersonalityAdaptation(self.factory)
        
        # Set the personality_adaptation attribute of the factory to avoid circular dependency
        self.factory.personality_adaptation = self.adaptation
        
        self.evolution = PersonalityEvolution()
        self.conversation_tracker = ConversationTracker()
        self.emotion_analyzer = EmotionAnalyzer()
        self.phrase_bank = PhraseBank()
        
        logger.info("Personality system initialized")

    def process_message(self, user_id: str, message: str) -> str:
        """Process incoming user message and generate appropriate response"""
        try:
            # Track conversation stats
            self.conversation_tracker.add_message(user_id, message)
            
            # Analyze message
            analysis = self.emotion_analyzer.analyze(message)
            emotion = analysis.get("emotion", "neutral")
            emotion_intensity = analysis.get("intensity", 0.3)
            message_depth = analysis.get("depth", 0.2)
            
            # Update emotional trend tracking
            self.adaptation.update_emotional_trend(user_id, emotion, emotion_intensity)
            emotional_trend = self.adaptation.get_emotional_trend(user_id)
            
            # Calculate conversation depth score
            conversation_depth = min(0.9, (message_depth * 0.7) + (emotion_intensity * 0.3))
            
            # Get relationship stage and metrics
            relationship_data = self.evolution.get_relationship_data(user_id)
            relationship_stage = relationship_data.get("stage", "new")
            
            # Generate response components based on analysis
            response_components = []
            
            # 1. Handle emotional content first if strongly present
            if emotion != "neutral" and emotion_intensity > 0.4:
                primary_categories = []
                secondary_categories = []
                
                if emotion in ["sadness", "anger", "fear", "anxiety", "grief", "depression"]:
                    # Use phrase_bank directly to get comfort phrase for the emotion
                    comfort_response = self.phrase_bank.get_comfort_phrase(emotion)
                    if comfort_response:
                        response_components.append(comfort_response)
                        primary_categories.extend(["comfort", "validation"])
                        secondary_categories.extend(["encouragement", "presence"])
                elif emotion in ["joy", "excitement", "contentment"]:
                    response_components.append(self.phrase_bank.get_phrase("greetings"))
                    primary_categories.extend(["celebration", "encouragement"])
                    secondary_categories.extend(["light_conversation", "curiosity"])
                
                # Add layered response for emotional depth
                if primary_categories:
                    layered = self.phrase_bank.get_layered_response(
                        primary_categories=primary_categories,
                        secondary_categories=secondary_categories,
                        max_phrases=2
                    )
                    if layered:
                        response_components.append(layered)
            
            # 2. Add main response based on message content and context
            main_response = self.factory.generate_response(user_id, message, relationship_stage)
            if main_response:
                response_components.append(main_response)
            
            # 3. Add follow-up for deeper conversations
            if conversation_depth > 0.5:
                # Map relationship stage to appropriate follow-up categories
                if relationship_stage in ["new", "acquaintance"]:
                    secondary_categories = ["light_conversation", "curiosity"]
                elif relationship_stage in ["familiar", "close"]:
                    secondary_categories = ["connection_deepening", "personal_disclosure"]
                else:  # trusted, intimate stages
                    secondary_categories = ["deep_reflection", "emotional_exploration"]
                
                follow_up = self.phrase_bank.get_layered_response(
                    primary_categories=["follow_up"],
                    secondary_categories=secondary_categories,
                    max_phrases=1
                )
                if follow_up:
                    response_components.append(follow_up)
            
            # Combine components into final response
            response_components = [component.strip() for component in response_components if component and component.strip()]
            
            # Clean up response components to ensure proper spacing and punctuation
            formatted_components = []
            for component in response_components:
                # Skip empty components or components that might just be category labels
                if not component or len(component.split()) <= 1:
                    continue
                    
                # Make sure each component ends with proper punctuation
                if not component.endswith(('.', '!', '?')):
                    component = component + '.'
                
                formatted_components.append(component)
            
            # Join with proper spacing
            full_response = " ".join(formatted_components)
            
            # If we somehow don't have a response, use a default one
            if not full_response:
                full_response = self.phrase_bank.get_phrase("greetings", "I'm here to chat whenever you're ready.")
            
            # Update metrics
            self.evolution.update_metrics({
                "user_id": user_id,
                "message": message,
                "response": full_response,
                "emotion": emotion,
                "emotion_intensity": emotion_intensity,
                "depth_level": conversation_depth
            })
            
            return full_response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "I'm having trouble processing that right now. Could you try rephrasing it?"
    
    def get_relationship_stage(self, user_id: str) -> str:
        """Get current relationship stage with user"""
        try:
            relationship_data = self.evolution.get_relationship_data(user_id)
            return relationship_data.get("stage", "new")
        except Exception as e:
            logger.error(f"Error getting relationship stage: {e}")
            return "new"
    
    def get_time_appropriate_greeting(self, user_id: str) -> str:
        """Get a time and relationship-appropriate greeting"""
        try:
            hour = datetime.now().hour
            relationship_stage = self.get_relationship_stage(user_id)
            
            # Get appropriate greeting category based on relationship stage
            if relationship_stage in ["close", "trusted", "intimate"]:
                greeting_category = "greetings_close"
            elif relationship_stage in ["familiar", "acquaintance"]:
                greeting_category = "greetings_familiar"
            else:
                greeting_category = "greetings"
                
            greeting = self.phrase_bank.get_phrase(greeting_category, "Hello")
            
            # Add time-appropriate prefix
            if hour < 12:
                time_prefix = "Good morning!"
            elif hour < 17:
                time_prefix = "Good afternoon!"
            else:
                time_prefix = "Good evening!"
            
            return f"{time_prefix} {greeting}"
                
        except Exception as e:
            logger.error(f"Error generating greeting: {e}")
            return "Hello"