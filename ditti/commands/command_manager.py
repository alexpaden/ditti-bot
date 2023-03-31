import logging
import os

from farcaster.models import Parent

from ditti.commands.bookmark import Bookmark
from ditti.commands.cut import Cut
from ditti.commands.gpt import Gpt
from ditti.commands.hash import Hash
from ditti.commands.text2img import Text2Img
from ditti.commands.thread import Thread
from ditti.commands.translate import TranslatorBotCommand
from ditti.commands.whois import WhoIs

DEV_MODE = bool(os.getenv("DEV_MODE") == "True")
TRANSLATE_COM = "translate"
THREAD_COM = "thread"
GPT_COM = "gpt"
GPT_REPLY_COM = "gpt_reply"
HASH_COM = "hash"
HELP_COM = "help"
BOOKMARK_COM = "bookmark"
CUT_COM = "cut"
WHOIS_COM = "whois"


class Commands:
    def __init__(self, fcc, supabase, gtc, bot_username):
        self.fcc = fcc
        self.supabase = supabase
        self.bot_username = bot_username
        self.translate = TranslatorBotCommand(fcc, gtc)
        self.thread = Thread(fcc)
        self.gpt = Gpt(fcc, self.bot_username, GPT_COM)
        self.hash = Hash(fcc)
        self.bookmark = Bookmark(fcc, self.supabase, DEV_MODE)
        self.cut = Cut(fcc, self.supabase, DEV_MODE)
        self.text2img = Text2Img()
        self.whois = WhoIs(fcc)

    def handle_command(self, notif):
        command_mapping = {
            TRANSLATE_COM: self.handle_translate_command,
            THREAD_COM: self.handle_thread_command,
            GPT_COM: self.handle_gpt_command,
            HASH_COM: self.handle_hash_command,
            HELP_COM: self.handle_help_command,
            GPT_REPLY_COM: self.handle_gpt_reply_command,
            BOOKMARK_COM: self.handle_bookmark_command,
            CUT_COM: self.handle_cut_command,
            WHOIS_COM: self.handle_whois_command,
        }

        command_prefix = f"{self.bot_username} "
        for command, handler in command_mapping.items():
            if notif.content.cast.text.lower().startswith(command_prefix + command):
                handler(notif)
                break

    def handle_generic_command(self, notif, command, perform_func):
        if self.should_command_run(
            notif.content.cast.hash,
            command,
            notif.content.cast.author.username,
        ):
            try:
                perform_func(notif)
                self.mark_command_run(notif.content.cast.hash)
            except Exception as e:
                self.handle_error(e, f"Error while handling {command} command")

    def handle_translate_command(self, notif):
        self.handle_generic_command(
            notif, TRANSLATE_COM, self.perform_translate_command
        )

    def handle_thread_command(self, notif):
        self.handle_generic_command(notif, THREAD_COM, self.perform_thread_command)

    def handle_gpt_command(self, notif):
        self.handle_generic_command(notif, GPT_COM, self.perform_gpt_command)

    def handle_hash_command(self, notif):
        self.handle_generic_command(notif, HASH_COM, self.perform_hash_command)

    def handle_help_command(self, notif):
        self.handle_generic_command(notif, HELP_COM, self.perform_help_command)

    def handle_bookmark_command(self, notif):
        self.handle_generic_command(notif, BOOKMARK_COM, self.perform_bookmark_command)

    def handle_cut_command(self, notif):
        self.handle_generic_command(notif, CUT_COM, self.perform_cut_command)

    def handle_whois_command(self, notif):
        self.handle_generic_command(notif, WHOIS_COM, self.perform_whois_command)

    def handle_gpt_reply_command(self, notif):
        self.handle_generic_command(
            notif, GPT_REPLY_COM, self.perform_gpt_reply_command
        )

    def should_command_run(self, hash: str, type: str, username: str):
        try:
            result = (
                self.supabase.table("command").select("*").eq("hash", hash).execute()
            )
            if result.data == []:
                self.supabase.table("command").insert(
                    {"hash": hash, "type": type, "caller": username}
                ).execute()
                return True
            elif not result.data[0]["completed"]:
                return True
            else:
                return False
        except Exception as e:
            self.handle_error(e, "Error while checking if command should run: {hash}")
            return False

    def is_bot_command(self, hash: str):
        try:
            result = (
                self.supabase.table("command").select("type").eq("hash", hash).execute()
            )
            return bool(result.data) and result.data[0]["type"] in (
                "gpt",
                "gpt_reply",
            )
        except Exception as e:
            self.handle_error(e, "Error while checking if is bot command: {hash}")
            return False

    def mark_command_run(self, hash: str):
        try:
            if DEV_MODE:
                logging.info("Marking command as run (but dev mode)")
            else:
                self.supabase.table("command").update({"completed": True}).eq(
                    "hash", hash
                ).execute()
        except Exception as e:
            self.handle_error(e, "Error while marking command as run")

    def post_to_farcaster(self, text: str, parent: Parent):
        try:
            if DEV_MODE:
                logging.info("Posting to farcaster (but dev mode)")
            else:
                self.fcc.post_cast(text=text, parent=parent)
        except Exception as e:
            self.handle_error(e, "Error while posting to farcaster")

    def post_thread_to_farcaster(self, replies: list, parent: Parent):
        try:
            if DEV_MODE:
                logging.info("Posting to farcaster (but dev mode)")
            else:
                for reply in replies:
                    res = self.fcc.post_cast(text=reply, parent=parent)
                    parent = res.cast.parent_hash
        except Exception as e:
            self.handle_error(e, "Error while posting to farcaster")

    def perform_translate_command(self, notif):
        logging.info("Performing translate command")
        reply, parent = self.translate.start_translate(notif.content.cast)
        self.post_to_farcaster(text=reply, parent=parent)
        logging.info("Translate command completed")

    def perform_thread_command(self, notif):
        logging.info("Performing thread command")
        reply, parent = self.thread.start_thread(notif.content.cast)
        self.post_to_farcaster(text=reply, parent=parent)
        logging.info("Thread command completed")

    def perform_gpt_command(self, notif):
        logging.info("Performing gpt command")
        reply, parent = self.gpt.start_gpt(notif.content.cast)
        self.post_to_farcaster(text=reply, parent=parent)
        logging.info("Gpt command completed")

    def perform_gpt_reply_command(self, notif):
        logging.info("Performing gpt command")
        reply, parent = self.gpt.start_gpt_reply(notif.content.cast)
        self.post_to_farcaster(text=reply, parent=parent)
        logging.info("Gpt command completed")

    def perform_hash_command(self, notif):
        logging.info("Performing hash command")
        reply, parent = self.hash.start_hash(notif.content.cast)
        self.post_to_farcaster(text=reply, parent=parent)
        logging.info("Hash command completed")

    def perform_bookmark_command(self, notif):
        logging.info("Performing bookmark command")
        reply, parent = self.bookmark.start_bookmark(notif.content.cast)
        self.post_to_farcaster(text=reply, parent=parent)
        logging.info("Bookmark command completed")

    def perform_cut_command(self, notif):
        logging.info("Performing cut command")
        reply, parent = self.cut.start_cut(notif.content.cast)
        self.post_to_farcaster(text=reply, parent=parent)
        logging.info("Cut command completed")

    def perform_whois_command(self, notif):
        logging.info("Performing whois command")
        reply, parent = self.whois.start_whois(notif.content.cast)
        self.post_thread_to_farcaster(replies=reply, parent=parent)
        logging.info("Whois command completed")

    def perform_help_command(self, notif):
        logging.info("Performing help command")
        reply = (
            "Thanks for your interest in ditti bot! "
            "Tag @alexpaden for further assistance. "
            "https://i.imgur.com/J7sh9ip.png"
        )
        parent = Parent(fid=notif.content.cast.author.fid, hash=notif.content.cast.hash)
        self.post_to_farcaster(text=reply, parent=parent)
        logging.info("Help command completed")

    def handle_error(self, error, message):
        # Log the error and take any necessary action to handle it
        logging.error(f"{message}: {error}")
