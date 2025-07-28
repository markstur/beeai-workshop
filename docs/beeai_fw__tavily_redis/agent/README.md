---
title: Built Agent
description: Build the AI Agent
logo: images/BeeAI-Logo-White.png
---
# Running the Agent

> ⚠️ **Before you begin:**  
> Make sure you’ve completed the [Prework](../pre-work/README.md) and [Setup](../setup/README.md) sections.  
> Your `.env` must include either an **OpenAI API key** or your **local Ollama model** must be running.

---

## Step 1: Prepare to Run the Agent

1. Navigate to the following file:

    ```text
    beeai-tavily-redis/agent.py
    ```

2. This file contains **fill-in-the-blank** sections. Follow the in-line comments to complete the logic.

    - **Uncomment the language model** you intend to use:
        - Use `OpenAI` if your API key is in `.env`
        - Use `Ollama` if you're running `granite3.3:8b` locally

    If you are using **Ollama**:

    ```bash
    ollama run granite3.3:8b
    ```

    If you are using **OpenAI**, your `.env` file must include your API key:

    ```env
    OPENAI_API_KEY=your-key-here
    ```

    - Be sure to **add the tools you implemented earlier** (Tavily MCP Tool and Redis Retriever).
    - You can read more about tool usage in the BeeAI Framework here:  
        👉 [Tool Usage Documentation](https://framework.beeai.dev/modules/tools)

---

## Step 2: Understand the Agent

Read the `system_prompt` variable in the file.  
It defines how the assistant should behave and respond to users.

To learn more about how the BeeAI **Requirement Agent** works:  
👉 [Requirement Agent Documentation](https://framework.beeai.dev/experimental/requirement-agent)

Also, explore the `conditional_requirements` section — this allows you to control **how and when** specific tools should be used.

👉 View the complete argument reference here:  
[Conditional Requirements Reference](https://framework.beeai.dev/experimental/requirement-agent#complete-parameter-reference)

---

## Step 3: Verify Environment

1. Navigate to the working directory:

    ```bash
    cd beeai-workshop/beeai-tavily-redis
    ```

2. Activate your virtual environment:

    ```bash
    source .venv/bin/activate
    ```

3. Sync dependencies:

    ```bash
    uv sync
    ```

---

## Step 4: Run the Agent

Execute or debug the agent script:

```bash
uv run agent.py
```

You’ll be prompted to enter a question in your terminal. You can ask your own or try one of these examples:

### Sample Questions

- Tell me about the new pilot. Who is the target audience?
- What options do we have for vegetarians?
- I haven't gotten my order of french fries for 3 days and we are running low. This will start to affect operations. What do I do?
- Who do I call if there is an event in my store and I think it might turn into a PR emergency?

> 💡 If asking your own questions, remember:  
> The agent only knows what’s in its vector store documents and what the prompt instructs it to do.
