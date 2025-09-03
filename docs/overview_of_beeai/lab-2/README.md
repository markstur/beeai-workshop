---
title: BeeAI Workshop Lab 2
description: Create a multi-agent A2A workflow
logo: images/ibm-blue-background.png
---

# Create a Multi-Agent A2A Workflow

In this lab, we'll create a ticket agent that uses the triage agent and the response agent in a single workflow.

## Steps

### 1. Open the Project Directory

If you don't already have the `overview_of_beeai` folder open in VS Code, navigate there. Your working directory should look something like this: `~/beeai-workshop/overview_of_beeai`.

### 2. Install Dependencies

If you already did this in Lab 1, you can skip this step. If not, open your terminal (either in VS Code or using your preferred terminal) and install the dependencies:

```shell
uv sync
```

### 3. Run the Ticket Workflow Agent

In your terminal, run the ticket workflow agent (defaults to run on port 10000):

```shell
uv run src/ticket_workflow_agent.py
```

!!! insight
    If you take a look at the code you will notice (in the `ticket_workflow_agent.py` file) the main agent -- named "Ticket Agent" -- orchestrates the run of the `ticket_triage_agent` and `ticket_response_agent` sequentially. The `ticket_triage_agent` runs first and then its output is used as input for the `ticket_response_agent`.

### 4. Verify All Agents Are Running

You should have 2 terminals running the agents from lab 1.  You can verify this by downloading the agent cards using curl:

```shell
curl -X 'GET' 'http://localhost:10001/.well-known/agent-card.json' -H 'accept: application/json'
curl -X 'GET' 'http://localhost:10002/.well-known/agent-card.json' -H 'accept: application/json'
```

### 5. Execute the Ticket Workflow Agent

#### Option A: Use a curl command

In a separate terminal, run this curl command:

```shell
 curl -X 'POST' \
  'http://localhost:10000/' \
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
          "text": "Hi there, this is Jane Doe. Ever since yesterday your ProPlan keeps throwing \"Error 500\" whenever I try to export reports. This is blocking my quarter-end close—please fix ASAP or refund the month.AccountNumber: 872-55"
        }
      ],
      "role": "agent"
    }
  }
}'
```

#### Option B: Use your browser to use the FastAPI interface

1. In your browser navigate to [http://localhost:10000/docs](http://localhost:10000/docs)
2. Pull down **POST** `/` *Handle Requests*
3. Hit the `Try it out` button
4. In the `Request body`:

   - Find **params -> message -> parts** and in the first part (where kind=text) look for `"text": "string"` change the value of `string` to:

     ```text
     Hi there, this is Jane Doe. Ever since yesterday your ProPlan won't let me export reports. This is blocking my quarter-end close—please fix ASAP or refund the month.AccountNumber: 872-55
     ```

5. Click `Execute`
6. Scroll down to the server response

**Expected Results:**

You should see a human-like customer service response in the server response.

If you check the terminal where you are running the `ticket_workflow_agent.py`, you will see that it found Ticket Triager and printed the triage results, and then it found the Ticket Responder and printed the response. The result you saw above should be very similar to the result from the Ticket Responder.

Notice that when you are not using BeeAI Platform, the agents are only found by getting the port numbers that were set in the `.env` file (and assuming they are running on localhost).

### 6. Clean Up

Stop the three A2A agent servers using `Ctrl + C` or exiting the terminals where you have them running.
