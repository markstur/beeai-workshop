# Intro to BeeAI Framework

Temporary notes for stuff here. We'll use the mkdocs workshop for most instructions, but this is a quick and handy way to describe what is here.

## Overview

This is the source for the workshop.
Put links to docs here.

## Files

* ipynb is for running workshop in colab or Jupyter environments
* src/* is for running the agent locally (optionally with BeeAI platform)

## Setup

* Ollama/granite setup

* For the colab/jupyter setup:
    * Colab is easy
    * TODO: jupyter install notes

* BeeAI Platform install, setup, start

* Run the agent locally with BeeAI Platform (todo can make sure it also works w/o platform?)
    * Open a terminal to run the following commands
    * Install uv
    * Use uv to install the required version of python:
        * $ uv python install 3.13
    * uv sync
    * Set your IDE python interpreter to the one in .venv/bin/python (relative to this project dir)
    * Create a .env file from the template
        * `cp env.template .env`
    * Edit the .env file (defaults using local ollama should just work)
    * Run the agent:
       * `uv run src/agent.py` -- serves the agent self-registering with BeeAI platform
       * `uv run src/agent.py "quoted question string here"` -- runs the agent with a simple question, prints output, quits.

