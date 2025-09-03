# Copyright 2025 © BeeAI a Series of LF Projects, LLC
# SPDX-License-Identifier: Apache-2.0

# Standard
import asyncio
import os
import sys
import textwrap

# Framework imports
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel

# A2A imports
from a2a.types import AgentCapabilities

# BeeAI SDK imports
from beeai_sdk.server import Server
from beeai_sdk.a2a.extensions import AgentDetail
from beeai_sdk.a2a.types import Message, AgentMessage

# Third Party
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants
AGENT_NAME = "Ticket Responder"
PORT_ENV_VAR = "TICKET_RESPONSE_AGENT_PORT"
PORT = os.environ.get(PORT_ENV_VAR)
MODEL_ID = os.getenv("MODEL_ID")

# Create the A2A server
server = Server()


# Add the server decorator with the agent detail + capabilities as required by A2A
@server.agent(
    name=AGENT_NAME,
    detail=AgentDetail(
        ui_type="hands-off",
        user_greeting="Provide your triaged ticket details",
        framework="PydanticAI",
        license="Apache 2.0",
        language="Python",
    ),
    capabilities=AgentCapabilities(streaming=True)  # This must always be true for A2A
)
# Create the Agent that uses the Pydantic AI framework
async def ticket_response_agent(input: Message):
    """An agent that responds to customer support tickets."""

    query = input.model_dump_json()
    model = OpenAIChatModel(MODEL_ID)
    pydantic_agent = Agent(model=model,
                           system_prompt=(textwrap.dedent("""
                                           You are a helpful customer support agent that creates clear, helpful, human-sounding replies to a customer.
                                           Tone & Style Matrix:
                                            Category   | Primary Tone        | Secondary Goals
                                            Billing    | Efficient, courteous | Reassure accuracy, outline next steps, offer quick resolution
                                            Technical  | Clear, solution-oriented | Provide concise troubleshooting or escalation info
                                            Complaint  | Empathetic, apologetic | Acknowledge feelings, accept responsibility where appropriate, explain corrective action
                                            Account    | Professional, supportive | Clarify account status or changes, confirm security measures
                                            Feedback   | Appreciative, receptive | Thank the customer, highlight how feedback is used
                                            Other      | Warm, helpful        | Clarify intent, offer assistance
                                           """)))
    response = await pydantic_agent.run(query)
    return response.output


async def cli_agent(query: str):
    """Run an async agent with a query. await and return the result"""
    return await ticket_response_agent(AgentMessage(text=query))


def serve():
    """Start a server that runs the agent"""
    if PORT is None:
        server.run()  # Default port is 10000
    else:
        # Assign configured port
        # Note: 0=auto-assign but that is not supported by beeai platform registration
        server.run(port=int(PORT))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(f"RUNNING '{AGENT_NAME}' CLI:")
        print(f"INPUT TO '{AGENT_NAME}': {sys.argv[1]}")
        agent_response = asyncio.run(cli_agent(sys.argv[1]))
        print(f"OUTPUT FROM '{AGENT_NAME}':")
        print(agent_response)
    else:
        print(f"SERVING '{AGENT_NAME}'")
        serve()
