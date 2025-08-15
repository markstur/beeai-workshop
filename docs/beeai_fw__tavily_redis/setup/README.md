---
title: Setup Instructions
description: Setup the repo and pre-populate the vector store
logo: images/BeeAI-Logo-White.png
---

# Workshop Setup Instructions

## Get the Workshop Code

**Option A: Clone with Git (Recommended):**

```bash
git clone https://github.com/IBM/beeai-workshop.git
```

**Option B: Download ZIP:**

If you're not comfortable with Git, [download the ZIP](https://github.com/IBM/beeai-workshop/archive/refs/heads/main.zip) file and extract it to your desired location.

---

## Open the Workshop in VS Code

Navigate to the specific workshop folder and open it in VS Code:

```bash
cd beeai-workshop/beeai_fw_tavily_redis
code .
```

**Important:**  
Make sure to open the specific `beeai_fw_tavily_redis` folder in VS Code, not the entire `beeai-workshop` directory.  
This ensures proper project structure and dependencies are detected.

Alternatively, you can open VS Code first and use `File > Open Folder` to navigate to and select the correct folder.

---

## Set Up Environment Variables

Create a `.env` file based on the existing `env.template` at the `beeai_fw_tavily_redis` directory level.  

```bash
cp env.template .env
```

In your new .env file:

1. Add your `TAVILY_API_KEY` key
2. Add your `REDIS_URL` with your Redis database details (replace URL with your `Public endpoint` and PASSWORD with your `Default user password`)
3. Optionally, add your **OpenAI** key

---

## Install Project Dependencies

1. **Install all required dependencies:**

    ```bash
    uv sync
    ```

2. **Activate the virtual environment created by `uv`:**

    ```bash
    source .venv/bin/activate
    ```

This ensures you have the correct versions of all packages used in the workshop, installed in the correct environment.

---

## Populate the Vector Database

To prepare your Redis vector database for Retrieval-Augmented Generation (RAG):

!!! note
    This may take a couple of minutes depending on your device.

```bash
uv run src/redis_vector_db.py  
```
