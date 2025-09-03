---
title: BeeAI Workshop Lab 1
description: Create and invoke A2A agents
logo: images/ibm-blue-background.png
---

# Create and Invoke A2A Agents

In this lab, you will invoke 2 agents using the BeeAI SDK with A2A (the Python code is provided). One agent is written using the BeeAI Framework and the other agent is written using PydanticAI. We are using 2 different frameworks to illustrate how easy it is to make any agent A2A-compatible with the BeeAI SDK.

**Agent Overview:**

- **Agent 1 (BeeAI Framework)**: "Triage Agent" – categorizes the ticket (e.g., billing, tech, complaint) and extracts key facts in a structured way (e.g., using tags, severity, sentiment).
- **Agent 2 (PydanticAI)**: "Response Agent" – takes the structured summary and crafts a tone-specific response (e.g., empathetic for complaints, efficient for billing).

!!! prerequisite
    The following steps assume that you have already completed the pre-work section. If not, please return to the previous section before moving forward.

## Steps

### 1. Open the Project Directory

If you don't already have the `overview_of_beeai` folder open in VS Code, navigate there. Your working directory should look something like this: `~/beeai-workshop/overview_of_beeai`.

### 2. Install Dependencies

Open your terminal (either in VS Code or using your preferred terminal) and install the dependencies:

```shell
uv sync
```

### 3. Run the Ticket Triage Agent

In your terminal, run the ticket triage agent (defaults to run on port 10001):

```shell
uv run src/ticket_triage_agent.py
```

!!! insight
    If you take a look at the code you will notice that the agent is wrapped in an `@server.agent` decorator. The decorator makes it an A2A agent and the metadata provides agent details for discoverability.

### 4. Test the Agent via Browser Interface

Use your browser to invoke the `ticket_triage_agent` using the FastAPI interface:

1. In your preferred browser navigate to [http://localhost:10001/docs](http://localhost:10001/docs)
2. Pull down **GET** `/.well-known/agent-card.json` *Handle Get Agent Card*
3. Hit the `Try it out` button and then click `Execute`

**Expected Results:**

Under `Responses`:

- Under `Response body`, the result shows the details for the agent named `Ticket Triager`.
- Under `Curl`, you get the curl command that you can run in a terminal (instead of using the UI)

**Try the curl command:** In a new terminal window, run:

```shell
curl -X 'GET' \
  'http://localhost:10001/.well-known/agent-card.json' \
  -H 'accept: application/json'
```

!!! insight
    This shows you that your A2A agent is discoverable on port 10001 and is served and available. A server hosts one agent.

### 5. Run the Ticket Response Agent

In a separate terminal, run the ticket response agent (defaults to run on port 10002):

```shell
uv run src/ticket_response_agent.py
```

!!! insight
    Notice how the `ticket_triage_agent` and `ticket_response_agent` are running on separate ports. Agents have their own server and are discoverable on separate ports (as you will see in a later lab with BeeAI Platform).

### 6. Invoke the Response Agent

Invoke the response agent using a curl command. Remember that the `ticket_response_agent` expects a formatted output from the `ticket_triage_agent` as its input. You'll put these together in a sequential workflow in lab 2.

In a separate terminal, run this curl command:

```shell
 curl -X 'POST' \
  'http://localhost:10002/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "id": "string",
  "jsonrpc": "2.0",
  "method": "message/send",
  "params": {
    "message": {
      "kind": "message",
      "messageId": "string",
      "parts": [
        {
          "kind": "text",
          "text": "{\"category\":[\"Technical\"],\"customer_name\":\"Jane Doe\",\"account_id\":\"872-55\",\"product\":\"ProPlan\",\"issue_summary\":\"ProPlan product is throwing \\\"Error 500\\\" when exporting reports since yesterday, blocking quarter-end close.\",\"severity\":\"high\",\"sentiment\":\"negative\",\"incident_date\":\"2024-06-11\"}"
        }
      ],
      "role": "agent"
    }
  }
}'
```

**Expected Results:**

In the response body, you should see an appropriate human-like ticket agent response.

### 7. Clean Up

If you are continuing the workshop you should leave these servers running for the following labs. When you are ready to stop the A2A agent servers use `Ctrl + C` where they are running. You can always start them again with the `uv run` commands above.
