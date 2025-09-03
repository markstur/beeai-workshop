---
title: Use the BeeAI Platform
description: Run the BeeAI Platform and use your agents in the UI
logo: images/ibm-blue-background.png
---

# Interact with Your Agents in the BeeAI Platform

In this lab, we'll run our Ticket Agent that we created in Lab 2 in the BeeAI platform. The BeeAI platform creates a simple and elegant UI so that we can test, run, and share our agents easily.

## Steps

### 1. Install BeeAI Platform

Install BeeAI platform using the [installation instructions in the documentation](https://docs.beeai.dev/introduction/installation). Be sure to complete all parts of installation and setup:

!!! insight
    Be sure to install a version that was tested with the workshop with this syntax `uv tool install beeai-cli==<version>`.

1. Install uv (part of pre-work section)

2. Install BeeAI

    ```shell
    uv tool install beeai-cli==0.3.1
    ```

3. Start the BeeAI platform

    ```shell
    beeai platform start
    ```

4. Configure an LLM provider

    ```shell
    beeai env setup
    ```

5. Check that everything works

    ```shell
    beeai run chat Hi!
    ```

Already installed BeeAI in the past? Be sure to update it to the latest version according to the instructions in the documentation.

### 2. Open the Project Directory

If you don't already have the `overview_of_beeai` folder open in VS Code, navigate there. Your working directory should look something like this: `~/beeai-workshop/overview_of_beeai`.

### 3. Install Dependencies

If you already did this in Lab 1 or 2, you can skip this step. If not, open your terminal (either in VS Code or using your preferred terminal) and install the dependencies:

```shell
uv sync
```

### 4. Run the Ticket Workflow Agent

In your 3 terminals, run the 3 agents again (one of these commands in each terminal):

```shell
uv run src/ticket_triage_agent.py
uv run src/ticket_response_agent.py
uv run src/ticket_workflow_agent.py
```

!!! insight
    If you take a look at the code pay special attention to the metadata in the `@server.agent` decorator. The metadata is used by the BeeAI Platform UI.

### 5. Launch the BeeAI UI

In your terminal, run:

```shell
beeai ui
```

You should see the UI launch in your browser.

!!! insight
    If you navigate to the menu bar on the left hand side you will see a list of agents. All 3 agents that we are running on the active server appear because they each have UI metadata in their agent detail. If we killed the server, these agents would instantly disappear.

### 6. Run the Ticket Agent in the BeeAI Platform

1. Navigate to the menu bar on the left hand side and select the Ticket Agent
2. Enter in the sample text or have fun with coming up with your own ticket:

    ```text
    Hi there, this is Jane Doe. Ever since yesterday your ProPlan won't let me export reports. This is blocking my quarter-end close—please fix ASAP or refund the month.AccountNumber: 872-55
    ```

3. Press `Run`

**Expected Results:**

You should see a human-like customer service response in the server response.

If you check the terminal where you are running the `ticket_workflow_agent.py`, you will see that it found Ticket Triager and printed the triage results, and then it found the Ticket Responder and printed the response. The result you saw above should be very similar to the result from the Ticket Responder.

In the output from the `ticket_workflow_agent.py`, you will see the status of `Attempting to find agents using BeeAI Platform`.  When you do not have BeeAI Platform running (as in Lab 2) the A2A agents are only found using the configured ports in the .env file.  When you have BeeAI Platform running, the agents self-register on start-up. With the BeeAI platform the Ticket Agent can find (and run) the other agents using BeeAI Platform.

### 7. Clean Up

1. Stop the 3 agent servers using `Ctrl + C` or exiting the terminal where it is running.
2. Clean up the platform by running this command in your terminal:

    ```shell
    beeai platform delete
    ```

## Congratulations! You've completed the Overview of BeeAI Workshop.