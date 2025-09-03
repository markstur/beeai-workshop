# Copyright 2025 © BeeAI a Series of LF Projects, LLC
# SPDX-License-Identifier: Apache-2.0

# Standard
import asyncio
import json
import os
import pprint
import sys
from typing import List, Optional

# Framework imports
from beeai_framework.agents.experimental import RequirementAgent
from beeai_framework.backend.chat import ChatModel
from beeai_framework.middleware.trajectory import GlobalTrajectoryMiddleware

# A2A imports
from a2a.types import AgentCapabilities
from beeai_sdk.a2a.types import Message, AgentMessage
from beeai_sdk.server import Server
from beeai_sdk.a2a.extensions import AgentDetail

# Third Party
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants
AGENT_NAME = "Ticket Triager"
PORT_ENV_VAR = "TICKET_TRIAGE_AGENT_PORT"
PORT = os.environ.get(PORT_ENV_VAR)
PROVIDER_ID = os.getenv("PROVIDER_ID")
MODEL_ID = os.getenv("MODEL_ID")
MODEL_NAME = ":".join([PROVIDER_ID, MODEL_ID])


# Create the A2A Server
server = Server()


# Create the data model for the structured output
class TicketClassifierOutput(BaseModel):
    """Structured payload returned by the LLM for a single ticket."""
    category: List[str] = Field(
        description="Options: Billing, Technical, Complaint, Account, Feedback, Other"
    )
    customer_name: Optional[str] = Field(
        default=None,
        description="Full customer name; null if not mentioned."
    )
    account_id: Optional[str] = Field(
        default=None,
        description="Exact account identifier as it appears in the ticket."
    )
    product: Optional[str] = Field(
        default=None,
        description="Product/SKU referenced in the ticket."
    )
    issue_summary: str = Field(
        description="concise plain-language summary of the problem, extracting key insights."
    )
    severity: str = Field(
        description='One of: "critical", "high", "medium", "low".'
    )
    sentiment: str = Field(
        description='One of: "negative", "neutral", "positive".'
    )
    incident_date: Optional[str] = Field(
        default=None,
        description="ISO-8601 date (YYYY-MM-DD) if provided."
    )


# Add the server decorator and agent detail + capabilities as required by A2A 
@server.agent(
    name=AGENT_NAME,
    detail=AgentDetail(
        ui_type="hands-off",
        user_greeting="Enter your ticket details",
        framework="BeeAI",
        license="Apache 2.0",
        language="Python",
    ),
    capabilities=AgentCapabilities(streaming=True)  # This must always be true for A2A
)
# Create the function for the BeeAI Agent
async def ticket_triage_agent(input: Message) -> str:
    """An agent that classifies and summarizes customer support tickets."""

    requirement_agent = RequirementAgent(
        llm=ChatModel.from_name(MODEL_NAME),
        instructions="""
            You are “Support-Sensei.”
            1) Choose the single best ticket category.
            2) Extract the required fields.
            Return ONLY a single top-level JSON object that matches the schema.
            """,
        # Use middlewares for lots of great output and optionally
        # add excluded if you want to narrow it down.
        # middlewares=[
            # GlobalTrajectoryMiddleware(
                # pretty=True,
                # excluded=[
                #     ChatModel,
                #     RequirementAgent,
                #     Requirement,
                #     Tool,
                # ]
            # )],
    )

    result = await requirement_agent.run(
        prompt=input.model_dump_json(),
        expected_output=TicketClassifierOutput,
    )
    return result.answer_structured.model_dump_json()


async def cli_agent(query: str):
    """Run an async agent with a query, await and return the result"""
    return await ticket_triage_agent(AgentMessage(text=query))


def serve():
    """Start a server that runs the agent"""
    if PORT is None:
        server.run()  # Default port is 10000
    else:
        # Assign configured port
        # Note: 0=auto-assign but that is not supported for BeeAI Platform registration
        server.run(port=int(PORT))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(f"RUNNING '{AGENT_NAME}' CLI:")
        print(f"INPUT TO '{AGENT_NAME}': {sys.argv[1]}")
        agent_response = asyncio.run(cli_agent(sys.argv[1]))
        print(f"OUTPUT FROM '{AGENT_NAME}':")
        pprint.pprint(json.loads(agent_response), indent=4)
    else:
        print(f"SERVING '{AGENT_NAME}'")
        serve()
