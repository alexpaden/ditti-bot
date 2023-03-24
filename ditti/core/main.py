import logging
import os
import time

import openai
from dotenv import load_dotenv
from farcaster import Warpcast
from google.cloud import translate

from ditti.commands.command_manager import Commands
from ditti.helpers.google_json_maker import run_google_maker
from supabase import Client, create_client

load_dotenv()


def configure_main_function():
    logging.basicConfig(
        filename="bot.log",
        level=logging.ERROR,
        format="%(asctime)s %(message)s",
    )
    run_google_maker()

    fcc = Warpcast(access_token=os.getenv("FARC_SECRET"))
    gtc = translate.TranslationServiceClient()
    openai.api_key = os.getenv("OPENAI_KEY")
    bot_username = os.getenv("USERNAME")
    supabase = create_supabase_client()

    return Commands(
        fcc=fcc,
        supabase=supabase,
        gtc=gtc,
        bot_username=bot_username,
    )


def create_supabase_client() -> Client:
    url = os.environ.get("SUPABASE_URL", "VALUE NOT SET")
    key = os.environ.get("SUPABASE_KEY", "VALUE NOT SET")
    return create_client(url, key)


def start_notification_stream(commands_instance: Commands):
    fcc = commands_instance.fcc
    bot_username = commands_instance.bot_username

    for notif in fcc.stream_notifications():
        if notif and notif.content.cast.text.startswith(bot_username):
            commands_instance.handle_command(notif)
        elif notif and notif.content.cast.parent_hash:
            try:
                parent = fcc.get_cast(notif.content.cast.parent_hash).cast
                if parent and parent.author.username == bot_username[1:]:
                    parent2 = fcc.get_cast(parent.parent_hash).cast
                    should_run = commands_instance.is_bot_command(parent2.hash)
                    if should_run:
                        commands_instance.handle_gpt_reply_command(notif)
            except Exception as e:
                logging.error(f"Error occurred in notification stream: {e}")


def main():
    logging.info("Configuring main function")
    try:
        commands_instance = configure_main_function()
    except Exception as e:
        logging.error(f"Error occurred configuring main function: {e}")
        return

    logging.info("Starting notification stream in main")
    while True:
        try:
            start_notification_stream(commands_instance)
        except Exception as e:
            logging.error(f"Error occurred in notification stream, main function: {e}")
            time.sleep(60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Error occurred __main__ function: {e}")
