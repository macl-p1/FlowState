"""Quick diagnostic: call the planner directly and print raw responses."""
import asyncio
import sys
sys.path.insert(0, ".")

from app.config import settings
from app.tools.registry import registry
from app.agents.planner import PlannerAgent

async def main():
    print(f"API Key: {settings.anthropic_api_key[:10]}...")
    print(f"Base URL: {settings.anthropic_base_url}")
    print(f"Model: {settings.anthropic_model}")
    print(f"Tools available: {[t.name for t in registry.list_all()]}")
    print()

    planner = PlannerAgent(tool_registry=registry)
    result = await planner.plan("send email notification whenever a new customer signs up, make sure to take their data from the API, transform it and store it in data base")

    print(f"Success: {result.success}")
    print(f"Error: {result.error}")
    print(f"Raw response:\n{result.raw_response}")

if __name__ == "__main__":
    asyncio.run(main())
