---
title: Clean up
description: How to remove data and uninstall the vector DB
logo: images/ibm-blue-background.png
---

# Clean up

## Redis Vector DB

To remove the `internal_docs` data and destroy the vector search index,
use the RedisVL Python library. From the `beeai_fw_tavliy_redis` directory,
run:

```shell
uv run rvl index destroy --index internal_docs 
```

## Stop Redis

To stop Redis, run:

```shell
redis-cli SHUTDOWN
```

## Uninstall Redis

To completely remove Redis from your system, run:

```shell
brew uninstall redis
brew untap redis/redis
```
