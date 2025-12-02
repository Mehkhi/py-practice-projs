# Background Jobs with Redis

This project implements a background job queue using Redis and RQ (Redis Queue).

## Features

- **R1: Enqueue & Worker Process** - Jobs can be enqueued and processed by workers.
- **R2: Retries & Backoff** - Configurable retry policies with exponential backoff.
- **R3: Idempotency Keys** - Prevents duplicate job execution using unique keys.
- **R4: Status & DLQ** - Job status tracking and dead letter queue for failed jobs.
- **B1: Scheduled Jobs** - Schedule jobs to run at specific times.
- **B2: Priority Queues** - High, default, and low priority queues.
- **B3: Web Dashboard** - Simple web interface to view queue stats and manage jobs.

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Start Redis:
   ```
   redis-server
   ```

3. Run the worker:
   ```
   python worker.py
   ```

4. Run the web app:
   ```
   python app.py
   ```

5. Use CLI to enqueue jobs:
   ```
   python cli.py enqueue --type example --priority high
   ```

## Usage

- Web dashboard: http://localhost:5000
- Enqueue jobs via web form or CLI
- Schedule jobs for future execution
- View failed jobs in DLQ and retry them
