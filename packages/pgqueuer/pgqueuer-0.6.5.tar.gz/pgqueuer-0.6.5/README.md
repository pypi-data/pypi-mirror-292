### Readme
## 🚀 PgQueuer - Building Smoother Workflows One Queue at a Time 🚀
[![CI](https://github.com/janbjorge/PgQueuer/actions/workflows/ci.yml/badge.svg)](https://github.com/janbjorge/PgQueuer/actions/workflows/ci.yml?query=branch%3Amain)
[![pypi](https://img.shields.io/pypi/v/PgQueuer.svg)](https://pypi.python.org/pypi/PgQueuer)
[![downloads](https://static.pepy.tech/badge/PgQueuer/month)](https://pepy.tech/project/PgQueuer)
[![versions](https://img.shields.io/pypi/pyversions/PgQueuer.svg)](https://github.com/janbjorge/PgQueuer)

---

📚 **Documentation**: [Explore the Docs 📖](https://pgqueuer.readthedocs.io/en/latest/)

🔍 **Source Code**: [View on GitHub 💾](https://github.com/janbjorge/PgQueuer/)

💬 **Join the Discussion**: [Discord Community](https://discord.gg/C7YMBzcRMQ)

---

## PgQueuer

PgQueuer is a minimalist, high-performance job queue library for Python, leveraging the robustness of PostgreSQL. Designed for simplicity and efficiency, PgQueuer uses PostgreSQL's LISTEN/NOTIFY to manage job queues effortlessly.

### Features

- **Simple Integration**: Easy to integrate with existing Python applications using PostgreSQL.
- **Efficient Concurrency Handling**: Utilizes PostgreSQL's `FOR UPDATE SKIP LOCKED` for reliable and concurrent job processing.
- **Real-time Notifications**: Leverages `LISTEN` and `NOTIFY` for real-time updates on job status changes.

### Installation

To install PgQueuer, simply install with pip the following command:

```bash
pip install PgQueuer
```

### Example Usage

Here's how you can use PgQueuer in a typical scenario processing incoming data messages:

#### Write and run a consumer
Start a long-lived consumer that will begin processing jobs as soon as they are enqueued by another process. In this case we want to be a bit more carefull as we want gracefull shutdowns, `PgQueuer run` will setup signals to
ensure this.

```python
from __future__ import annotations

import asyncpg
from PgQueuer.db import AsyncpgDriver, dsn
from PgQueuer.models import Job
from PgQueuer.qm import QueueManager


async def main() -> QueueManager:
    connection = await asyncpg.connect(dsn())
    driver = AsyncpgDriver(connection)
    qm = QueueManager(driver)

    # Setup the 'fetch' entrypoint
    @qm.entrypoint("fetch")
    async def process_message(job: Job) -> None:
        print(f"Processed message: {job}")

    return qm
```

```bash
python3 -m PgQueuer run tools.consumer.main
```

#### Write and run a producer
Start a short-lived producer that will enqueue 10,000 jobs.
```python
from __future__ import annotations

import asyncio
import sys

import asyncpg
from PgQueuer.db import AsyncpgDriver
from PgQueuer.queries import Queries


async def main(N: int) -> None:
    connection = await asyncpg.connect()
    driver = AsyncpgDriver(connection)
    queries = Queries(driver)
    await queries.enqueue(
        ["fetch"] * N,
        [f"this is from me: {n}".encode() for n in range(1, N+1)],
        [0] * N,
    )


if __name__ == "__main__":
    print(sys.argv)
    N = 1_000 if len(sys.argv) == 1 else int(sys.argv[1])
    asyncio.run(main(N))
```

```bash
python3 tools/producer.py 10000
```
