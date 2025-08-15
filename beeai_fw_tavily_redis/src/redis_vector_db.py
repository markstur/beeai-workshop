#!/usr/bin/env python
# coding: utf-8

# Retrieval Augmented Generation (RAG) vector DB setup
# 
# This script uses:
# * Hugging Face model to generate embeddings for documents and queries
# * Redis vector store to cache and query the embeddings
# * Langchain library to interact with both of the above
# * Redis rvl command to demonstrate checking the DB status

# Use case
# 
# We are loading fictional company documents from `example_docs`. These may
# look like McDonalds documents to fit in with our live search Tavily example,
# but are not associated with McDonalds.

# Setup Python packages
# 
# > NOTE! Remember to navigate to the `beeai_fw_tavily_redis` folder of this repo and run `uv sync` before running this.
#
# Use `uv run src/redis_vector_db.py` to run this script with the proper environment and relative path to example_docs.

import os
import subprocess
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_redis import RedisConfig, RedisVectorStore
from langchain_text_splitters import MarkdownHeaderTextSplitter
import redis

# Python version check
assert (3, 11) <= sys.version_info < (3, 12), "Use Python 3.11 to run this script."


# Constants (or variables that you might want to change) are set here and used later.

EMBEDDINGS_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")  # Local Redis default


# Setup for the embeddings model
# 
# The embeddings model will be used to create embedding vectors from the documents and the queries.
# With HuggingFaceEmbeddings we can download a sentence-transformers model to run locally for our embeddings.

embeddings = HuggingFaceEmbeddings(model_name=EMBEDDINGS_MODEL_NAME)


# Setup the vector store
# 
# Redis is being used as the vector store.

# Test connection with Redis client
print(f"Connecting to Redis at: {REDIS_URL}")
redis_client = redis.from_url(REDIS_URL)
print(f"Connected = {redis_client.ping()}")


# Configure and init the vector store with our embeddings model
config = RedisConfig(
    index_name="internal_docs",
    redis_url=REDIS_URL,
    metadata_schema=[
        {"name": "document", "type": "tag"},
    ],
)

vector_store = RedisVectorStore(embeddings, config=config)


# Read and split the documents

splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[
        ("#", "Header_1"),
        ("##", "Header_2"),
        ("###", "Header_3"),
    ],
    strip_headers=True,
)

# Get the list of all files in the directory
path = 'example_docs'
files = os.listdir(path)

n_docs = 0
metadata = []
splits = []
for file in files:
    filename = os.path.join(path, file)
    if not os.path.isdir(filename) and filename.endswith(".md"):
        with open(filename) as f:
            file_contents = f.read()
            n_docs += 1
            for split in splitter.split_text(file_contents):
                splits.append(split.page_content)
                metadata.append({"document": filename})

print(f"{n_docs} documents split in to {len(splits)} chunks of text")


# Add the text and metadata to the vector store
_ids = vector_store.add_texts(splits, metadata)
# print(_ids)


def run_rvl_cli_command(command):
    """Run a shell command and print the output."""

    print(f"rvl command: {command}")
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()

    if error:
        print(f"ERROR! {error.decode('utf-8')}")
    else:
        print(f"Output: {output.decode('utf-8')}")

# Example usage of the `rvl` shell command to check on your redis DB.
# Assumes you're running Redis locally (use --host, --port, --password, --username, to change this)
run_rvl_cli_command('rvl version')
run_rvl_cli_command('rvl index listall --port 6379')
run_rvl_cli_command('rvl index info -i internal_docs --port 6379')
run_rvl_cli_command('rvl stats -i internal_docs --port 6379')


# Try a query
query = "What is our target market for the pilot?"
results = vector_store.similarity_search(query, k=2)

print("==========================")
print("Similarity Search Results:")
print("==========================")
print(f"Query: {query}")
print("Results:")
for doc in results:
    print(f"Metadata --> {doc.metadata}")
    print(f"Content -->")
    print(doc.page_content)
