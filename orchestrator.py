from uagents import Agent, Context, Model, Bureau
from QuestionGenerator import QuestionGenerator
from ChatBot import ChatBot, ChatbotMessage, QuestionGenerationMessage
import asyncio

# Create the agents
interface_agent = Agent(
    name="interface_agent",
    seed="Interface Agent Recovery Phrase",
    port=8000,
    endpoint=["http://127.0.0.1:8000/submit"]
)

question_generator_agent = Agent(
    name="question_generator_agent",
    seed="Question Generator Agent Recovery Phrase",
    port=8001,
    endpoint=["http://127.0.0.1:8001/submit"]
)

# Initialize the components
interface = ChatBot()
question_generator = QuestionGenerator()

@interface_agent.on_event("startup")
async def startup(ctx: Context):
    """Initialize conversation on startup"""
    ctx.logger.info("Interface is starting")
    message = interface.get_last_user_response()
    await ctx.send(question_generator_agent.address, message)

@interface_agent.on_message(QuestionGenerationMessage)
async def handle_interface_message(ctx: Context, sender: str, msg: QuestionGenerationMessage):
    """Handle messages received by interface agent"""
    ctx.logger.info(f"Received message from {sender}")
    next_question, user_response = await interface.continue_conversation(msg.message)
    
    new_message = ChatbotMessage(content=user_response)
    await ctx.send(question_generator_agent.address, new_message)

@question_generator_agent.on_message(ChatbotMessage)
async def handle_generator_message(ctx: Context, sender: str, msg: ChatbotMessage):
    """Handle messages received by question generator"""
    try:
        response = await question_generator.generate_next_question_and_emotion(
            msg.conversation_history,
            msg.content
        )
        
        response_message = QuestionGenerationMessage(message=response)
        await ctx.send(sender, response_message)
        
    except Exception as e:
        ctx.logger.error(f"Error in question generator: {e}")
        error_message = QuestionGenerationMessage(message={
            "question": "Could you tell me more about that?",
            "emotional_state": "neutral"
        })
        await ctx.send(sender, error_message)

def run():
    """Run the bureau"""
    bureau = Bureau()
    bureau.add(interface_agent)
    bureau.add(question_generator_agent)
    
    # Run the bureau directly
    bureau.run()

if __name__ == "__main__":
    # Run without explicit asyncio.run()
    run()