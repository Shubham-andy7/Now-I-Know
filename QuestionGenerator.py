import anthropic
from uagents import Agent, Context, Model, Bureau
import json
import asyncio
import os

class QuestionGenerationContext(Model):
    """
    Model to define the structure of context passed to the agent
    """
    conversation_history: list
    user_response: str

class QuestionGenerator:
    def __init__(self, api_key=None, model="claude-3-haiku-20240307"):
        """
        Initialize the Question Generation Agent with Anthropic Claude.
        
        Args:
            api_key (str, optional): Anthropic API key
            model (str, optional): Claude model to use
        """
        self.client = anthropic.Anthropic(api_key="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")
        self.model = model

    async def generate_next_question_and_emotion(self, conversation_history, user_response):
        """
        Generate the next question and determine emotional state using Claude.
        
        Args:
            conversation_history (list): Full conversation history
            user_response (str): Latest user response
        
        Returns:
            dict: Contains next question and emotional state
        """
        try:
            # Construct a comprehensive prompt for Claude
            prompt = f"""
            You are an advanced AI conversation architect tasked with:
            1. Analyzing the conversation history
            2. Understanding the nuances of the user's most recent response
            3. Generating a thought-provoking, contextually relevant next question
            4. Identifying the user's underlying emotional state

            Conversation History:
            {json.dumps(conversation_history, indent=2)}

            Latest User Response:
            {user_response}

            Task Guidelines:
            - Extract key terms and themes from the user's response
            - Create a question that:
              a) Builds directly on the user's previous input
              b) Uses specific terminology from their response
              c) Encourages deeper exploration of the topic
            
            Emotional State Analysis:
            - Assess the emotional undertones of the response
            - Categorize the emotional state (e.g., excited, anxious, curious, confused)
            - The state should reflect the user's tone, word choice, and implied sentiment

            Output Format (JSON):
            {
                "question": "Carefully crafted next question",
                "emotional_state": "detected emotional state"
            }
            """
            
            # Send request to Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=300,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse the response
            generated_content = response.content[0].text.strip()
            
            # Attempt to parse as JSON, with fallback
            try:
                parsed_response = json.loads(generated_content)
            except json.JSONDecodeError:
                # If JSON parsing fails, create a manual dictionary
                parsed_response = {
                    "question": generated_content.split('\n')[0],
                    "emotional_state": self._detect_emotional_state(user_response)
                }
            
            return parsed_response
        
        except Exception as e:
            return {
                "question": f"I'm intrigued by your response. Could you tell me more about {' '.join(user_response.split()[:3])}?",
                "emotional_state": "neutral"
            }

    def _detect_emotional_state(self, response):
        """
        Fallback method to detect emotional state if Claude's response is inconclusive.
        
        Args:
            response (str): User's response
        
        Returns:
            str: Detected emotional state
        """
        # Simple heuristics to detect emotional state
        excitement_keywords = ['wow', 'amazing', 'excited', 'fantastic', 'awesome']
        anxiety_keywords = ['worried', 'concerned', 'nervous', 'uncertain', 'scared']
        confusion_keywords = ['confused', 'unclear', 'don\'t understand', 'what do you mean']
        
        response_lower = response.lower()
        
        if any(word in response_lower for word in excitement_keywords):
            return 'excited'
        elif any(word in response_lower for word in anxiety_keywords):
            return 'anxious'
        elif any(word in response_lower for word in confusion_keywords):
            return 'confused'
        else:
            return 'neutral'