import logging

import requests
from farcaster.models import Parent

# Generates a sharecast and searchcast link for a given post
"""
THIS CODE HAS BEEN DEPRECATED VIA NEW HASHES AND WARPCAST.COM

THE COMMAND IS NOT CURRENTLY ACTIVATED AND THIS CODE WILL NOT BE CALLED.

THE NEW SHARECASTER FORMAT IS https://sharecaster.xyz/hyper/0x2cfb65
"""


class Share:
    def __init__(self, fcc, commands):
        self.fcc = fcc
        self.commands = commands

    def link_maker(self, cast):
        try:
            self.fcc.get_cast(hash=cast.parent_hash)
            self.fcc.get_cast(hash=cast.hash)
        except Exception as e:
            logging.error(f"error get_cast in link_maker: {e}")

        share_link = self.sharecaster(
            parent_hash=cast.parent_hash, thread_hash=cast.thread_hash
        )
        search_link = self.searchcaster(
            parent_hash=cast.parent_hash, thread_hash=cast.thread_hash
        )
        link_cast = "Sharecast:\n{0}\n\nSearchcast:\n{1}".format(
            share_link, search_link
        )

        if link_cast == "Sharecast:\nError\n\nSearchcast:\nError":
            logging.error(Exception("Error generating sharecast and searchcast links"))

        parent = Parent(fid=cast.author.fid, hash=cast.hash)
        return link_cast, parent

    # Generates a sharecast link for a given post
    def sharecaster(self, parent_hash, thread_hash):
        cast_uri = f"farcaster://casts/{parent_hash or thread_hash}/{thread_hash}"

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }

        json_data = {
            "sharecast": cast_uri,
        }

        try:
            response = requests.post(
                "https://sharecaster.xyz/api/share",
                headers=headers,
                json=json_data,
            )
            sharecast = response.json()["data"]
            return f"https://sharecaster.xyz/{sharecast}"
        except Exception as e:
            logging.error(e)
            return "Error"

    # Generates a searchcaster link for a given post
    def searchcaster(self, parent_hash, thread_hash):
        try:
            response = requests.get(
                f"https://searchcaster.xyz/api/search?"
                f"merkleRoot={parent_hash or thread_hash}"
            )

            if response.json()["casts"] == []:
                raise Exception("No searchcast found")
        except Exception as e:
            logging.error(e)
            return "Error"
        return (
            f"https://searchcaster.xyz/search?merkleRoot={parent_hash or thread_hash}"
        )
