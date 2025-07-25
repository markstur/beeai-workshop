---
title: Create Tools
description: Create the tools to enable the AI agent
logo: images/BeeAI-Logo-White.png
---


# Tool Development: Tavily Internet Search + Redis RAG

> ⚠️ **Before you begin:**  
> Make sure you have completed the [Prework](../pre-work/README.md) and [Setup](../setup/README.md) instructions.  
> The tools rely on environment configuration, the redis stack to be running, dependencies, and your `.env` file.

In this section of the workshop, you'll build two essential tools that power your company assistant:

1. **Web Search Tool** using a locally run **Tavily MCP server**
2. **Redis Retriever Tool** for enabling **Retrieval-Augmented Generation (RAG)** from your vector database

Each tool is implemented interactively. You’ll fill in missing logic and test each script on its own before integrating it into your assistant.

---

## Part 1: Tavily MCP Tool

### Step 1: Locate the Tool File

Navigate to the following file:

```text
beeai-tavily-redis/tavily_mcp_tool.py
```

Some parts of the implementation are left incomplete. Follow the in-line comments to fill them in. If you need help, check the solution:

```text
solutions/tavily_mcp_tool.py
```

### Step 2: Verify Your Environment

1. **Navigate to the correct directory:**

```bash
cd beeai-workshop/beeai-tavily-redis
```

2. **Activate your virtual environment:**

```bash
source .venv/bin/activate
```

3. **Install dependencies:**

```bash
uv sync
```

### Step 3: Run the Tool

Run or debug the Tavily tool independently to test its functionality:

```bash
uv run src/tavily_mcp_tool.py
```

---

## Part 2: Redis Retriever Tool

### Step 1: Locate the Tool File

Navigate to:

```text
beeai-tavily-redis/redis_retriever.py
```

Some sections of the code are incomplete. Fill in the missing parts as instructed by comments in the file. You can check your work using the solution file:

```text
solutions/redis_retriever.py
```

### Step 2: Verify Your Environment

If you've just completed Part 1, your environment should still be active. Otherwise:

```bash
cd beeai-workshop/beeai-tavily-redis
source .venv/bin/activate
uv sync
```

### Step 3: Run the Tool

Run or debug your Redis retriever tool independently:

```bash
uv run src/redis_retriever.py
```

This ensures the tool works as expected before integrating it into your BeeAI Agent!
