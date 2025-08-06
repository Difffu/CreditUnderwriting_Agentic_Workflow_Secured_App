import asyncio
from dotenv import load_dotenv
load_dotenv()
from browser_use import Agent
from browser_use.llm import ChatGoogle

from google.genai import types

config = types.GenerateContentConfigDict(
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
)

prompt = """
login to gmail using the following credentials:
email: dipesh.divyanshu@greenridertech.com
password: Shashi@520741

then open gmail and draft a a mail to shashikalakurrey78@gmail.com mentioning I love you and send it
"""

async def main():
    agent = Agent(
        task=prompt,
        llm=ChatGoogle(model="gemini-2.0-flash", temperature=1.0, config=config),
        use_vision=True,
        max_actions_per_step=1000
    )
    await agent.run()

asyncio.run(main())