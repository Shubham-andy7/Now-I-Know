import anthropic
from typing import List, Dict
import json
import asyncio

class ChatBot:
    def __init__(self, model="claude-3-haiku-20240307"):
        self.client = anthropic.Anthropic(
            api_key="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"
        )
        self.model = model
        self.conversation_history = []
        self.initial_question = "What do you know about AI?"
        self.conversation_history.append({
            "role": "assistant", 
            "content": self.initial_question
        })

    async def process_message(self, user_message: str) -> Dict[str, str]:
        # Add user message to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Generate next question using a separate method to maintain full history
        next_question = await self.generate_next_question()
        
        # Add the generated question to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": next_question
        })

        return {
            "question": next_question,
            "conversation_history": self.conversation_history
        }

    async def generate_next_question(self) -> str:
        # Construct a comprehensive prompt for generating the next question
        prompt = f"""
        You are an empathetic AI conversation partner. 
        Carefully analyze the conversation history and generate a thoughtful follow-up question.

        Conversation History:
        {json.dumps(self.conversation_history, indent=2)}

        Guidelines:
        - Create a question that directly relates to the user's most recent response
        - Show curiosity and genuine interest
        - Encourage deeper exploration of the topic
        - Use context from previous messages

        Return only the follow-up question.
        """
        
        try:
            # Send request to Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract and return the question
            return response.content[0].text.strip()
        
        except Exception as e:
            # Fallback question if generation fails
            return f"That's interesting. Could you tell me more about {' '.join(self.conversation_history[-1]['content'].split()[:3])}?"

    def get_conversation_history(self) -> List[Dict[str, str]]:
        return self.conversation_history

    def reset_conversation(self):
        self.conversation_history = [{
            "role": "assistant", 
            "content": self.initial_question
        }]

