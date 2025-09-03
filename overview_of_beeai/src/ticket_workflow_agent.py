# Copyright 2025 © BeeAI a Series of LF Projects, LLC
# SPDX-License-Identifier: Apache-2.0

# Standard
import asyncio
import json
import os
import pprint
import sys
from typing import Any, Dict

# A2A imports
from a2a.types import AgentCapabilities

# BeeAI Framework imports
from beeai_framework.adapters.beeai_platform import BeeAIPlatformAgent
from beeai_framework.agents.experimental import RequirementAgent
from beeai_framework.agents.experimental.requirements.conditional import ConditionalRequirement
from beeai_framework.backend import ChatModel
from beeai_framework.middleware.trajectory import GlobalTrajectoryMiddleware
from beeai_framework.tools import Tool
from beeai_framework.tools.handoff import HandoffTool
from beeai_framework.tools.think import ThinkTool
from beeai_framework.adapters.a2a.agents import A2AAgent
from beeai_framework.memory.unconstrained_memory import UnconstrainedMemory
from beeai_framework.tools import tool

# BeeAI SDK imports
from beeai_sdk.a2a.extensions import AgentDetail
from beeai_sdk.a2a.types import AgentMessage, Message
from beeai_sdk.server import Server

# Third Party
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Local
from ticket_triage_agent import AGENT_NAME as TICKET_TRIAGE_AGENT
from ticket_triage_agent import PORT_ENV_VAR as TICKET_TRIAGE_PORT_ENV_VAR
from ticket_response_agent import AGENT_NAME as TICKET_RESPONSE_AGENT
from ticket_response_agent import PORT_ENV_VAR as TICKET_RESPONSE_PORT_ENV_VAR


# Load environment variables from .env file (before setting log levels)
load_dotenv()

# Constants
AGENT_NAME = "Ticket Agent"
PORT_ENV_VAR = "TICKET_AGENT_PORT"
PORT = os.environ.get(PORT_ENV_VAR)
USE_PLATFORM = os.environ.get("USE_PLATFORM", "false").lower() not in ["0", "false", "off"]
PLATFORM_URL = os.environ.get("PLATFORM_URL", "http://127.0.0.1:8333")
PROVIDER_ID = os.getenv("PROVIDER_ID")
MODEL_ID = os.getenv("MODEL_ID")
MODEL_NAME = ":".join([PROVIDER_ID, MODEL_ID])

# Keep a map of the triager and responder which will be discovered using the
# BeeAI Platform or using ports configured for individual local servers.
REMOTE_AGENTS = [TICKET_RESPONSE_AGENT, TICKET_TRIAGE_AGENT]  # The 2 remote agents to be found
AGENT_PORTS = [  # Configured local ports to use when not registering with BeeAI Platform
    (TICKET_TRIAGE_AGENT, TICKET_TRIAGE_PORT_ENV_VAR),
    (TICKET_RESPONSE_AGENT, TICKET_RESPONSE_PORT_ENV_VAR),
]
AGENTS: Dict[str, BeeAIPlatformAgent | A2AAgent] = {}


# Create the A2A server
server = Server()


async def find_agents():
    """Find and refresh agents using BeeAI platform if available, else using configured local ports."""

    global AGENTS

    if USE_PLATFORM:
        print(f"Attempting to find agents using BeeAI Platform because USE_PLATFORM={USE_PLATFORM}")
        try:
            platform_agents = await BeeAIPlatformAgent.from_platform(url=PLATFORM_URL, memory=UnconstrainedMemory())
            AGENTS.update({pa.name: pa for pa in platform_agents if pa.name in REMOTE_AGENTS})
        except Exception as e:
            print(f"Attempting to find agents using BeeAI Platform at {PLATFORM_URL} exception: {e}")
        for name in AGENTS:
            print(f"FOUND AGENT '{name}' USING BEEAI PLATFORM")
    else:
        print(f"Not attempting to find agents using BeeAI Platform because USE_PLATFORM={USE_PLATFORM}")


    # Fill in any missing remote ticket agents with local A2AAgent runnables
    for name, env_var in AGENT_PORTS:
        if name not in AGENTS:
            print(f"Attempting to use configured local ports for remote agent '{name}'")
            port = os.environ.get(env_var)
            if port is None:
                raise Exception(f"{env_var} must be set in .env")
            url = f"http://127.0.0.1:{port}"
            AGENTS[name] = A2AAgent(url=url, memory=UnconstrainedMemory())
            print(f"AGENT '{name}' IS CONFIGURED TO USE {url} WITH BEEAI FRAMEWORK A2A ADAPTER")


