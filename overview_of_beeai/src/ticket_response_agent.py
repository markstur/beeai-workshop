# Copyright 2025 © BeeAI a Series of LF Projects, LLC
# SPDX-License-Identifier: Apache-2.0

# Standard
import asyncio
import os
import sys
import textwrap
from typing import Annotated

# Framework imports
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel

# A2A imports
from a2a.types import AgentCapabilities

# BeeAI SDK imports
import beeai_sdk.a2a.extensions
from beeai_sdk.a2a.extensions.ui.form import (
    DateField,
    TextField,
    FileField,
    CheckboxField,
    MultiSelectField,
    OptionItem,
    FormExtensionServer,
    FormExtensionSpec,
    FormRender,
)
from beeai_sdk.platform.configuration import SystemConfiguration
from beeai_sdk.platform.model_provider import ModelProvider
from beeai_sdk.server import Server
from beeai_sdk.a2a.extensions import AgentDetail
from beeai_sdk.a2a.types import Message, AgentMessage

# Using BeeAI Framework just to split provider from model name
from beeai_framework.backend.utils import parse_model

# Third Party
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants
AGENT_NAME = "Ticket Responder"
PORT_ENV_VAR = "TICKET_RESPONSE_AGENT_PORT"
PORT_DEFAULT = "10002"
PORT = os.environ.get(PORT_ENV_VAR, PORT_DEFAULT)
PROVIDER_ID = os.getenv("PROVIDER_ID")
MODEL_ID = os.getenv("MODEL_ID")
MODEL_NAME = ":".join([PROVIDER_ID, MODEL_ID]) if PROVIDER_ID and MODEL_ID else None

# Create the A2A server
server = Server()

# TODO:...
agent_detail_extension_spec = beeai_sdk.a2a.extensions.AgentDetailExtensionSpec(
    params=beeai_sdk.a2a.extensions.AgentDetail(
        interaction_mode="multi-turn",
    )
)

issue_summary = TextField(type="text", id="issue_summary", label="Issue summary", required=True, col_span=2)
customer_name = TextField(type="text", id="customer_name", label="Customer name", required=True, col_span=1)
account_id = TextField(type="text", id="account_id", label="Account ID", required=True, col_span=1)
product = TextField(type="text", id="product", label="Product", required=True, col_span=2)
incident_date = DateField(type="date", id="incident_date", label="Incident date", required=False, col_span=1)

severity = MultiSelectField(
    type="multiselect",
    id="severity",
    label="Severity",
    required=False,
    col_span=1,
    options=[
        OptionItem(id="critical", label="critical"),
        OptionItem(id="high", label="high"),
        OptionItem(id="medium", label="medium"),
        OptionItem(id="low", label="low"),
    ],
    default_value=["medium"],
)

sentiment = MultiSelectField(
    type="multiselect",
    id="sentiment",
    label="Sentiment",
    required=False,
    col_span=1,
    options=[
        OptionItem(id="negative", label="negative"),
        OptionItem(id="neutral", label="neutral"),
        OptionItem(id="positive", label="positive"),
    ],
    default_value=["neutral"],
)

category = MultiSelectField(
    type="multiselect",
    id="category",
    label="Category",
    required=False,
    col_span=2,
    options=[
        OptionItem(id="billing", label="billing"),
        OptionItem(id="technical", label="technical"),
        OptionItem(id="complaint", label="complaint"),
        OptionItem(id="account", label="account"),
        OptionItem(id="feedback", label="feedback"),
        OptionItem(id="other", label="other"),
    ],
)
notes = FileField(type="file", id="notes", label="Upload notes", accept=["text/*"], required=False, col_span=2)

form_render = FormRender(
    id="ticket_form",
    title="Ticket Details",
    columns=2,
    fields=[
        issue_summary,
        category,
        customer_name, account_id,
        severity, sentiment,
        product, incident_date
    ],
)
form_extension_spec = FormExtensionSpec(form_render)


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
    capabilities=AgentCapabilities(
        streaming=True,
        push_notifications=False,
        state_transition_history=False,
        extensions=[
            *form_extension_spec.to_agent_card_extensions(),
            *agent_detail_extension_spec.to_agent_card_extensions(),
        ],
    ),
)
# Create the Agent that uses the Pydantic AI framework
async def ticket_response_agent(input: Message,
                                form: Annotated[
                                    FormExtensionServer,
                                    form_extension_spec,
                                ],
                                ):
    """An agent that responds to customer support tickets."""

    try:
        form = form.parse_form_response(message=input)
        query = form.model_dump_json()
    except ValueError:
        query = input.model_dump_json()

    print("PARSED QUERY", query)

    # TODO: make this work w/o platform running!!!
    # TODO: make this work w/o platform running!!!
    # TODO: make this work w/o platform running!!!
    # TODO: make this work w/o platform running!!!
    global MODEL_NAME
    if not MODEL_NAME:
        system_config = await SystemConfiguration.get()
        model_from_platform = system_config.default_llm_model
        # model_from_platform = await ModelProvider.match()
        if model_from_platform:
            print("USING MODEL FROM PLATFORM: ", model_from_platform)
            # MODEL_NAME = model_from_platform[0].model_id
            MODEL_NAME = model_from_platform

    parsed_model = parse_model(MODEL_NAME)
    if parsed_model.provider_id == "ollama":
        if not os.getenv("OLLAMA_BASE_URL"):
            os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434/v1"  # Use ollama default

    model = OpenAIChatModel(model_name=parsed_model.model_id, provider=parsed_model.provider_id)
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
    return await ticket_response_agent(AgentMessage(text=query), form=FormExtensionServer(form_extension_spec))


def serve():
    """Start a server that runs the agent"""
    if PORT is None:
        server.run()  # Default port is 10000
    else:
        # Assign configured port
        # Note: 0=auto-assign but that is not supported by beeai platform registration
        server.run(port=int(PORT),
                   configure_telemetry=True)


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
