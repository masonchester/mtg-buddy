from openai import AsyncOpenAI
from agents import (
    Agent, 
    Runner,
    set_default_openai_client,
    set_default_openai_api,
    set_tracing_disabled)
from mtg_buddy import tool

SYSTEM_PROMPT = """
Role: You are an Magic: The Gathering card information agent. Your role is to assist users in finding information surroding Magic: The Gathering cards.

Context: Users will make queries about Magic: The Gathering cards revolving around cards attributes. 
A sample question could be as such, "What does Sol Ring do?".

Assignment: You will do the following to answer a users questions with the avaliable tools at your 
disposal to query for card information given the name of the card.
- Always call get_card before answering.
- Only state facts that appear in the tool result.
- If found is false, say so or offer the suggestions. Never guess.

Output: Output your findings in plain text.
"""

async def run_agent(message: str) -> str:

    ollama_client = AsyncOpenAI(base_url='http://localhost:11434/v1', api_key='not-needed')
    set_default_openai_client(ollama_client)
    set_default_openai_api('chat_completions')
    set_tracing_disabled(True)


    agent = Agent(
        name='MTG Buddy',
        instructions=SYSTEM_PROMPT,
        model="qwen3:4b",
        tools=[tool.get_card]
    )

    results = await Runner.run(agent, message, max_turns=6)

    return results.final_output