async def remote_agent_run(agent_name: str, query: str) -> str:
    """Run remote agent using BeeAI Platform or local servers."""

    # Get agent by name from map of available agents
    agent = AGENTS.get(agent_name)
    if not agent:  # Init or refresh the AGENTS map and try again
        await find_agents()
        agent = AGENTS.get(agent_name)

    if not agent:
        raise Exception(f"{agent_name} not found using BeeAI Platform or locally configured ports")

    ret = await agent.run(query)
    return ret.result.text


class TicketInput(BaseModel):
    text: str = Field(..., description="The ticket descriptive text.")


@tool(input_schema=TicketInput)
async def ticket_response_tool(text: str) -> [AgentMessage]:
    """Response tool that takes classified ticket and response..."""

    result = await remote_agent_run(TICKET_RESPONSE_AGENT, str(text))
    print(f"RESULT FROM '{TICKET_RESPONSE_AGENT}': ", result)
    return result


@tool(input_schema=TicketInput)
async def ticket_triage_tool(text: str) -> [AgentMessage]:
    """Triage tool that takes user input and classifies it for a ticket."""

    result = await remote_agent_run(TICKET_TRIAGE_AGENT, str(text))
    print(f"RESULT FROM '{TICKET_TRIAGE_AGENT}': ", result)
    pprint.pprint(json.loads(result), indent=4)
    return result


# Add the server decorator with the agent detail + capabilities as required by A2A
@server.agent(
    name=AGENT_NAME,
    detail=AgentDetail(
        ui_type="hands-off",
        user_greeting="Enter your ticket details",
        framework="BeeAI",
        license="Apache 2.0",
        language="Python",
    ),
    capabilities=AgentCapabilities(streaming=True)
)
async def ticket_agent(input: Message) -> dict[str, Any]:

    response_agent = RequirementAgent(
        llm=ChatModel.from_name(MODEL_NAME),
        tools=[ticket_response_tool],
        requirements=[
            ConditionalRequirement(ticket_response_tool, force_at_step=1),
        ],
        role="Ticket Response Specialist",
        instructions="Provide a helpful response to a user that submitted a ticket.",
    )

    response_handoff_tool = HandoffTool(
        response_agent,
        name="TicketResponseTool",
        description="Craft an empathetic response to a user that submitted a ticket.",
    )
    triage_agent = RequirementAgent(
        llm=ChatModel.from_name(MODEL_NAME),
        tools=[ticket_triage_tool],
        requirements=[
            ConditionalRequirement(ticket_triage_tool, force_at_step=1),
        ],
        role="Support Triage Specialist",
        instructions="You specialize in categorizing incoming tickets. Use the ticket_triage_tool to do the classification.",
        notes=[
            "Always use the ticket_triage_tool first to properly classify incoming tickets.",
            "Always use the output from the ticket_triage_tool as your output.",
            "If the tool throws an error respond with the error information for troubleshooting.",
        ]
    )

    triage_handoff_tool = HandoffTool(
        triage_agent,
        name="TicketTriageTool",
        description="Triage an incoming issue to categorize and summarize it for a ticket.",
    )

    main_agent = RequirementAgent(
        name="MainAgent",
        llm=ChatModel.from_name(MODEL_NAME),
        tools=[
            # ThinkTool(),
            triage_handoff_tool,
            response_handoff_tool,
        ],
        requirements=[
            ConditionalRequirement(triage_handoff_tool, force_at_step=1, min_invocations=1),
            ConditionalRequirement(response_handoff_tool, force_after=triage_handoff_tool, min_invocations=1),
        ],
        # Log all tool calls to the console for easier debugging
        # middlewares=[GlobalTrajectoryMiddleware(included=[Tool])],
        role="General Support Specialist",
        instructions="Use your tools to makes sure ticket input is properly categorized and respond using the responder tool",
        notes=[
            "You perform better when you use the ThinkTool tool first. Use it to plan your reasoning and determine which other tools to use next.",
            "Always use the triage_handoff_tool first to properly classify incoming tickets.",
            "Always use the output from the triage_handoff_tool as input to the response_handoff_tool.",
            "The response_handoff_tool will craft a response using an appropriate tone depending on the classification categories.",
            "If either tool throws an error respond with the error information for troubleshooting.",
            "You must use the response from the response_handoff_tool whenever possible without rewording.",
        ]
    )

    result = await main_agent.run(
        prompt=input.model_dump_json(),
        expected_output="Helpful and clear response.")

    return result.answer.text


async def cli_agent(query: str):
    """Run an async agent with a query. await and return the result"""
    return await ticket_agent(AgentMessage(text=query))


def serve():
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
