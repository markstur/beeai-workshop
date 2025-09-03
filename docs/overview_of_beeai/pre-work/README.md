---
title: BeeAI Workshop Pre-work
description: Preparation for the BeeAI Workshop
logo: images/ibm-blue-background.png
---

# Pre-work

## BeeAI

### Prerequisites to get started with BeeAI

#### Visual Studio Code (Recommended)

- You can use any IDE, but this workshop assumes you're using [VS Code](https://code.visualstudio.com/Download)
- If this is your first time using VS Code, make sure to install the Python extension from the extension marketplace

#### uv

- `uv` is the recommended Python package and environment manager for this workshop
- If you're unfamiliar with `uv`, check out [this uv primer](https://agentcommunicationprotocol.dev/introduction/uv-primer) for installation instructions

#### API Key

- [openrouter](https://openrouter.ai/) (free)
- [OpenAI](https://platform.openai.com/api-keys) (paid)
- [Groq](https://console.groq.com/keys) (free/limited)

## Workshop Specific Requirements

1. Get the workshop code:

    Option A: Clone with Git (Recommended):

    ```shell
    git clone https://github.com/IBM/beeai-workshop.git
    ```

    Option B: Download ZIP:
    If you're not comfortable with Git, [download the ZIP file](https://github.com/IBM/beeai-workshop/archive/refs/heads/main.zip) and extract it to your desired location.

2. Navigate to the workshop folder and open in VS Code:

    ```shell
    cd beeai-workshop/overview_of_beeai
    code .
    ```

    !!! important
        Make sure to open the specific `overview_of_beeai` folder in VS Code, not the entire `beeai-workshop` directory. This ensures proper project structure and dependencies.

    **Alternative:** You can also open VS Code first, then use "File > Open Folder" to navigate to and select the `beeai-workshop/overview_of_beeai` folder.

3. Create a .env file based on the env.template file at the overview_of_beeai directory level. Uncomment one of the provider configs and add your own api key.

    ```shell
    cp env.template .env
    ```

    !!! note
        For OpenAI you just need the API Key, for OpenRouter or Groq you need to uncomment all 3 environment variables but only need to modify the API Key.
