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
Add your **Tavily** key and optionally your **OpenAI** key to this file.

```bash
cp env.template .env
```

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

1. **Ensure the correct kernel is selected:**

    The notebook should use the Python environment from your `.venv`. If it’s not available in the kernel list:

    - Open the Command Palette in VS Code (`Cmd+Shift+P` or `Ctrl+Shift+P`)
    - Select `Python: Select Interpreter`
    - If your `.venv` is not listed, add it manually:

        - Choose `Enter interpreter path`
        - Browse to:

        ```text
        beeai_fw_tavily_redis/.venv/bin/python
        ```

        - Select that path to register and use it as the kernel

    This ensures all required packages and dependencies are correctly loaded in the notebook environment.

2. **Run the Jupyter notebook:**

    Run the following Jupyter notebook cell by cell:

    ```text
    beeai_fw_tavily_redis/src/solutions/redis_vector_db.ipynb
    ```
