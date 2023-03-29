import logging
from collections import OrderedDict

import openai
from farcaster import Warpcast
from farcaster.models import Parent

from ditti.commands.text2img import Text2Img


class LimitedSizeDict(OrderedDict):
    def __init__(self, *args, size_limit=None, **kwargs):
        self.size_limit = size_limit
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._check_size_limit()

    def _check_size_limit(self):
        if self.size_limit is not None:
            while len(self) > self.size_limit:
                self.popitem(last=False)


class Gpt:
    def __init__(self, fcc: Warpcast, bot_username: str, gpt_com: str):
        self.fcc = fcc
        self.t2i = Text2Img()
        self.BOT_USERNAME = bot_username
        self.GPT_COM = gpt_com
        self.cache = LimitedSizeDict(size_limit=100)

    # Will break if a parent is deleted, but that's a problem for another day
    def start_gpt(self, call_cast):
        messages, length_type = self.get_messages_from_gpt_call(call_cast)
        if length_type == 0:
            result = self.run_gpt_query(messages=messages)
        else:
            result = self.run_gpt_query_long(messages=messages)
        parent = Parent(fid=call_cast.author.fid, hash=call_cast.hash)
        return result, parent

    def start_gpt_reply(self, call_cast):
        messages = [{"role": "user", "content": call_cast.text}]
        counter = 0
        parent_hash = call_cast.parent_hash
        while parent_hash is not None:
            parent_cast = self.fcc.get_cast(parent_hash).cast
            if parent_cast.text.lower().startswith(
                f"{self.BOT_USERNAME} {self.GPT_COM}"
            ):
                og_messages, length_type = self.get_messages_from_gpt_call(parent_cast)
                messages[:0] = og_messages
                break
            elif parent_cast.author.username == self.BOT_USERNAME[1:]:
                text = parent_cast.text
                if text.startswith(
                    "https://i.imgur.com/"
                ):  # If the text is an imgur URL
                    text = self.cache.get(
                        text, text
                    )  # Replace it with the cached text if available
                messages.insert(0, {"role": "assistant", "content": text})
            else:
                if parent_cast.parent_hash is not None:
                    temp_cast = self.fcc.get_cast(parent_cast.parent_hash).cast
                    if temp_cast.author.username != self.BOT_USERNAME[1:]:
                        break
                    else:
                        messages.insert(
                            0, {"role": "user", "content": parent_cast.text}
                        )
            counter += 1
            if counter > 12:
                break
            parent_hash = parent_cast.parent_hash
        result = self.run_gpt_query(messages=messages)
        parent = Parent(fid=call_cast.author.fid, hash=call_cast.hash)
        return result, parent

    # When using ^ in gpt command this returns thread casts as text-only messages
    def get_messages_from_gpt_call(self, call_cast):
        call_text = call_cast.text
        command_text = ""
        length_type = 0
        parent_count = self.find_integer_after_caret(call_text)
        if parent_count is None:
            return "Something is wrong with your ^ command"
        if call_text.lower().startswith(f"{self.BOT_USERNAME} {self.GPT_COM}*"):
            length_type = 1
            command_text = self.get_long_form_command(call_text, parent_count)
        elif call_text.lower().startswith(f"{self.BOT_USERNAME} {self.GPT_COM}^"):
            command_text = self.get_short_form_parent_command(call_text, parent_count)
        elif call_text.lower().startswith(f"{self.BOT_USERNAME} {self.GPT_COM}"):
            command_text = f"{self.BOT_USERNAME} {self.GPT_COM}"
        else:
            logging.error("GPT command not recognized ", call_text)

        query_text = call_text.replace(command_text, "").strip()
        parent_texts: list[str] = []
        parent_hash = call_cast.parent_hash
        counter = 0

        while counter < parent_count and parent_hash is not None:
            res = self.fcc.get_cast(parent_hash)
            parent_texts.insert(0, res.cast.text.strip())
            parent_hash = res.cast.parent_hash
            counter += 1

        messages = self.simple_messages_string_builder(
            parent_texts=parent_texts, query_text=query_text, length_type=length_type
        )
        return messages, length_type

    # this finds how many parents to include in the query
    def find_integer_after_caret(self, s: str) -> int:
        caret_index = s.find("^")
        if caret_index == -1:
            return 0
        elif caret_index == len(s) - 1:
            return -1

        for i in range(caret_index + 1, len(s)):
            if s[i] == " ":
                break
            elif not s[i].isdigit():
                return -1

        integer_str = s[caret_index + 1 : i]
        if integer_str == "":
            return 1

        return int(integer_str)

    # This extracts the command text from the call text, long form gpt*
    def get_long_form_command(self, call_text, parent_count):
        command_text = f"{self.BOT_USERNAME} {self.GPT_COM}*"
        if parent_count == 0:
            if call_text.lower().startswith(f"{self.BOT_USERNAME} {self.GPT_COM}*^0"):
                pass
            else:
                return command_text
        if parent_count == 1:
            if call_text.lower().startswith(f"{self.BOT_USERNAME} {self.GPT_COM}*^1"):
                pass
            else:
                command_text += "^"
                return command_text

        command_text += f"^{parent_count}"
        return command_text

    # This extracts the command text from the call text, short form gpt
    def get_short_form_parent_command(self, call_text, parent_count):
        command_text = f"{self.BOT_USERNAME} {self.GPT_COM}"
        if parent_count == 1:
            if call_text.lower().startswith(f"{self.BOT_USERNAME} {self.GPT_COM}^1"):
                pass
            else:
                command_text += "^"
                return command_text
        command_text += f"^{parent_count}"
        return command_text

    # This builds the messages list using parent texts as system input
    def simple_messages_string_builder(self, parent_texts, query_text, length_type):
        messages = []
        messages = [{"role": "system", "content": text} for text in parent_texts]
        if length_type == 0:
            messages.insert(
                0,
                {
                    "role": "system",
                    "content": (
                        "Given the initial system context, "
                        "provide the shortest possible "
                        "response to the user, ideally under 300 characters."
                    ),
                },
            )
        else:
            messages.insert(
                0,
                {
                    "role": "system",
                    "content": (
                        "Given the initial system context, "
                        "provide a detailed response which "
                        "best answers the users prompt."
                    ),
                },
            )
        messages.append({"role": "user", "content": query_text})
        return messages

    # This is the actual call to chatgpt which returns the text summary
    # Text2Img is used if the summary is too long, it returns a url string
    def run_gpt_query(self, messages):
        # Send the API request and get the response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=100,
            temperature=0.65,
        )

        summary = response.choices[0].message.content
        if len(summary) > 320:
            img_url = self.t2i.convert(text=summary)
            self.cache[img_url] = summary  # Add the text message to the cache
            summary = img_url
        return summary

    # Long form gpt query
    def run_gpt_query_long(self, messages):
        # Send the API request and get the response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=750,
            temperature=0.65,
        )

        summary = response.choices[0].message.content
        if len(summary) > 320:
            img_url = self.t2i.convert(text=summary)
            self.cache[img_url] = summary  # Add the text message to the cache
            summary = img_url
        return summary
