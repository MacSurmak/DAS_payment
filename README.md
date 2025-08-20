[English](README.md) | [Русский](README.ru.md)

# DAS Payment Bot

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![Python Version](https://img.shields.io/badge/python-3.13-blue)

A Telegram bot for managing an electronic queue system at DAS MSU, built with a focus on clean architecture, scalability, and maintainability.

## Key features

This project adheres to a strict set of architectural principles to ensure high code quality and ease of maintenance:

*   **Declarative UI (`aiogram-dialog`):** The entire user interface is described declaratively, eliminating "callback hell" and complex FSM state management. UI logic is isolated from business logic.
*   **Separation of Concerns (SoC):** The project is strictly divided into layers:
    *   `dialogs/`: UI definition (windows, transitions).
    *   `services/`: Business logic (database operations, calculations), completely independent of Telegram.
    *   `handlers/`: Entry points for commands (`/start`) that launch dialogs.
    *   `database/`: Data structure definitions (SQLAlchemy models).
*   **Database as a Single Source of Truth:** All mutable configurations (schedules, faculty-to-window mappings, available dates) are stored in a PostgreSQL database, not hardcoded.
*   **Full Localization (i18n):** No user-facing strings are hardcoded. All text is managed through a central `lexicon/` module, making translation and text changes simple.
*   **ORM-first Approach:** All database interactions are performed through the SQLAlchemy ORM, ensuring type safety, security, and code readability.
*   **Fully Asynchronous:** The entire stack, from `aiogram` handlers to `asyncpg` database queries, is asynchronous for maximum performance.
*   **Production-Ready:** The bot is containerized with Docker, includes health check endpoints for Kubernetes, and has separate, automated notification and bot processes.

## Technology stack

*   **Framework:** Aiogram 3
*   **UI:** aiogram-dialog
*   **Database:** PostgreSQL
*   **ORM:** SQLAlchemy 2.0 (async)
*   **Cache/FSM Storage:** Redis
*   **Logging:** Loguru
*   **Notifications:** APScheduler
*   **Containerization:** Docker, Docker Compose

## Getting started

The easiest way to run the project locally is with Docker Compose.

### Prerequisites

*   Docker
*   Docker Compose

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/macsurmak/das-payment-bot.git
    cd das-payment-bot
    ```

2.  **Create the configuration file:**
    Copy the example environment file and fill in your details.
    ```bash
    cp .env.example .env
    ```
    You will need to provide your `BOT_TOKEN` and `ADMIN_IDS`. The default database and Redis settings are suitable for local development with Docker Compose.

3.  **Build and run the containers:**
    This command will build the bot's image and start the bot, scheduler, PostgreSQL, and Redis containers.
    ```bash
    docker-compose up --build
    ```
    The bot will now be running in polling mode.

## Configuration

All configuration is done via environment variables in the `.env` file:

*   `BOT_TOKEN`: Your Telegram bot token.
*   `ADMIN_IDS`: A comma-separated list of Telegram user IDs for administrators.
*   `ADMIN_PASSWORD`: The password used with the `/admin` command to gain admin rights.
*   `DB_*`: Connection settings for the PostgreSQL database.
*   `REDIS_*`: Connection settings for Redis.
*   `BASE_WEBHOOK_URL`, `WEBHOOK_PATH`: Optional settings for running the bot in webhook mode (recommended for production).

## Deployment

The project is designed for containerized deployment, for example, using Kubernetes.

1.  The `Dockerfile` creates a production-ready image.
2.  The GitHub Actions workflow in `.github/workflows/deploy.yml` automatically builds and pushes the image to Docker Hub on every commit to the `main` branch.
3.  The `k8s/` directory contains example manifests for deploying the bot and the scheduler as separate deployments in a Kubernetes cluster.