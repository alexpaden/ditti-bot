# DITTI Farcaster Bot: Cast Line Interface

DITTI is a Farcaster bot that serves as a cast line interface (CLI), offering a variety of functions to improve user experience on the Farcaster platform. The bot is written in Python and utilizes the Farcaster-py library, OpenAI GPT, Google Cloud Translate, and Text2Img.

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/YjcrsJ?referralCode=T61Pcu)

## Features

- Python-based Farcaster bot
- Utilizes Farcaster-py, OpenAI GPT, Google Cloud Translate, and Text2Img
- Offers a range of commands for users to interact with

## Commands

To use DITTI, simply mention the bot with the desired command:

`@ditti <command>`

### Available Commands

- `@ditti thread`: Convert a thread of posts by the same author into an image.
- `@ditti gpt <question>`: Create an instance of ChatGPT, subsequent replies do not require the command.
- `@ditti gpt^`: Create an instance of ChatGPT using the specified number of thread replies for context (default is 1), e.g. `@ditti gpt^4`.
- `@ditti translate`: Translate a single cast or a thread of foreign language casts by a user into English.
- `@ditti hash`: Reply to a cast with this command to get the hash of that cast.
- `@ditti help`: Display all commands and information.
- `@ditti bookmark <title text> --tag <name>` Creates a bookmark of a cast using a Title description and optional category tag.
- `@ditti cut <title> --tag <name>` Cuts an image from cast and saves it for gallery use with option title and tag.

## How to Use

### Running Locally

<br>
**Requirements:** Python3, Poetry, Docker, Supabase CLI

1. In the project directory, create a local Supabase instance. This will create all the tables for you:
   `supabase start`

2. Rename `.env.example` to `.env` and configure your variables with the credentials generated from the previous step. Your `SUPABASE_URL` will be the API URL from the terminal output. The Studio URL is not necessary, but you may want to use it to view your database tables:
   `cp .env.example .env`

3. In the project directory, ensure poetry is using python 3.10 with `poetry env use 3.10`, then run `poetry install` and `poetry run python ditti/core/main.py`

<br>

### Deploying to Production (Railway)

1. Create an empty Supabase project and connect to the CLI:
   `supabase login`
   `supabase link --project-ref <project-id>`

2. Push your database schema:
   `supabase db push`

3. In railway, set environment variables using your .env values, and set the start command to:
   `python -m venv /opt/venv && . /opt/venv/bin/activate && poetry run python ditti/core/main.py`

<br>

## Running Tests

1. From the main folder, run `poetry run python -m pytest tests`.
2. For specific tests, run `poetry run python -m pytest tests/test_<module>.py`, for example `poetry run python -m pytest tests/test_gpt.py`.

<br>

## Contributing

Before submitting a pull request, please ensure your code follows the project's style guidelines by running `make codestyle` and passes lint checks with `make lint`.

### Codestyle

To enforce consistent code style, we use `pyupgrade`, `isort`, and `black`. You can run the following command to automatically format your code:
`make codestyle`
<br>

### Linting

We use `flake8` and `mypy` to perform linting and type checking. Run the following command to check your code for issues:
`make lint`
<br><br>
For more information and other useful tools, visit [ditti.xyz](https://ditti.xyz) or contact [@ditti](https://warpcast.com/ditti) on farcaster.
